from fastapi import APIRouter

router = APIRouter(tags=["santé"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
