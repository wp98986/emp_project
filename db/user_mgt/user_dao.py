from api.user_mgt.user_schemas import CreateUserSchema, UpdateUserSchema
from db.dao import BaseDao
from db.user_mgt.user_models import UserModel


class UserDao(BaseDao[UserModel, CreateUserSchema, UpdateUserSchema]):
    """用户模块中，专门处理数据库操作的dao类"""

    model = UserModel  # 数据模型类

    # 因为BaseDao 中已经定义了增删改查方法，这里无需再定义
    # 可以根据需要自定义其他方法
