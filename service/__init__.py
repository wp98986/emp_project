"""
Service 层

Service 层位于 Controller (Views) 和 DAO 之间，职责：
  - 封装业务逻辑（校验、事务编排、多 DAO 协作）
  - DAO 只负责数据存取，不包含业务规则
  - Controller 只做参数接收 / 响应组装，不写业务逻辑

分层结构：
  Controller (views) → Service → DAO → Model
"""
