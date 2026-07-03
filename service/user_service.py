"""
用户业务逻辑层 (UserService)

职责：
  - 用户注册：检查用户名唯一性、密码加密
  - 用户登录：校验用户名/密码、签发 JWT
  - 用户 CRUD：委托 DAO 完成数据存取
  - 批量删除：委托 DAO 清理关联角色

不直接操作 session / request / response，
session 由构造注入，Controller 负责组装。
"""

from db.system_mgt.user_dao import UserDao
from utils.password_hash import get_password_hash, verify_password
from utils.jwt_utils import create_access_token


class UserService:
    """用户业务服务"""

    def __init__(self, dao: UserDao | None = None):
        self.dao = dao or UserDao()

    # ------------------------------------------------------------------ #
    # 注册 & 登录
    # ------------------------------------------------------------------ #

    def register(self, session, username: str, password: str, **kwargs):
        """
        注册用户

        :param session: SQLAlchemy session
        :param username: 用户名
        :param password: 明文密码
        :param kwargs: 其余字段 (phone, email, real_name, icon, dept_id, roles)
        :return: UserModel
        """
        # 1. 用户名唯一性校验
        if self.dao.get_by_username(session, username):
            raise ValueError(f"用户名 '{username}' 已存在")

        # 2. 组装数据（密码在此处加密）
        password_hashed = get_password_hash(password)

        # 3. 调用 DAO 创建
        from api.system_mgt.user_schemas import CreateUserSchema

        payload = {"username": username, "password": password_hashed, **kwargs}
        schema = CreateUserSchema(**payload)
        return self.dao.create(session, schema)

    def login(self, session, username: str, password: str):
        """
        用户登录

        :return: dict {user_dict, token}
        """
        user = self.dao.get_by_username(session, username)
        if not user:
            raise ValueError("用户名不存在")

        if not verify_password(password, user.password):
            raise ValueError("密码错误")

        token = create_access_token(data={"sub": str(user.id), "username": username})

        user_dict = {
            "id": user.id,
            "username": user.username,
            "phone": user.phone,
            "email": user.email,
            "real_name": user.real_name,
            "icon": user.icon,
            "token": token,
        }
        return user_dict

    # ------------------------------------------------------------------ #
    # CRUD 委托
    # ------------------------------------------------------------------ #

    def get_all(self, session):
        """获取所有用户"""
        return self.dao.get_all(session)

    def get_by_id(self, session, pk: int):
        """根据 ID 获取用户"""
        return self.dao.get_by_id(session, pk)

    def search(self, session, id=None, username=None, real_name=None,
               dept_id=None, phone=None):
        """分页查询前的条件构建（供 Controller 传入 Query 参数）"""
        from api.system_mgt.user_schemas import UserSearchQuery

        query = UserSearchQuery(
            id=id,
            username=username,
            real_name=real_name,
            dept_id=dept_id,
            phone=phone,
        )
        return self.dao.search_user_query(session, query)

    def create(self, session, username: str, password: str, **kwargs):
        """创建用户（内部复用 register 的业务逻辑）"""
        return self.register(session, username, password, **kwargs)

    def update(self, session, pk: int, **kwargs):
        """
        更新用户

        :param pk: 主键
        :param kwargs: 要更新的字段
        """
        from api.system_mgt.user_schemas import UpdateUserSchema

        # 排除 password 的话，DAO 不会更新它
        obj_in = UpdateUserSchema(id=pk, **kwargs)
        return self.dao.update(session, pk, obj_in)

    def delete(self, session, pk: int):
        """删除单个用户"""
        return self.dao.delete(session, pk)

    def batch_delete(self, session, pks: list[int]):
        """批量删除用户（清理关联角色）"""
        return self.dao.deletes(session, pks)
