# 创建字路由
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from fastapi_pagination import Page

from api.system_mgt import ApiResponse
from api.system_mgt.user_schemas import (
    CreateUserSchema,
    LoginUserRequestSchema,
    LoginUserResponseSchema,
    UpdateUserSchema,
    UserBaseSchema,
    UserSchema,
    UserSearchQuery,
)

from utils.dependencis import get_db
from db.system_mgt.user_dao import UserDao
from service.user_service import UserService
from utils.password_hash import get_password_hash

router = APIRouter(prefix="/user")

# 创建 dao 及服务实例
_dao = UserDao()
user_service = UserService(_dao)

import logging

log = logging.getLogger("user_view")


# ====================================================================== #
#  以下路由与原始版本完全一致（URL / 参数名 / 响应格式均不变），
#  仅内部实现从直接调 DAO 改为调 UserService。
# ====================================================================== #


# 获取所有用户
@router.get(
    "/get_all",
    summary="获取所有用户",
    description="获取所有用户信息",
    response_model=ApiResponse[list[UserSchema]],
)
def get_user_list(session: Session = Depends(get_db)):
    """获取用户列表"""
    user_list = user_service.get_all(session)
    return {"code": 200, "msg": "获取用户列表", "data": user_list}


# 分页查询用户列表
@router.get(
    "/get_by_page",
    summary="分页查询用户列表",
    description="分页查询用户列表",
    response_model=Page[UserSchema]
) # fastapi-pagination 装饰器：自动将 Query 对象转为分页响应
def get_user_list_by_page(
    session: Session = Depends(get_db),
    id: int | None = Query(default=None, description="用户ID"),
    username: str | None = Query(default=None, description="用户名"),
    real_name: str | None = Query(default=None, description="真实姓名"),
    query_dept_id: int | None = Query(default=None, description="部门ID"),
    query_phone: str | None = Query(default=None, description="手机号"),
):
    """分页查询用户列表"""
    query_obj = user_service.search(
        session,
        id=id,
        username=username,
        real_name=real_name,
        dept_id=query_dept_id,
        phone=query_phone,
    )
    result = paginate(query_obj)
    return result


# 根据ID查询用户
@router.get(
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
    # print("request.state.user:", request.state.user)
    user = user_service.get_by_id(session, pk)
    return {"code": 200, "msg": "查询用户成功", "data": user}


# 注册用户
@router.post(
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
    try:
        obj = user_service.register(
            session,
            username=user.username,
            password=user.password,
            phone=user.phone,
            email=user.email,
            real_name=user.real_name,
            icon=user.icon,
            dept_id=user.dept_id,
            roles=user.roles or [],
        )
        return {"code": 200, "msg": "创建用户成功", "data": obj}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


# 用户登录
@router.post(
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
    try:
        result = user_service.login(session, user.username, user.password)
        return {"code": 200, "msg": "登录成功", "data": result}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


# 更新用户
@router.post(
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
    print("user开始更新:", user)
    update_kwargs = user.model_dump(exclude_unset=True, exclude={"id", "password"})
    if user.password:
        update_kwargs["password"] = get_password_hash(user.password)
    obj = user_service.update(session, pk=user.id, **update_kwargs)
    return {"code": 200, "msg": "更新用户成功", "data": obj}


# 删除用户
@router.post(
    "/delete",
    summary="删除用户",
    description="根据用户ID删除用户信息",
    response_model=ApiResponse[None],
)
def delete_user(
    obj_in: UserSchema,
    session: Session = Depends(get_db),
):
    """删除用户"""
    user_service.delete(session, obj_in.id)
    return {"code": 200, "msg": "删除用户成功", "data": None}


# 接口文档认证表单
@router.post("/auth/", description="接口文档中认证表单提交")
def auth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db),
):
    """
    接口文档中，用于接受认证表单提交的视图函数
    """
    try:
        result = user_service.login(session, form_data.username, form_data.password)
        return {"access_token": result["token"], "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        )
