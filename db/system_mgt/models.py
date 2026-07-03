from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import mapped_column, Mapped, relationship

from db import DBModelBase

# 多对多关联，先定义中间表
user_role_middle_table = Table(
    "t_user_role",
    DBModelBase.metadata,
    Column(
        "user_id", ForeignKey("t_usermodel.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "role_id", ForeignKey("t_rolemodel.id", ondelete="CASCADE"), primary_key=True
    ),  # 联合主键
)


class UserModel(DBModelBase):
    """
    用户模型
    """

    # DBModelBase 中已经根据子类名定义了表名，这里无需再定义表名
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(
        String(20), nullable=True, comment="用户的手机号码"
    )
    email: Mapped[str] = mapped_column(
        String(50), nullable=True, comment="用户的邮箱地址"
    )
    real_name: Mapped[str] = mapped_column(
        String(50), nullable=True, comment="用户的真实名字"
    )
    icon: Mapped[str] = mapped_column(
        String(100),
        default="/static/user_icon/default.jpg",
        nullable=True,
        comment="用户的展示头像",
    )
    # 和部门表关联的外键
    dept_id: Mapped[int | None] = mapped_column(
        ForeignKey("t_deptmodel.id"), nullable=True
    )
    # 定义一个关联属性： 该员工所属的部门
    dept: Mapped[DeptModel | None] = relationship(
        "DeptModel", back_populates="emp_list", cascade="save-update", lazy="select"
    )

    # 多对多的关联属性
    roles: Mapped[list[RoleModel]] = relationship(
        secondary=user_role_middle_table, lazy="select", cascade="save-update"
    )


class MenuModel(DBModelBase):
    """菜单模型类： 只有两级"""

    number: Mapped[int] = mapped_column(Integer, nullable=False, comment="排序数字")
    url: Mapped[str] = mapped_column(
        String(200), nullable=True, comment="前端路由访问地址，可以没有"
    )
    name: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="菜单显示的名称"
    )
    is_parent: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="是否为顶级菜单", default=False
    )

    # 外键
    pid: Mapped[int | None] = mapped_column(ForeignKey("t_menumodel.id"), nullable=True)
    # 定义一个关联属性
    children: Mapped[list[MenuModel]] = relationship(
        back_populates="parent", order_by=number.desc()
    )
    # 定义一个关联属性
    parent: Mapped[MenuModel | None] = relationship(
        "MenuModel", back_populates="children", remote_side="MenuModel.id"
    )

    # 该菜单中所有的权限列表
    permissions_list: Mapped[list[PermissionModel]] = relationship(
        back_populates="menu", cascade="save-update, delete", lazy="dynamic"
    )


class PermissionModel(DBModelBase):
    """权限模型类"""

    name: Mapped[str] = mapped_column(String(20), nullable=False, comment="权限名字")
    is_interface: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="是否为接口", default=False
    )
    url: Mapped[str] = mapped_column(
        String(200), nullable=True, comment="接口访问地址，可以没有"
    )
    method: Mapped[str] = mapped_column(
        String(20), nullable=True, comment="接口的请求方法，可以没有"
    )

    # 外键
    menu_id: Mapped[int | None] = mapped_column(
        ForeignKey("t_menumodel.id"), nullable=True
    )
    menu: Mapped[MenuModel | None] = relationship(
        back_populates="permissions_list", cascade="save-update"
    )

    # 外键
    pid: Mapped[int | None] = mapped_column(
        ForeignKey("t_permissionmodel.id"), nullable=True
    )
    # 定义一个关联属性
    children: Mapped[list[PermissionModel]] = relationship(
        back_populates="parent"
    )
    # 定义一个关联属性
    parent: Mapped[PermissionModel | None] = relationship(
        back_populates="children", remote_side="PermissionModel.id"
    )


# 多对多关联，先定义中间表
role_permission_middle_table = Table(
    "t_role_permission",
    DBModelBase.metadata,
    Column(
        "permission_id",
        ForeignKey("t_permissionmodel.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id", ForeignKey("t_rolemodel.id", ondelete="CASCADE"), primary_key=True
    ),  # 联合主键
)


class RoleModel(DBModelBase):
    """角色模型类"""

    name: Mapped[str] = mapped_column(String(20), nullable=False, comment="角色的名字")
    remark: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="角色的备注"
    )
    # 多对多的关联属性
    permissions: Mapped[list[PermissionModel]] = relationship(
        secondary=role_permission_middle_table, lazy="dynamic"
    )


class DeptModel(DBModelBase):
    """部门模型类"""

    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    city: Mapped[str] = mapped_column(String(50))

    # 定义一个关联属性：一个部门下的所有员工
    emp_list: Mapped[list[UserModel]] = relationship(
        back_populates="dept", cascade="save-update", lazy="dynamic"
    )

    # 定义一个外键：关联到父机构
    pid: Mapped[int | None] = mapped_column(ForeignKey("t_deptmodel.id"), nullable=True)

    # 定义一个关联属性
    children: Mapped[list[DeptModel]] = relationship(back_populates="parent")
    # 定义一个关联属性
    parent: Mapped[DeptModel | None] = relationship(
        "DeptModel", back_populates="children", remote_side="DeptModel.id"
    )
    # 部门的负责人, 没有采用外键关联
    leader_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    leader_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
