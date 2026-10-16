from fastapi import APIRouter
from sqlalchemy import select

from app.auth.deps import DB, CurrentUser
from app.models import City, ForecastVersion, Segment
from app.schemas import CityOut, ReferenceOut, SegmentOut, VersionOut

router = APIRouter(tags=["référentiel"])


@router.get("/reference", response_model=ReferenceOut)
def reference(_: CurrentUser, db: DB) -> ReferenceOut:
    return ReferenceOut(
        cities=[CityOut.model_validate(c) for c in db.scalars(select(City).order_by(City.code))],
        segments=[
            SegmentOut.model_validate(s) for s in db.scalars(select(Segment).order_by(Segment.id))
        ],
        versions=[
            VersionOut.model_validate(v)
            for v in db.scalars(select(ForecastVersion).order_by(ForecastVersion.id))
        ],
    )
