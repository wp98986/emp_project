import logging
from typing import List

from fastapi import APIRouter, Depends, Query

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.system_mgt import ApiResponse
from api.system_mgt.role_schemas import (
    RoleCreateSchema,
    SingleRoleSchema,
    RoleUpdateSchema,
    SetPermissionToRole,
)
from db.system_mgt.role_dao import RoleDao
from utils.dependencis import get_db

# 创建分路由
router = APIRouter()
# 创建dao类的对象实例
_dao = RoleDao()

log = logging.getLogger("emp")


def get_permission(session, rid):
    """得到字典，保护角色的所有权限ID"""
    return {
        "checkedKeys": _dao.get_checked_keys(session, rid),
        "halfKeys": _dao.get_half_keys(session, rid),
    }


@router.get(
    "/roles/",
    description="分页查询所有的角色信息",
    summary="分页查询",
    response_model=ApiResponse[list[dict]],
)
def get(
    id: int = Query(default=None, description="角色ID"),
    name: str = Query(default=None, description="角色名"),
    session: Session = Depends(get_db),
):
    result = _dao.search_roles(session, id, name)  # 只有角色信息,没有权限的列表
    lst = []
    if result:
        for r in result:
            lst.append(
                {
                    "id": r.id,
                    "name": r.name,
                    "remark": r.remark,
                    "create_time": r.create_time,
                    "permissions": get_permission(
                        session, r.id
                    ),  # 得到该角色的所有权限ID
                }
            )
    return {"code": 200, "msg": "获取角色列表", "data": lst}


# @router.get('/roles/{pk}/', description='根据主键查询角色信息', summary='单个查询', response_model=SingleRoleSchema)
# def get_by_id(pk: int, session: Session = Depends(get_db)):
#     return _dao.get_by_id(session, pk)


@router.post(
    "/roles/", description="创建角色", response_model=ApiResponse[SingleRoleSchema]
)
def create(obj_in: RoleCreateSchema, session: Session = Depends(get_db)):
    res = _dao.create(session, obj_in)
    return {"code": 200, "msg": "新增角色成功", "data": res}


@router.post(
    "/roles/setPermission/", description="给角色授权", response_model=ApiResponse[str]
)
def set_permission(obj_in: SetPermissionToRole, session: Session = Depends(get_db)):
    _dao.set_permission(session, obj_in)
    return {"code": 200, "msg": "修改权限成功", "data": "修改权限成功"}


@router.patch(
    "/roles/update/",
    response_model=ApiResponse[SingleRoleSchema],
    description="根据主键，修改角色",
)
def patch(obj_in: RoleUpdateSchema, session: Session = Depends(get_db)):
    res = _dao.update(session, obj_in)
    return {"code": 200, "msg": "修改角色成功", "data": res}


@router.delete(
    "/roles/{pk}/",
    description="根据主键批量删除角色",
    response_model=ApiResponse[str | None],
)
def delete(pk: int, session: Session = Depends(get_db)):
    # 角色的批量删除，如果该角色已经分配给用户了，则不能删除。
    if _dao.count_user(session, [pk]) > 0:
        # return JSONResponse(
        #     {"detail": "不能删除，因为角色下面还有员工！"}, status_code=201
        # )
        return {"code": 201, "msg": "不能删除，因为角色下面还有员工！", "data": None}
    _dao.delete(session, pk)
    return {"code": 200, "msg": "删除角色成功！", "data": None}
