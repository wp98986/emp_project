from datetime import datetime
from pydantic import BaseModel, Field


class BaseDeptSchema(BaseModel):
    """普通部门的Schema"""

    name: str = Field(description="部门名字")
    city: str | None = Field(description="所在城市", default=None)
    pid: int | None = Field(description="所属父部门ID", default=None)
    leader_id: int | None = Field(description="负责人的ID", default=None)
    leader_name: str = Field(
        description="负责人的用户名",
    )

class DeptCreateSchema(BaseDeptSchema):
    """创建部门的Schema"""

    pass

class DeptUpdateSchema(BaseDeptSchema):
    """更新部门的Schema"""
    id: int = Field(description="部门编号")
    pass

class SingleDeptSchema(BaseDeptSchema):
    """查询响应单个部门的Schema"""

    id: int = Field(description="部门编号")
    children: list[SingleDeptSchema] | None = Field(
        description="所有的子部门列表", default=None
    )

    create_time: datetime = Field(description="角色的创建时间")
    update_time: datetime = Field(description="角色的修改时间")
