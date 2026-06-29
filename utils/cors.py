from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings


# 配置跨域中间件
def init_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,  # 跨域中间件FASTAPI自带
        allow_origins=["*"],  # 允许所有来源的跨域请求
        # allow_origins=settings.ORIGINS,  # 允许指定来源的跨域请求
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
