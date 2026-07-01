from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from api.system_mgt.user_schemas import CreateUserSchema, UpdateUserSchema, UserSearchQuery

from db.dao import BaseDao
from db.system_mgt.models import UserModel, RoleModel


class UserDao(BaseDao[UserModel, CreateUserSchema, UpdateUserSchema]):
    """
    用户模块中，专门处理数据库操作的Dao类
    """

    model = UserModel

    def get_by_username(self, session: Session, username: str):
        """
        根据用户名，查询用户对象
        :param session:
        :param username:
        :return:
        """
        stmt = select(self.model).where(self.model.username == username)
        return session.execute(stmt).scalars().first()

    def search_user(
        self,
        session: Session,
        uid: int = None,
        username: str = None,
        real_name: str = None,
    ):
        """
        根据查询条件，查询用户列表，注意：分页查询，只要返回一个query对象就可以。
        :param uid:
        :param real_name:
        :param session:
        :param username:
        :return:
        """
        q = session.query(self.model)
        if uid:
            q = q.filter(self.model.id == uid)
        if username:
            q = q.filter(self.model.username == username)
        if real_name:
            q = q.filter(self.model.real_name.like(f"%{real_name}%"))
        return q

    def search_user_query(
        self,
        session: Session,
        query: UserSearchQuery,
    ):
        """
        根据搜索条件构建查询对象（不分页），供 fastapi-pagination 使用。
        :param session: 数据库会话
        :param query: 搜索条件
        :return: SQLAlchemy Query 对象
        """
        q = session.query(self.model)
        if query.id:
            q = q.filter(self.model.id == query.id)
        if query.username:
            q = q.filter(self.model.username == query.username)
        if query.real_name:
            q = q.filter(self.model.real_name.like(f"%{query.real_name}%"))
        if query.dept_id:
            q = q.filter(self.model.dept_id == query.dept_id)
        if query.phone:
            q = q.filter(self.model.phone == query.phone)
        return q

    def deletes(self, session: Session, ids: List[int]):
        """
        用户的批量删除，在删除用户之前，先把该用户分配的角色删除
        :param session:
        :param ids:
        :return:
        """
        session.execute(
            text("delete from t_user_role where user_id in :ids"), {"ids": ids}
        )
        super().deletes(session, ids)

    def create(self, session: Session, obj_in: CreateUserSchema) -> UserModel:
        """
        插入一条用户数据
        :param session:
        :param obj_in:
        :return:
        """
        obj = self.model(**jsonable_encoder(obj_in))  # 把Pydantic的模型类转化为字典
        # 处理角色
        role_list = session.scalars(
            select(RoleModel).where(RoleModel.id.in_(obj.roles))
        ).all()
        obj.roles = role_list
        session.add(obj)
        session.commit()
        return obj

    def update(self, session: Session, pk: int, obj_in: UpdateUserSchema) -> UserModel:
        """
        修改一条用户数据
        :param session:
        :param pk: 主键ID
        :param obj_in: 修改的BaseModel类
        :return:
        """
        obj = self.get_by_id(session, pk)
        update_data = obj_in.dict(exclude_unset=True)  # 排除模型中的默认值
        print("update_data:", update_data)
        # 处理角色
        role_list = session.scalars(
            select(RoleModel).where(RoleModel.id.in_(update_data.pop("roles")))
        ).all()
        print("role_list:", role_list)
        print("update_data:", obj)
        obj.roles = role_list
        for key, val in update_data.items():
            setattr(obj, key, val)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
