from sqlalchemy import select


from api.system_mgt.user_schemas import CreateUserSchema, UpdateUserSchema
from db.dao import BaseDao
from db.system_mgt.user_models import UserModel
from sqlalchemy.orm import Session


class UserDao(BaseDao[UserModel, CreateUserSchema, UpdateUserSchema]):
    """用户模块中，专门处理数据库操作的dao类"""

    model = UserModel  # 数据模型类

    # 因为BaseDao 中已经定义了增删改查方法，这里无需再定义

    # 可以根据需要自定义其他方法
    def get_by_username(self, session: Session, username: str) -> UserModel | None:
        """根据用户名查询用户"""
        result = session.execute(
            select(self.model).where(self.model.username == username)
        ).scalar_one_or_none()
        print(6666, result)
        return result
