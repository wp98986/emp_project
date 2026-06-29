# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 **FastAPI + SQLAlchemy + MySQL** 的员工管理系统 (EMP) 后端 API 服务。当前仅实现了用户管理 (user\_mgt) 模块，提供完整的 CRUD 接口。前端目录 (`/frontend`) 预留但未实现。

## 技术栈

- **Web 框架**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy 2.0 (声明式基类 + scoped\_session)
- **数据库**: MySQL (配置在 `config/development.yml`)
- **迁移工具**: Alembic
- **配置管理**: Dynaconf (`config/development.yml`)
- **认证**: JWT (HS256, 30分钟过期)
- **会话**: 自定义 DB Session 中间件

## 目录结构

```
main.py                  # 应用入口，创建 FastAPI 实例并挂载中间件
api/                     # API 层（路由 + Schema）
├── routes.py            # 路由注册中心，按版本分组 (route_v1)
├── schemas.py           # 通用泛型定义 (ModelType/CreateSchema/UpdateSchema) 和 InDBMixin
└── user_mgt/            # 用户管理模块
    ├── user_view.py     # FastAPI 路由定义 + 业务响应组装
    └── user_schemas.py  # Pydantic Schema (CreateUserSchema/UpdateUserSchema/UserSchema)
db/                      # 数据层（模型 + DAO）
├── __init__.py          # SQLAlchemy 引擎、SessionFactory、DBModelBase（公共字段 id/create\_time/update\_time）
├── dao.py               # BaseDao 泛型基类：CRUD + 分页 + 批量删除 + count
└── user_mgt/
    ├── user_models.py   # ORM 模型 (UserModel)
    └── user_dao.py      # UserDao（继承 BaseDao，指定泛型参数）
utils/                   # 工具层
├── session_middleware.py # DB Session 中间件（请求开始创建 session，请求结束关闭）
├── cors.py              # CORS 中间件初始化
├── dependencis.py       # 依赖注入 (get\_db, CommonQueryParams)
└── handle_error.py      # 全局异常处理器 (HTTPException, RequestValidationError)
config/                  # 配置
├── __init__.py          # Dynaconf 初始化
├── development.yml      # 开发环境配置
└── log_config.py        # 日志配置
alembic/                 # 数据库迁移脚本
```

## 关键架构模式

### 1. 泛型 BaseDao 模式

`db/dao.py` 中的 `BaseDao[ModelType, CreateSchema, UpdateSchema]` 是所有业务 DAO 的基类。子类只需指定 `model` 类属性，即可继承 get\_all/get\_by\_page/get\_by\_id/create/update/delete/deletes/count 等方法。

### 2. 分层路由结构

`api/routes.py` 中 `route_v1()` 聚合各模块路由，统一挂载到 `/api` 前缀。新增模块时在 `route_v1()` 中添加 `include_router` 即可。

### 3. 响应格式

所有 API 返回统一格式：`{"code": 200, "msg": "...", "data": ...}`。`ApiResponse[T]` 泛型模型定义在 `api/user_mgt/user_view.py` 中。

### 4. 数据库会话生命周期

通过 FastAPI 中间件在每个 HTTP 请求开始时创建 SQLAlchemy session 并注入到 `request.state.session`，请求结束时关闭。`utils/dependencis.py` 中的 `get_db` 依赖注入函数从中取出 session。

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

1. 在 `db/<module>/` 下创建 `user_models.py` 风格的 ORM 模型
2. 在 `db/<module>/` 下创建 `user_dao.py` 风格的 DAO 类（继承 BaseDao）
3. 在 `api/<module>/` 下创建 `user_schemas.py` 风格的 Pydantic Schema
4. 在 `api/<module>/` 下创建 `user_view.py` 风格的路由文件
5. 在 `api/routes.py` 的 `route_v1()` 中 `include_router`

## 配置说明

- 开发配置在 `config/development.yml`
- 通过环境变量 `EMP_ENV=production` 切换环境
- 通过环境变量前缀 `EMP_CONF_` 覆盖配置项
- JWT Secret 等敏感信息当前硬编码在配置文件中，生产环境应使用环境变量或密钥管理服务
