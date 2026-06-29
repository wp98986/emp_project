from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from db import SessionFactory
import logging

log = logging.getLogger("emp")  # 创建一个logger日志器，命名为emp


async def db_session_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    数据库会话中间件
    每个请求开始时创建一个数据库会话，在请求结束时关闭会话
    定义一个中间件函数, 请求处理之前，和响应返回之前
    """
    # 定义一个错误响应，把字典转换成json格式
    response_err = JSONResponse(
        content={"error": "服务器错误！请检查接口"}, status_code=500
    )
    print(response_err)
    try:
        # 从SessionFactory创建一个session，并注入到请求状态中state中。命名为session
        request.state.session = SessionFactory()
        response = await call_next(
            request
        )  # 继续向下执行，调用下一个中间件或路由处理函数
    except Exception as e:
        log.error(e)  # 记录错误日志
        return response_err
    finally:
        # 关闭session会话
        request.state.session.close()
    return response


def init_middleware(app: FastAPI):
    # 注册中间件,FASTAPI 90%是http中间件
    app.middleware("http")(db_session_middleware)
