from fastapi import APIRouter

from db import dbm

router = APIRouter(
    prefix="/api/audit/analytics",
    tags=["lpa_anyltics"],
    responses={404: {"description": "Not found"}},
)

