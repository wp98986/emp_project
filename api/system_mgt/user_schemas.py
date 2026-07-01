from datetime import datetime

from pydantic import BaseModel, Field

from api.schemas import InDBMixin
from api.system_mgt.dept_schemas import SingleDeptSchema


class UserSearchQuery(BaseModel):
    """用户列表搜索条件（全部可选，不传则不过滤）"""

    id: int | None = Field(None, description="用户ID")
    username: str | None = Field(None, description="用户名（精确匹配）")
    real_name: str | None = Field(None, description="真实姓名（模糊匹配）")
    dept_id: int | None = Field(None, description="部门ID")
    phone: str | None = Field(None, description="手机号")


class UserBaseSchema(BaseModel):
    """普通用户的Schema"""

    username: str = Field(..., description="用户名")
    phone: str | None = Field(description="用户手机号", default=None)
    email: str | None = Field(description="用户游戏", default=None)
    real_name: str | None = Field(description="用户真实姓名", default=None)
    icon: str | None = Field(description="用户头像", default=None)
    dept_id: int | None = Field(description="所属部门ID", default=None)


class GetUserList(BaseModel):
    """获取用户列表的时候的Schema"""

    username: str | None = Field(..., description="用户名")
    id: int | None = Field(..., description="用户ID编号")


class CreateUserSchema(UserBaseSchema):
    """创建用户的Schema"""

    roles: list[int] | None = Field(description="用户所选的角色ID列表", default=None)
    password: str | None = Field(
        description="用户密码",
        default="88888888",
    )


class UpdateUserSchema(UserBaseSchema):
    """更新用户的Schema"""

    id: int | None = Field(description="用户ID", default=None)
    roles: list[int] | None = Field(description="用户所选的角色ID列表", default=None)

    password: str | None = Field(
        description="用户密码",
        default=None,
    )


class UserSchema(UserBaseSchema, InDBMixin):
    """查询用户Schema"""

    # 可以自定义其他数据字段
    id: int = Field(..., description="用户ID")
    create_time: datetime | None = Field(description="创建时间", default=None)
    dept: SingleDeptSchema | None = Field(description="用户所在的部门", default=None)


class LoginUserRequestSchema(BaseModel):
    """登录用户的请求Schema"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="用户密码")


class LoginUserResponseSchema(UserBaseSchema, InDBMixin):
    """登录用户的响应Schema"""

    token: str = Field(..., description="登录token")
