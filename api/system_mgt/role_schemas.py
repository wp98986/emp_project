from datetime import datetime
from typing import Union, List
from pydantic import BaseModel, Field


class BaseRoleSchema(BaseModel):
    """普通角色的Schema"""

    name: str = Field(description="角色名字")
    remark: str | None = Field(description="角色备注", default=None)


class RoleCreateSchema(BaseRoleSchema):
    """创建角色的Schema"""

    pass


class RoleUpdateSchema(BaseRoleSchema):
    """修改角色的Schema"""

    id: int = Field(description="角色编号")



class PermissionsOfRole(BaseModel):
    """语言角色的权限ID列表"""

    checkedKeys: list[int] | None = Field(
        description="已勾选的权限ID列表", default=None
    )
    halfKeys: list[int] | None = Field(description="半勾选的权限ID列表", default=None)


class SetPermissionToRole(BaseModel):
    """给角色授权的请求模型类"""

    id: int = Field(description="角色编号")
    permissions: PermissionsOfRole | None = Field(
        description="权限ID列表", default=None
    )


class SingleRoleSchema(BaseRoleSchema):
    """查询角色列表的Schema"""

    id: int = Field(description="角色编号")
    create_time: datetime = Field(description="角色的创建时间")
    permissions: PermissionsOfRole = Field(description="权限ID列表")
