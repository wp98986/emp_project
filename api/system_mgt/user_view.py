# 创建字路由
from typing import Generic, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.system_mgt.user_schemas import (
    CreateUserSchema,
    LoginUserRequestSchema,
    LoginUserResponseSchema,
    UpdateUserSchema,
    UserBaseSchema,
    UserSchema,
)
from db.system_mgt.user_models import UserModel
from utils.dependencis import get_db
from db.system_mgt.user_dao import UserDao
from utils.jwt_utils import create_access_token
from utils.password_hash import get_password_hash, verify_password

T = TypeVar("T")


# 定义响应模型
class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(..., description="状态码")
    msg: str = Field(..., description="状态信息")
    data: T | None = None


user_router = APIRouter(prefix="/user")

# 创建dao类
_dao = UserDao()

import logging

log = logging.getLogger("user_view")


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
    request: Request,
    pk: int = Path(..., description="用户ID"),
    session: Session = Depends(get_db),
):
    """根据用户ID查询用户信息"""
    print("request.state.user:", request.state.user)
    user = _dao.get_by_id(session, pk)
    # if user is None:
    #     return {"code": 404, "msg": "用户不存在", "data": None}
    return {"code": 200, "msg": "查询用户成功", "data": user}


# 注册用户
@user_router.post(
    "/register",
    summary="注册用户",
    description="注册用户信息",
    response_model=ApiResponse[UserSchema],
)
def create_user(
    user: CreateUserSchema,
    session: Session = Depends(get_db),
):
    """注册用户"""
    # 用户名是否存在
    result = _dao.get_by_username(session, user.username)
    if result is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )
    # 密码加密
    user.password = get_password_hash(user.password)
    obj = _dao.create(session, user)
    return {"code": 200, "msg": "创建用户成功", "data": obj}


# 用户登录
@user_router.post(
    "/login",
    summary="用户登录",
    description="用户登录",
    response_model=ApiResponse[LoginUserResponseSchema],
)
def login_user(
    user: LoginUserRequestSchema,
    session: Session = Depends(get_db),
):
    """用户登录"""
    # 用户名是否存在
    result = _dao.get_by_username(session, user.username)
    log.info(result)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名不存在"
        )
    # 密码是否正确
    if not verify_password(user.password, result.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密码错误")
    user_dict = {
        "id": result.id,
        "username": result.username,
        "phone": result.phone,
        "email": result.email,
        "real_name": result.real_name,
        "icon": result.icon,
    }
    # 生成访问令牌
    token = create_access_token(
        data={
            "sub": str(result.id),
            "username": result.username,
        }
    )

    return {"code": 200, "msg": "登录成功", "data": {**user_dict, "token": token}}


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


# 这个接口是给接口文档用的，测试接口时需要登录获取token，登录口测试接口时自动携带token
@user_router.post("/auth/", description="接口文档中认证表单提交")
def auth(
    form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)
):
    """
    接口文档中，用于接受认证表单提交的视图函数
    :param form_data: 表单数据
    :param session:
    :return:
    """
    user = _dao.get_by_username(session, form_data.username)
    log.info(user)
    if not user:  # 用户不存在
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"用户名{form_data.username}，在数据库表中不存在!",
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"登录密码错误"
        )
    # 代码执行到此，则登录成功
    # 生成访问令牌
    token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
        }
    )
    return {"access_token": token, "token_type": "bearer"}  # 创建token
