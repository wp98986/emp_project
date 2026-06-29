# 创建字路由
from typing import Generic, TypeVar

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.user_mgt.user_schemas import CreateUserSchema, UpdateUserSchema, UserBaseSchema, UserSchema
from utils.dependencis import get_db
from db.user_mgt.user_dao import UserDao

T = TypeVar("T")


# 定义响应模型
class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(..., description="状态码")
    msg: str = Field(..., description="状态信息")
    data: T | None = None


user_router = APIRouter(prefix="/user")

# 创建dao类
_dao = UserDao()


# 获取所有用户
@user_router.get(
    "/get_all",
    summary="获取所有用户",
    description="获取所有用户信息",
    response_model=ApiResponse[list[UserSchema]],
)
def get_user_list(session: Session = Depends(get_db)):
    """获取用户列表"""
    user_list = _dao.get_all(session)
    return {"code": 200, "msg": "获取用户列表", "data": user_list}


# 分页查询用户列表
@user_router.get(
    "/get_by_page",
    summary="分页查询用户列表",
    description="分页查询用户列表",
)
def get_user_list_by_page(
    session: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 10,
):
    """分页查询用户列表"""
    user_list = _dao.get_by_page(session, page, page_size)
    total = _dao.count(session)
    # return {"message": "分页查询用户列表", "data": user_list}
    return {
        "code": 200,
        "msg": "分页查询员工成功",
        "data": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "models": user_list,
        },
    }


# 根据ID查询用户
@user_router.get(
    "/get_by_id/{pk}",
    summary="根据ID查询用户",
    description="根据用户ID查询用户信息",
    response_model=ApiResponse[UserSchema],
)
def get_user_by_id(
    pk: int = Path(..., description="用户ID"),
    session: Session = Depends(get_db),
):
    """根据用户ID查询用户信息"""
    user = _dao.get_by_id(session, pk)
    if user is None:
        return {"code": 404, "msg": "用户不存在", "data": None}
    return {"code": 200, "msg": "查询用户成功", "data": user}


# 创建用户
@user_router.post(
    "/create",
    summary="创建用户",
    description="创建用户信息",
    response_model=ApiResponse[UserBaseSchema],
)
def create_user(
    user: CreateUserSchema,
    session: Session = Depends(get_db),
):
    """创建用户"""
    obj = _dao.create(session, user)
    return {"code": 200, "msg": "创建用户成功", "data": obj}


# 更新用户
@user_router.put(
    "/update",
    summary="更新用户",
    description="更新用户信息",
    response_model=ApiResponse[UserBaseSchema],
)
def update_user(
    user: UpdateUserSchema,
    session: Session = Depends(get_db),
):
    """更新用户"""
    obj = _dao.update(session, user)
    return {"code": 200, "msg": "更新用户成功", "data": obj}


# 删除用户
@user_router.delete(
    "/delete/{pk}",
    summary="删除用户",
    description="根据用户ID删除用户信息",
    response_model=ApiResponse[None],
)
def delete_user(
    pk: int = Path(..., description="用户ID"),
    session: Session = Depends(get_db),
):
    """删除用户"""
    _dao.delete(session, pk)
    return {"code": 200, "msg": "删除用户成功", "data": None}
