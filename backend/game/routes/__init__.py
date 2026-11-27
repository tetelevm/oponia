from fastapi import APIRouter

from .locations import router as locations_router

router = APIRouter()
router.include_router(locations_router)
