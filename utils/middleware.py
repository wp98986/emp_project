import re
from typing import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from httpx import head
import jwt
from db import SessionFactory
import logging
from config import settings
import json

log = logging.getLogger("emp")  # 创建一个logger日志器，命名为emp


# 加密算法
ALGORITHM = settings.ALGORITHM
# 密钥
JWT_SECRET_KEY = settings.JWT_SECRET_KEY


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
    # print(response_err)
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


async def verify_token(request: Request, call_next: Callable[[Request]]) -> Response:
    """
    验证token
    """

    # path = request.url.path
    # method = request.method
    # query = dict(request.query_params)

    # log_data = json.dumps(
    #     {
    #         "method": method,
    #         "path": path,
    #         "query": query,
    #     },
    #     ensure_ascii=False,
    # )

    # print("请求数据:", log_data)

    auth_error = JSONResponse(
        content={"detail": "非法token，请重新登录"},
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )

    auth_expired = JSONResponse(
        content={"detail": "Token 已过期，请重新登录"},
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 白名单url不需要校验toekn
    white_list = settings.WHITE_LIST
    path = request.url.path
    print("path:", path)

    for item in white_list:
        if re.match(item, path):
            print("命中白名单url:", item)
            # 命中白名单url，直接放行
            return await call_next(request)
    else:
        # print("================未命中白名单url，校验token================")
        authorization: str = request.headers.get("Authorization", "")
        if not authorization:
            # 中间件校验token失败，不能直接返回HTTPException ❌️
            # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未授权")
            return auth_error
        auth_token = authorization.split(" ")[1]
        try:
            # 解析token，获取用户信息，将用户信息注入到请求状态中state中
            payload = jwt.decode(auth_token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
            print("解析token成功:", payload)
            sub, user_name = payload.get("sub"), payload.get("user_name")
            # 校验token合法性
            if not sub:  # sub 是用户id
                return auth_error
            request.state.user = {"user_id": sub, "user_name": user_name}
            return await call_next(
                request
            )  # 继续向下执行，调用下一个中间件或路由处理函数
        except jwt.ExpiredSignatureError as e:
            # jwt 自动校验token是否过期，无需要手动校验过期时间
            log.error(e)  # 记录错误日志
            return auth_expired
        except Exception as e:
            log.error(e)  # 记录错误日志
            return auth_error


def init_middleware(app: FastAPI):
    # 注册中间件,FASTAPI 90%是http中间件
    app.middleware("http")(db_session_middleware)
    app.middleware("http")(verify_token)
