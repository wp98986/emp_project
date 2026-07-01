import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.system_mgt import ApiResponse
from api.system_mgt.permission_schemas import (
    SinglePermissionSchema,
    UpdatePermissionSchema,
    CreatePermissionSchema,
)
from db.system_mgt.permission_dao import PermissionDao
from utils.dependencis import get_db

# 创建分路由
router = APIRouter(prefix="/permission")
# 创建dao类的对象实例
_dao = PermissionDao()

log = logging.getLogger("emp")


@router.get(
    "/get_all",
    description="查询所有权限",
    response_model=ApiResponse[list[SinglePermissionSchema]],
)
def get(session: Session = Depends(get_db)):
    res = _dao.get_parent_permission(session)
    return {"code": 200, "msg": "获取权限列表", "data": res}


@router.get("/get_by_user", description="查询用户所有权限的菜单列表")
def get_menu_by_user(request: Request, session: Session = Depends(get_db)):
    res = _dao.get_menu_bypermission(session, request.state.username)
    return {"code": 200, "msg": "获取用户权限菜单", "data": res}


@router.get(
    "/get_by_id/{pk}/",
    description="根据主键查询权限信息",
    summary="单个查询",
    response_model=ApiResponse[SinglePermissionSchema],
)
def get_by_id(pk: int, session: Session = Depends(get_db)):
    _res = _dao.get_by_id(session, pk)
    return {"code": 200, "msg": "获取权限详情", "data": _res}


@router.post(
    "/create",
    description="新增权限，必须也要新增权限",
    response_model=ApiResponse[SinglePermissionSchema],
)
def create(obj_in: CreatePermissionSchema, session: Session = Depends(get_db)):
    res = _dao.create(session, obj_in)
    return {"code": 200, "msg": "新增权限成功", "data": res}


@router.post(
    "/update",
    response_model=ApiResponse[SinglePermissionSchema],
    description="根据主键，修改权限",
)
def patch(obj_in: UpdatePermissionSchema, session: Session = Depends(get_db)):
    res = _dao.update(session, obj_in)
    return {"code": 200, "msg": "修改权限成功", "data": res}


@router.delete(
    "/delete/{pk}",
    description="根据主键删除权限",
    response_model=ApiResponse[None],
)
def delete(pk: int, session: Session = Depends(get_db)):
    _dao.delete(session, pk)
    return {"code": 200, "msg": "删除权限成功！", "data": None}
