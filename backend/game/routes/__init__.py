from fastapi import APIRouter

from .characters import router as characters_router
from .enemies import router as enemies_router
from .locations import router as locations_router
from .shop import router as shop_router

router = APIRouter()
router.include_router(characters_router)
router.include_router(enemies_router)
router.include_router(locations_router)
router.include_router(shop_router)
