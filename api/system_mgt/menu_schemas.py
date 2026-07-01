from pydantic import BaseModel, Field


class BaseMenuSchema(BaseModel):
    """普通菜单的Schema"""

    name: str = Field(..., description="菜单名字")
    url: str | None = Field(description="菜单的路由地址", default=None)

    number: int | None = Field(description="排序数字", default=None)
    is_parent: bool = Field(description="是否为顶级菜单", default=False)
    pid: int | None = Field(description="所属父菜单ID", default=None)


class MenuCreateSchema(BaseMenuSchema):
    """创建菜单的Schema"""

    pass


class MenuUpdateSchema(BaseMenuSchema):
    """修改菜单的Schema"""

    id: int = Field(..., description="菜单id")
    pass


class MenuDeleteSchema(BaseModel):
    """删除多个菜单的Schema"""

    id: int | None = Field(None, description="菜单编号")
    ids: list[int] | None = Field(description="菜单编号列表", default=None)


class SingleMenuSchema(BaseMenuSchema):
    """查询响应单个菜单的Schema"""

    id: int = Field(..., description="菜单编号")
    ids: list[int] | None = Field(description="菜单编号列表", default=None)
    children: list[SingleMenuSchema] = Field(
        description="所有的子菜单列表", default_factory=list
    )


class SingleMenuSchemaID(BaseMenuSchema):
    """查询响应单个菜单的Schema"""

    id: int = Field(..., description="菜单编号")
