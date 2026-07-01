# CLAUDE.md

## 项目概述

这是一个基于 **FastAPI + SQLAlchemy + MySQL** 的员工管理系统 (EMP) 后端 API 服务。实现了用户管理、角色管理、权限管理、部门管理、菜单管理五大模块，提供完整的 CRUD 接口。前端目录 (`/frontend`) 预留但未实现。

## 技术栈

- **Web 框架**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy 2.0 (声明式基类 + scoped_session)
- **数据库**: MySQL (配置在 `config/development.yml`)
- **迁移工具**: Alembic
- **配置管理**: Dynaconf (`config/development.yml`)
- **认证**: JWT (HS256, 30分钟过期)
- **会话**: 自定义 DB Session 中间件
- **分页**: fastapi-pagination (基于 SQLAlchemy 扩展)
- **密码哈希**: pwdlib (bcrypt + argon2)

## 目录结构

```
main.py                  # 应用入口，创建 FastAPI 实例并挂载中间件
api/                     # API 层（路由 + Schema）
├── routes.py            # 路由注册中心，按版本分组 (route_v1)
├── schemas.py           # 通用泛型定义 (ModelType/CreateSchema/UpdateSchema) 和 InDBMixin
└── system_mgt/          # 系统管理模块
    ├── __init__.py      # ApiResponse 通用响应模型
    ├── user_views.py    # 用户管理路由
    ├── user_schemas.py  # 用户 Pydantic Schema
    ├── dept_views.py    # 部门管理路由
    ├── dept_schemas.py  # 部门 Pydantic Schema
    ├── role_views.py    # 角色管理路由
    ├── role_schemas.py  # 角色 Pydantic Schema
    ├── menu_views.py    # 菜单管理路由
    ├── menu_schemas.py  # 菜单 Pydantic Schema
    ├── permission_views.py  # 权限管理路由
    └── permission_schemas.py # 权限 Pydantic Schema
db/                      # 数据层（模型 + DAO）
├── __init__.py          # SQLAlchemy 引擎、SessionFactory、DBModelBase（公共字段 id/create_time/update_time）
├── dao.py               # BaseDao 泛型基类：CRUD + 批量删除 + count
└── system_mgt/
    ├── models.py        # 所有 ORM 模型 (UserModel, RoleModel, DeptModel, MenuModel, PermissionModel)
    ├── user_dao.py      # UserDao（继承 BaseDao）
    ├── dept_dao.py      # DeptDao
    ├── role_dao.py      # RoleDao
    ├── menu_dao.py      # MenuDao
    └── permission_dao.py # PermissionDao
utils/                   # 工具层
├── middleware.py        # DB Session 中间件 + JWT Token 校验中间件
├── cors.py             # CORS 中间件初始化
├── dependencis.py      # 依赖注入 (get_db, CommonQueryParams)
├── handle_error.py     # 全局异常处理器 (HTTPException, RequestValidationError)
├── oauth2.py           # 自定义 OAuth2PasswordBearer（支持白名单跳过）
├── jwt_utils.py        # JWT token 生成
├── password_hash.py    # 密码哈希/验证（基于 pwdlib）
config/                 # 配置
├── __init__.py         # Dynaconf 初始化
├── development.yml     # 开发环境配置
└── log_config.py       # 日志配置
alembic/                # 数据库迁移脚本
```

## 关键架构模式

### 1. 泛型 BaseDao 模式

`db/dao.py` 中的 `BaseDao[ModelType, CreateSchema, UpdateSchema]` 是所有业务 DAO 的基类。子类只需指定 `model` 类属性，即可继承 get_all/get_by_page/get_by_id/create/update/delete/deletes/count 等方法。

### 2. 分层路由结构

`api/routes.py` 中 `route_v1()` 聚合各模块路由，统一挂载到 `/api` 前缀。新增模块时在 `route_v1()` 中添加 `include_router` 即可。

### 3. 响应格式

所有 API 返回统一格式：`{"code": 200, "msg": "...", "data": ...}`。`ApiResponse[T]` 泛型模型定义在 `api/system_mgt/__init__.py` 中。

### 4. 数据库会话生命周期

通过 FastAPI 中间件在每个 HTTP 请求开始时创建 SQLAlchemy session 并注入到 `request.state.session`，请求结束时关闭。`utils/dependencis.py` 中的 `get_db` 依赖注入函数从中取出 session。

### 5. JWT 权限校验

`utils/middleware.py` 中的 `verify_token` 中间件在每个请求上校验 JWT token。`config/development.yml` 中的 `WHITE_LIST` 配置了免认证的白名单路径。`utils/oauth2.py` 中的 `MyOAuth2PasswordBearer` 使接口文档的认证表单也支持白名单跳过。

### 6. 分页

使用 `fastapi-pagination` 库的 SQLAlchemy 扩展。在 `main.py` 中通过 `add_pagination(app)` 注册。路由中使用 `from fastapi_pagination.ext.sqlalchemy import paginate`，调用 `paginate(query_object)` 自动返回分页结果 `{items, total, page, page_size}`。

## 常用命令

```bash
# 启动开发服务器 (热重载)
python main.py
# 服务运行在 http://127.0.0.1:8000
# API 文档: http://127.0.0.1:8000/docs

# 数据库迁移（首次）
alembic upgrade head

# 生成新的迁移脚本
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 查看迁移历史
alembic history
```

## 添加新模块的步骤

1. 在 `db/system_mgt/` 下创建 `xxx_models.py` 风格的 ORM 模型（如已有 models.py 可追加）
2. 在 `db/system_mgt/` 下创建 `xxx_dao.py` 风格的 DAO 类（继承 BaseDao）
3. 在 `api/system_mgt/` 下创建 `xxx_schemas.py` 风格的 Pydantic Schema
4. 在 `api/system_mgt/` 下创建 `xxx_views.py` 风格的路由文件
5. 在 `api/routes.py` 的 `route_v1()` 中 `include_router`

## 配置说明

- 开发配置在 `config/development.yml`
- 通过环境变量 `EMP_ENV=production` 切换环境
- 通过环境变量前缀 `EMP_CONF_` 覆盖配置项
- JWT Secret 等敏感信息当前硬编码在配置文件中，生产环境应使用环境变量或密钥管理服务
