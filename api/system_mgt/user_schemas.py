from pydantic import BaseModel, Field

from api.schemas import InDBMixin


class UserBaseSchema(BaseModel):
    """普通用户的Schema"""

    username: str = Field(..., description="用户名")
    phone: str | None = Field(description="用户手机号", default=None)
    email: str | None = Field(description="用户游戏", default=None)
    real_name: str | None = Field(description="用户真实姓名", default=None)
    icon: str | None = Field(description="用户头像", default=None)
    # dept_id: int | None = Field(description="所属部门ID", default=None)


class CreateUserSchema(UserBaseSchema):
    """创建用户的Schema"""

    password: str = Field(..., description="用户密码")


class UpdateUserSchema(UserBaseSchema):
    """更新用户的Schema"""

    id: int | None = Field(description="用户ID", default=None)
    password: str | None = Field(
        description="用户密码",
        default=None,
    )


class UserSchema(UserBaseSchema, InDBMixin):
    """查询用户Schema"""

    # 可以自定义其他数据字段
    id: int = Field(..., description="用户ID")
    # password: str | None = Field(description="用户密码", default=None)


class LoginUserRequestSchema(BaseModel):
    """登录用户的请求Schema"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="用户密码")


class LoginUserResponseSchema(UserBaseSchema, InDBMixin):
    """登录用户的响应Schema"""

    token: str = Field(..., description="登录token")
