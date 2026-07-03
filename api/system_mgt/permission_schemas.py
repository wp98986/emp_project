from __future__ import annotations

from typing import Union, List
from pydantic import BaseModel, Field

from api.system_mgt.menu_schemas import SingleMenuSchemaID


class BasePermissionSchema(BaseModel):
    """普通权限的Schema"""

    name: str = Field(..., description="权限名字")
    method: str | None = Field(description="访问的方法", default=None)
    url: str | None = Field(description="权限的路由地址", default=None)
    is_interface: bool = Field(description="是否为请求的接口，不是菜单", default=False)
    pid: int | None = Field(description="所属父权限ID", default=None)
    menu_id: int | None = Field(description="所属菜单的ID", default=None)

class CreatePermissionSchema(BasePermissionSchema):
    """创建权限的Schema"""

    pass

class UpdatePermissionSchema(BasePermissionSchema):
    """修改权限的Schema"""
    id: int = Field(description="权限编号")
    pass

class CreateOrUpdatePermissionSchema(BasePermissionSchema):
    """创建或者修改权限的Schema"""

    pass


class SinglePermissionSchema(BasePermissionSchema):
    """查询响应单个权限的Schema"""

    id: int = Field(description="权限编号")
    children: list[SinglePermissionSchema] | None = Field(
        description="所有的子权限列表", default=None
    )
    menu: SingleMenuSchemaID | None = Field(
        description="权限所关联的菜单", default=None
    )
