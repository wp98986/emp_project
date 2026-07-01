import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.system_mgt import ApiResponse
from api.system_mgt.menu_schemas import (
    MenuCreateSchema,
    MenuDeleteSchema,
    MenuUpdateSchema,
    SingleMenuSchema,
)
from db.system_mgt.menu_dao import MenuDao
from utils.dependencis import get_db

# 创建分路由
router = APIRouter(prefix="/menu")
# 创建dao类的对象实例
_dao = MenuDao()

log = logging.getLogger("emp")


@router.get(
    "/get_all/",
    description="查询所有菜单",
    response_model=ApiResponse[list[SingleMenuSchema]],
)
def get(session: Session = Depends(get_db)):
    res = _dao.get_parent_menu(session)
    return {"code": 200, "msg": "获取菜单列表", "data": res}


@router.get(
    "/get_by_id/{pk}/",
    description="根据主键查询菜单详情",
    summary="单个查询",
    response_model=ApiResponse[SingleMenuSchema],
)
def get_by_id(pk: int, session: Session = Depends(get_db)):
    res = _dao.get_by_id(session, pk)
    return {"code": 200, "msg": "获取菜单详情", "data": res}


@router.post(
    "/create/",
    description="新增菜单，必须也要新增权限",
    response_model=ApiResponse[SingleMenuSchema],
)
def create(obj_in: MenuCreateSchema, session: Session = Depends(get_db)):
    res = _dao.create(session, obj_in)
    return {"code": 200, "msg": "新增菜单成功", "data": res}


@router.post(
    "/update",
    response_model=ApiResponse[SingleMenuSchema],
    description="修改菜单",
)
def update(obj_in: MenuUpdateSchema, session: Session = Depends(get_db)):
    res = _dao.update(session, obj_in)
    return {"code": 200, "msg": "修改菜单成功", "data": res}


@router.post(
    "/delete",
    description="根据主键批量删除多个菜单",
    response_model=ApiResponse[None | int | list[int]],
)
# def delete(ids: list[int], session: Session = Depends(get_db)):
def delete(obj_in: MenuDeleteSchema, session: Session = Depends(get_db)):
    print("删除菜单", obj_in)
    ids = obj_in.ids or []
    # 菜单的批量删除，如果该菜单下面还有二级菜单，则不能删除。
    if _dao.count_children(session, ids) > 0:
        # return JSONResponse(
        #     {"detail": "不能删除，因为菜单下面还有子菜单！"}, status_code=201
        # )
        return {"code": 400, "msg": "不能删除，因为菜单下面还有子菜单！", "data": ids}
    _dao.deletes(session, ids)
    # return JSONResponse({"detail": "批量删除成功！"}, status_code=200)
    return {"code": 200, "msg": "批量删除成功！", "data": None}
