from typing import List, Tuple

from dynaconf.cli import inspect
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, delete, text, and_
from sqlalchemy.orm import Session

from api.system_mgt.menu_schemas import MenuCreateSchema, MenuUpdateSchema

from db.dao import BaseDao
from db.system_mgt.models import MenuModel, PermissionModel


class MenuDao(BaseDao[MenuModel, MenuCreateSchema, MenuUpdateSchema]):
    """
    菜单模块中，专门处理数据库操作的Dao类
    """

    model = MenuModel

    def get_parent_menu(self, session: Session) -> list[MenuModel]:
        """
        查询所有的顶级父菜单列表， 树形结构
        :param session:
        :return:
        """
        stmt = (
            select(self.model)
            .where(self.model.pid.is_(None))
            .order_by(self.model.number.desc())
        )
        return list(session.scalars(stmt).all())

    def deletes(self, session: Session, ids: list[int]):
        """
        菜单的批量删除， 首先删除菜单对应的权限，然后再删除菜单
        :param session:
        :param ids:
        :return:
        """
        session.execute(delete(PermissionModel).where(PermissionModel.menu_id.in_(ids)))
        super().deletes(session, ids)

    def count_children(self, session: Session, ids: List[int]):
        """
        查询菜单下的子菜单的数量
        :param session:
        :param ids:
        :return:
        """
        return session.query(self.model).filter(self.model.pid.in_(ids)).count()

    def create(
        self, session: Session, obj_in: MenuCreateSchema
    ) -> MenuModel:
        """
        插入一条数据
        :param session:
        :param obj_in:
        :return:
        """
        # 先插入菜单
        menu = self.model(**jsonable_encoder(obj_in))  # 把Pydantic的模型类转化为字典
        session.add(menu)
        # 然后再新增菜单多对应的权限
        pm = PermissionModel(
            name=menu.name, url=menu.url, is_interface=False, menu=menu
        )
        # 处理权限的父子关系
        if not menu.is_parent:  # 是二级菜单
            parent = session.scalars(
                select(PermissionModel).where(PermissionModel.menu_id == menu.pid)
            ).first()
            pm.pid = parent.id
        session.add(pm)
        session.commit()
        return menu
