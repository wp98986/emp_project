from typing import Generic, Type
from fastapi import HTTPException
from sqlalchemy import CursorResult, delete, func, select, update
from sqlalchemy.orm import Session
from api.schemas import CreateSchema, ModelType, UpdateSchema


class BaseDao(Generic[ModelType, CreateSchema, UpdateSchema]):
    """
    基础数据访问层基类
    所有模型共有的基础数据访问方法，增删改查等
    """

    model: Type[ModelType]  # 具体模型类

    def get_all(self, session: Session) -> list[ModelType]:
        """
        查询所有数据
        """
        return list(session.scalars(select(self.model)).all())

    def get_by_page(
        self, session: Session, page: int = 1, page_size: int = 10
    ) -> list[ModelType]:
        """
        分页查询数据
        """
        if page <= 0:
            page = 1
        if page_size <= 0:
            page_size = 10
        return list(
            session.scalars(
                select(self.model).offset((page - 1) * page_size).limit(page_size)
            ).all()
        )

    def get_by_id(self, session: Session, pk: int) -> ModelType | None:
        """
        根据主键的值返回模型对象的实例
        """
        return session.get(self.model, pk)

    def create(self, session: Session, obj_in: CreateSchema) -> ModelType:
        """
        插入一条数据
        """
        obj = self.model(**obj_in.model_dump())  # 把Pydantic的模型类转化为字典
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def update(self, session: Session, obj_in: UpdateSchema) -> ModelType:
        """
        更新一条数据
        """
        obj = self.get_by_id(session, obj_in.id)
        if not obj:
            raise HTTPException(status_code=404, detail="数据不存在")
        # 方法1
        # update_data = obj_in.model_dump(exclude_unset=True)  # 排除模型中的默认值
        # for key, val in update_data.items():
        #     setattr(obj, key, val)
        # session.add(obj)

        # 方法2
        session.execute(
            update(self.model)
            .where(self.model.id == obj_in.id)
            .values(obj_in.model_dump(exclude_unset=True, exclude={"id"}))
        )

        ######
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, pk: int) -> None:
        """
        删除一条数据
        """
        obj = self.get_by_id(session, pk)
        if not obj:
            raise HTTPException(status_code=404, detail="数据不存在")
        session.delete(obj)
        session.commit()
        return None

    def deletes(self, session: Session, pks: list[int]) -> None:
        """
        删除多条数据
        """
        result = session.execute(delete(self.model).where(self.model.id.in_(pks)))
        if isinstance(result, CursorResult) and result.rowcount != len(pks):
            # 异常后会自动回滚事务,所有数据都不会被删除
            raise HTTPException(status_code=404, detail="部分数据不存在")
        session.commit()
        return None

    def count(self, session: Session) -> int | None:
        """
        查询数据总数
        """
        # sqlalchemy2.0写法
        return session.scalar(select(func.count()).select_from(self.model))
