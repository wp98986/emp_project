import logging

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.system_mgt import ApiResponse
from api.system_mgt.dept_schemas import (
    SingleDeptSchema,
    DeptCreateSchema,
    DeptUpdateSchema,
    BaseDeptSchema,
)
from db.system_mgt.dept_dao import DeptDao
from utils.dependencis import get_db

# 创建分路由
router = APIRouter(prefix="/dept")
## 创建dao类的对象实例
_dao = DeptDao()

log = logging.getLogger("emp")


@router.get(
    "/get_all/",
    description="查询所有部门",
    response_model=ApiResponse[list[SingleDeptSchema]],
)
def get(session: Session = Depends(get_db)):
    dept_list = _dao.get_parent_dept(session)
    return {"code": 200, "msg": "获取部门列表", "data": dept_list}


#
# @router.get('/dept/{pk}/', description='根据主键查询角色信息', summary='单个查询', response_model=SingleRoleSchema)
# def get_by_id(pk: int, session: Session = Depends(get_db)):
#     return _dao.get_by_id(session, pk)
#


@router.post(
    "/create", description="创建部门", response_model=ApiResponse[BaseDeptSchema]
)
def create(obj_in: DeptCreateSchema, session: Session = Depends(get_db)):
    dept = _dao.create(session, obj_in)
    return {"code": 200, "msg": "创建部门成功", "data": dept}


@router.post(
    "/update", response_model=ApiResponse[BaseDeptSchema], description="修改部门"
)
def update(obj_in: DeptUpdateSchema, session: Session = Depends(get_db)):
    dept = _dao.update(session, obj_in)
    return {"code": 200, "msg": "修改部门成功", "data": dept}


# 删除部门
@router.delete("/delete/{pk}/", description="根据主键删除部门")
def delete(pk: int, session: Session = Depends(get_db)):
    # 部门删除，如果该部门下面有用户则不能删除，如果该部门下面有子部门也不能删除
    if _dao.count_user(session, [pk]) > 0:
        # return JSONResponse(
        #     {"detail": "不能删除，因为部门下面还有员工！"}, status_code=201
        # )
        return {"code": 400, "msg": "不能删除，因为部门下面还有员工！", "data": None}
    if _dao.count_child(session, pk) > 0:
        # return JSONResponse(
        #     {"detail": "不能删除，因为部门下面还有子部门！"}, status_code=201
        # )
        return {"code": 400, "msg": "不能删除，因为部门下面还有子部门！", "data": None}
    return {"code": 200, "msg": "删除部门成功", "data": None}
