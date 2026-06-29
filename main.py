from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from api import routes
from config.log_config import init_log
from utils import cors, handle_error, session_middleware
from config import settings


class Server:
    def __init__(self):
        """初始化服务器"""
        init_log()  # 初始化日志
        self.app = FastAPI()
        self.app.mount(
            "/static", StaticFiles(directory="static"), name="my_static"
        )  # 挂载静态文件目录

    def init_app(self):
        """初始化应用"""
        handle_error.init_error_handler(self.app)  # 初始化全局异常处理
        session_middleware.init_middleware(self.app)  # 初始化中间件
        cors.init_cors(self.app)  # 初始化CORS
        routes.init_routes(self.app)  # 初始化路由

    # def run(self):
    #     """运行服务器"""
    #     self.init_app()
    #       这样不能热重启
    #     # uvicorn.run(app=self.app, host=settings.HOST, port=settings.PORT)
    #     uvicorn.run("main:app", host=settings.HOST, port=settings.PORT)


# if __name__ == "__main__":
#     # 启动服务器
#     print("Server is running on http://localhost:8000")
#     Server().run()


server = Server()
server.init_app()
app = server.app


@app.get("/", tags=["root"])
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    print("Server is running on http://localhost:8000")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
