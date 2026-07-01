from typing import List

from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from api.system_mgt.dept_schemas import DeptCreateSchema, DeptUpdateSchema

from db.dao import BaseDao
from db.system_mgt.models import DeptModel, UserModel


class DeptDao(BaseDao[DeptModel, DeptCreateSchema, DeptUpdateSchema]):
    """
    部门模块中，专门处理数据库操作的Dao类
    """

    model = DeptModel

    def get_parent_dept(self, session: Session) -> List[DeptModel]:
        """
        查询所有的顶级父部门列表， 树形结构
        :param session:
        :return:
        """
        stmt = select(self.model).where(self.model.pid.is_(None))
        return list(session.scalars(stmt).all())

    # def deletes(self, session: Session, ids: List[int]):
    #     """
    #     角色的批量删除，如果该角色已经分配给用户了，则不能删除。
    #     如果当前角色可以删除：
    #     1、先删除这个角色分配的权限
    #     2、再删除该角色
    #     :param session:
    #     :param ids:
    #     :return:
    #     """
    #     session.execute(text('delete from t_role_permission where role_id in :ids'), {'ids': ids})
    #     super().deletes(session, ids)

    def count_user(self, session: Session, ids: List[int]):
        """
        查询角色下的用户数量
        :param session:
        :param ids:
        :return:
        """
        # 查询这些部门下面的用户数量
        sql = text("select count(1) from t_usermodel where dept_id=:rid")
        result = session.execute(sql, {"rid": ids[0]}).first()
        if result is None:
            return 0
        return result[0]

    def count_child(self, session: Session, did: int):
        """
        查询角色下的用户数量
        :param session:
        :param did:
        :return:
        """
        # 查询该部门下子部门的数量
        sql = text("select count(1) from t_deptmodel where pid=:rid")
        result = session.execute(sql, {"rid": did}).first()
        if result is None:
            return 0
        return result[0]
