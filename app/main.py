from fastapi import FastAPI, APIRouter
from routers.main_router import router as api_v1

router = APIRouter(
    prefix="/api",
)
router.include_router(api_v1)
app = FastAPI()
app.include_router(router)
