from fastapi import APIRouter

from .characters import router as characters_router
from .locations import router as locations_router

router = APIRouter()
router.include_router(characters_router)
router.include_router(locations_router)
