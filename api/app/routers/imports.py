import hashlib
from datetime import UTC, datetime
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, defer

from app.auth.deps import DB, CurrentUser, require_roles
from app.imports.parsing import FileFormatError, ParseResult, parse_file, read_table
from app.imports.service import apply_batch, load_context
from app.imports.spec import TEMPLATES
from app.models import ActualValue, ImportBatch, ImportKind, ImportStatus, Role, User
from app.schemas import BatchOut, ConfirmIn, IssueOut, SourceStatus

router = APIRouter(prefix="/imports", tags=["imports"])

Uploader = Annotated[User, Depends(require_roles(Role.controller, Role.admin))]
MAX_BYTES = 10 * 1024 * 1024
LIGHT = (defer(ImportBatch.content), defer(ImportBatch.records))


def batch_out(batch: ImportBatch) -> BatchOut:
    return BatchOut(
        id=batch.id,
        kind=batch.kind,
        status=batch.status,
        filename=batch.filename,
        uploaded_at=batch.uploaded_at,
        uploaded_by=batch.uploaded_by.full_name if batch.uploaded_by else "—",
        rows_read=batch.rows_read,
        rows_kept=batch.rows_kept,
        rows_ignored=batch.rows_ignored,
        months=batch.months or [],
        errors=[IssueOut(**i) for i in batch.errors or []],
        warnings=[IssueOut(**i) for i in batch.warnings or []],
        warnings_confirmed=batch.warnings_confirmed,
        decided_at=batch.decided_at,
    )


def attachment(filename: str) -> dict[str, str]:
    return {"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"}


def get_pending(db: Session, batch_id: int) -> ImportBatch:
    batch = db.get(ImportBatch, batch_id)
    if batch is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dépôt introuvable")
    if batch.status != ImportStatus.pending:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ce dépôt n'est plus en attente")
    return batch


@router.get("/templates/{kind}")
def template(kind: ImportKind, _: CurrentUser) -> Response:
    filename, headers = TEMPLATES[kind.value]
    content = ("\ufeff" + ";".join(headers) + "\r\n").encode("utf-8")
    return Response(content, media_type="text/csv; charset=utf-8", headers=attachment(filename))


@router.get("/status", response_model=dict[str, SourceStatus])
def sources_status(_: CurrentUser, db: DB) -> dict[str, SourceStatus]:
    out: dict[str, SourceStatus] = {}
    for kind in ImportKind:
        last = db.scalar(
            select(ImportBatch)
            .options(*LIGHT)
            .where(ImportBatch.kind == kind, ImportBatch.status == ImportStatus.accepted)
            .order_by(ImportBatch.id.desc())
            .limit(1)
        )
        out[kind.value] = SourceStatus(
            last_import_at=last.decided_at if last else None,
            last_import_by=last.uploaded_by.full_name if last else None,
            last_month=db.scalar(
                select(func.max(ActualValue.month)).where(ActualValue.source == kind)
            ),
        )
    return out


@router.get("", response_model=list[BatchOut])
def list_batches(_: Uploader, db: DB) -> list[BatchOut]:
    batches = db.scalars(
        select(ImportBatch).options(*LIGHT).order_by(ImportBatch.id.desc()).limit(50)
    )
    return [batch_out(b) for b in batches]


@router.post("/{kind}/preview", response_model=BatchOut)
def preview(
    kind: ImportKind,
    user: Uploader,
    db: DB,
    file: Annotated[UploadFile, File()],
    year: Annotated[int | None, Form()] = None,
) -> BatchOut:
    """Vérifie le fichier sans rien enregistrer dans les réalisés."""
    content = file.file.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise HTTPException(413, "Fichier trop volumineux (10 Mo maximum)")
    if year is not None and not 2000 <= year <= 2100:
        raise HTTPException(422, "Année invalide")
    filename = (file.filename or "fichier")[:255]

    result = ParseResult(kind=kind.value)
    if not content:
        result.error("Le fichier est vide.")
    else:
        try:
            rows = read_table(content, filename)
        except FileFormatError as exc:
            result.error(str(exc))
        else:
            existing, previous = load_context(db, kind)
            result = parse_file(
                kind.value, rows, year=year, existing_months=existing, previous=previous
            )

    batch = ImportBatch(
        kind=kind,
        status=ImportStatus.pending if result.ok else ImportStatus.rejected,
        filename=filename,
        file_size=len(content),
        file_sha256=hashlib.sha256(content).hexdigest(),
        content=content,
        uploaded_by_id=user.id,
        year=year,
        rows_read=result.rows_read,
        rows_kept=result.rows_kept,
        rows_ignored=result.rows_ignored,
        months=[m.isoformat() for m in result.months],
        errors=[i.as_dict() for i in result.errors],
        warnings=[i.as_dict() for i in result.warnings],
        records=[r.as_dict() for r in result.records] if result.ok else None,
        decided_at=None if result.ok else datetime.now(UTC),
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch_out(batch)


@router.post("/{batch_id}/confirm", response_model=BatchOut)
def confirm(batch_id: int, body: ConfirmIn, _: Uploader, db: DB) -> BatchOut:
    batch = get_pending(db, batch_id)
    if batch.warnings and not body.confirm_warnings:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Confirmez les avertissements avant d'importer"
        )
    apply_batch(db, batch)
    batch.status = ImportStatus.accepted
    batch.warnings_confirmed = bool(batch.warnings)
    batch.records = None
    batch.decided_at = datetime.now(UTC)
    db.commit()
    db.refresh(batch)
    return batch_out(batch)


@router.post("/{batch_id}/cancel", response_model=BatchOut)
def cancel(batch_id: int, _: Uploader, db: DB) -> BatchOut:
    batch = get_pending(db, batch_id)
    batch.status = ImportStatus.cancelled
    batch.records = None
    batch.decided_at = datetime.now(UTC)
    db.commit()
    db.refresh(batch)
    return batch_out(batch)


@router.get("/{batch_id}/file")
def original_file(batch_id: int, _: Uploader, db: DB) -> Response:
    batch = db.get(ImportBatch, batch_id)
    if batch is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dépôt introuvable")
    return Response(
        batch.content, media_type="application/octet-stream", headers=attachment(batch.filename)
    )
