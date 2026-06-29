from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from api import routes
from config.log_config import init_log
from utils import cors, handle_error, middleware
from config import settings
from utils.oauth2 import MyOAuth2PasswordBearer

# from utils.jwt_utils import create_access_token


class Server:
    def __init__(self):
        """初始化服务器"""
        init_log()  # 初始化日志
        # 创建自定义的OAuth2的实例
        my_oauth2 = MyOAuth2PasswordBearer(tokenUrl="/api/user/auth", schema="JWT")
        """
        添加全局的依赖: 让所有的接口，都拥有接口文档的认证.
        这个是给接口文档用的，测试接口时需要登录获取token，登录口测试接口时自动携带token
        不影响前端的正常访问，
        """
        self.app = FastAPI(dependencies=[Depends(my_oauth2)])  #
        self.app.mount(
            "/static", StaticFiles(directory="static"), name="my_static"
        )  # 挂载静态文件目录

    def init_app(self):
        """初始化应用"""
        handle_error.init_error_handler(self.app)  # 初始化全局异常处理
        middleware.init_middleware(self.app)  # 初始化中间件
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

    # access_token = create_access_token({"user_id": "1233", "username": "testuser"})
    # print(access_token)
