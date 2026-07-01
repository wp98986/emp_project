from fastapi import APIRouter, FastAPI
from api.system_mgt import dept_views, permission_views, role_views, user_views, menu_views


def route_v1():
    """路由v1"""
    root_router = APIRouter()
    root_router.include_router(user_views.router, tags=["用户模块"])
    root_router.include_router(role_views.router, tags=["角色模块"])
    root_router.include_router(permission_views.router, tags=["权限模块"])
    root_router.include_router(dept_views.router, tags=["部门模块"])
    root_router.include_router(menu_views.router, tags=["菜单模块"])
    # 其他模块的路由也可以在这里添加
    # root_router.include_router(其他模块的路由, prefix="/其他模块", tags=["其他模块"])
    return root_router


def init_routes(app: FastAPI):
    """初始化路由"""
    app.include_router(route_v1(), prefix="/api")
    # 其他路由也可以在这里添加
    # app.include_router(其他路由, prefix="/其他路由", tags=["其他路由"])
