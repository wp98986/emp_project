# from typing import TypeVar

from pydantic import BaseModel, Field

# from db import DBModelBase

# 定义泛型   旧的写法，在py3.12+中可以使用新的语法定义泛型
# ModelType = TypeVar("ModelType", bound=DBModelBase)  # 数据模型类型
# CreateSchema = TypeVar("CreateSchema", bound=BaseModel)  # 创建Schema类型
# UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)  # 更新Schema类型


class InDBMixin(BaseModel):
    """数据库模型基类,所有响应的模型父类"""

    id: int = Field(..., description="主键ID")

    class config:
        from_attributes = True  # 设置后，能把ORM模型的属性映射到Pydantic模型的字段
