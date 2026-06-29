from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from db import DBModelBase


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
