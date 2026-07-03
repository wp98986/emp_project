from typing import Generic, TypeVar

from pydantic import BaseModel, Field

# T = TypeVar("T")


# 定义响应模型
# class ApiResponse(BaseModel, Generic[T]):
class ApiResponse[T](BaseModel):
    code: int = Field(..., description="状态码")
    msg: str = Field(..., description="状态信息")
    data: T | None = None
