from fastapi import APIRouter, FastAPI
from api.user_mgt.user_view import user_router


def route_v1():
    """路由v1"""
    root_router = APIRouter()
    root_router.include_router(user_router, tags=["用户模块"])
    # 其他模块的路由也可以在这里添加
    # root_router.include_router(其他模块的路由, prefix="/其他模块", tags=["其他模块"])
    return root_router


def init_routes(app: FastAPI):
    """初始化路由"""
    app.include_router(route_v1(), prefix="/api")
    # 其他路由也可以在这里添加
    # app.include_router(其他路由, prefix="/其他路由", tags=["其他路由"])
