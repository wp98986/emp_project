from typing import List, Tuple

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, delete, text, bindparam
from sqlalchemy.orm import Session

from api.system_mgt.permission_schemas import (
    UpdatePermissionSchema,
    CreatePermissionSchema,
)
from db.dao import BaseDao
from db.system_mgt.models import PermissionModel


class PermissionDao(
    BaseDao[PermissionModel, CreatePermissionSchema, UpdatePermissionSchema]
):
    """
    权限模块中，专门处理数据库操作的Dao类
    """

    model = PermissionModel

    def get_parent_permission(self, session: Session) -> list[PermissionModel]:
        """
        查询所有的顶级父权限列表， 树形结构
        :param session:
        :return:
        """
        stmt = select(self.model).where(self.model.pid.is_(None))
        return list(session.scalars(stmt).all())

    def get_menu_bypermission(
        self, session: Session, uname: str
    ) -> Tuple[list[dict], list[str]]:
        """
        根据用户查询，该用户拥有权限的菜单列表，同时返还结果中的菜单列表，必须是树形
        :param session:
        :param uname
        :return:
        """
        #  查询该用户所拥有的权限ID列表
        sql = text(
            "select distinct t3.permission_id from t_usermodel t1 join t_user_role t2 on t1.id=t2.user_id join t_role_permission t3 on t2.role_id=t3.role_id where t1.username=:un"
        )
        result = session.execute(
            sql, {"un": uname}
        ).all()  # 是列表中，嵌套元祖 [(2,), (4,)]
        print("resul233333t:", result)
        permission_ids = list(map(lambda t: t[0], result))
        print("permission_ids:", permission_ids)
        if not permission_ids:
            # return [], []  # 如果没有权限，直接返回空列表
            permission_ids = []
        # 指定返回的字段名字
        stmt = select(
            PermissionModel.id,
            PermissionModel.pid,
            PermissionModel.name,
            PermissionModel.url,
        ).where(
            PermissionModel.id.in_(permission_ids),
            PermissionModel.is_interface == False,
        )
        res = session.execute(stmt).all()  # res是一个列表，列表中是多个row对象。

        # 把列表中的菜单变成树形结构

        menus_list = []  # 菜单列表
        menus_dict = (
            {}
        )  # 临时存放所有的菜单: key：菜单的id，值就是整个菜单字典 {3: {'id':3, 'name': 系统管理, url: /roles, pid: 1}， 4: {....}}
        for item in res:  # item是一个row对象
            menus_dict[item.id] = {c: getattr(item, c) for c in item._fields}

        for i in menus_dict:  # i 是每个菜单的主键
            if menus_dict[i]["pid"]:  # 当前菜单是一个二级菜单
                pid = menus_dict[i]["pid"]
                parent = menus_dict[pid]  # parent是一个一级菜单
                parent.setdefault("children", []).append(menus_dict[i])
            else:  # 当前菜单是一级菜单
                menus_list.append(menus_dict[i])

        # 查询该用户，所拥有的按钮权限
        sql2 = text(
            'select concat(url, "^", method)  from t_permissionmodel where is_interface=1 and id in :ids'
        ).bindparams(bindparam('ids', expanding=True))
        result2 = session.execute(sql2, {"ids": permission_ids})
        print("result2:", result2)
        rows = result2.fetchall()
        print("rows:", rows)
        permissions = list(map(lambda t: t[0], rows))
        return menus_list, permissions

    def delete(self, session: Session, pk: int) -> None:
        """
        删除一条记录, 先把权限和角色的中间表的数据删除
        :param session:
        :param pk:
        :return:
        """
        session.execute(
            text("delete from t_role_permission where permission_id=:id"), {"id": pk}
        )
        super().delete(session, pk)
