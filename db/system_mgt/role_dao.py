from typing import List

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from api.system_mgt.role_schemas import RoleCreateSchema, RoleUpdateSchema, SetPermissionToRole
from db.dao import BaseDao
from db.system_mgt.models import RoleModel


class RoleDao(BaseDao[RoleModel, RoleCreateSchema, RoleUpdateSchema]):
    """
    用户模块中，专门处理数据库操作的Dao类
    """

    model = RoleModel

    def search_roles(
        self, session: Session, rid: int | None = None, name: str | None = None
    ):
        """
        根据查询条件，查询角色列表，注意：分页查询，只要返回一个query对象就可以。
        """
        q = select(self.model)
        if rid:
            q = q.where(self.model.id == rid)
        if name:
            q = q.where(self.model.name.like(f"%{name}%"))
        return session.scalars(q).all()

    def get_checked_keys(self, session: Session, rid: int | None = None) -> List[int]:
        """
        查询该角色已勾选的权限ID列表(可以直接访问的权限列表)
        :param session:
        :param rid:
        :return:
        """
        sql = text(
            "select b.id from t_role_permission a join t_permissionmodel b on a.permission_id=b.id where a.role_id = :rid and b.is_interface=1"
        )
        result = session.execute(sql, {"rid": rid}).all()
        return [r.id for r in result]

    def get_half_keys(self, session: Session, rid: int = None) -> List[int]:
        """
        查询该角色半勾选的权限ID列表(菜单权限列表)
        :param session:
        :param rid:
        :return:
        """
        sql = text(
            "select b.id from t_role_permission a join t_permissionmodel b on a.permission_id=b.id where a.role_id = :rid and b.is_interface=0"
        )
        result = session.execute(sql, {"rid": rid}).all()
        return [r.id for r in result]

    def set_permission(self, session: Session, obj_in: SetPermissionToRole):
        """
        给角色修改权限：1、删除之前所分配权限， 2、在添加所有的权限
        :param session:
        :param obj_in:
        :return:
        """
        rid = obj_in.id
        delete_sql = text("delete from t_role_permission where role_id = :rid")
        session.execute(delete_sql, {"rid": rid})
        # 第二步: 采用批量添加  insert into table (字段1， 字段2) values (值a1，值b1)，(值a2，值b2)，(值a3，值b3)，...
        insert_sql = "insert into t_role_permission (permission_id, role_id) values "
        for pid in obj_in.permissions.halfKeys:
            insert_sql += f"({pid}, {rid}),"
        for pid in obj_in.permissions.checkedKeys:
            insert_sql += f"({pid}, {rid}),"
        insert_sql = text(insert_sql[: len(insert_sql) - 1])  # 把最后一个逗号去掉
        session.execute(insert_sql)
        session.commit()

    def deletes(self, session: Session, ids: List[int]):
        """
        角色的批量删除，如果该角色已经分配给用户了，则不能删除。
        如果当前角色可以删除：
        1、先删除这个角色分配的权限
        2、再删除该角色
        :param session:
        :param ids:
        :return:
        """
        session.execute(
            text("delete from t_role_permission where role_id in :ids"), {"ids": ids}
        )
        super().deletes(session, ids)

    def count_user(self, session: Session, ids: List[int]):
        """
        查询角色下的用户数量
        :param session:
        :param ids:
        :return:
        """
        # 查询这些角色下面的用户数量
        sql = text("select count(1) from t_user_role where role_id=:rid")
        result = session.execute(sql, {"rid": ids[0]}).first()
        return result[0]
