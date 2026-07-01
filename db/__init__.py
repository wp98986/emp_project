from datetime import datetime

from config import settings


from sqlalchemy import URL, DateTime, create_engine, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    sessionmaker,
)

# 数据库连接URL
url = URL(
    drivername=settings.DATABASE.DRIVER,
    database=settings.DATABASE.NAME,
    host=settings.DATABASE.HOST,
    port=settings.DATABASE.PORT,
    username=settings.DATABASE.USERNAME,
    password=settings.DATABASE.PASSWORD,
    query=settings.DATABASE.QUERY,
)


engine = create_engine(
    url,
    echo=True,  # 打印SQL语句
    future=True,  # 启用未来版本的SQLAlchemy
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
    pool_timeout=30,  # 连接池超时时间
    pool_recycle=3600,  # 连接池回收时间
)


# 创建会话工厂（每个请求在中间件中创建独立session）
SessionFactory = sessionmaker(
    bind=engine,
    autoflush=True,
    autocommit=False,
)


# 定义数据库模型类的父类
class DBModelBase(DeclarativeBase):
    """定义一系列的可以映射的公共属性，此类是所有数据库模型类的父类"""

    @declared_attr.directive  # @declared_attr这是一个“类级别的声明”，在每个子类上都会被单独执行, 用于动态生成表名
    def __tablename__(cls) -> str:
        return (
            "t_" + cls.__name__.lower()
        )  # 未来所有的模型中：表名就是：t_当前模型类名字

    __table_args__ = {"mysql_engine": "InnoDB"}  # 数据库存储模型为InnoDB
    #  如果为true，则ORM将在插入或更新之后立即获取服务器生成的默认值的值
    __mapper_args__ = {"eager_defaults": True}  

    # 所有的模型类，都有的属性和字段映射
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, insert_default=func.now(), comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        insert_default=func.now(),
        onupdate=func.now(),
        comment="最后修改时间",
    )
