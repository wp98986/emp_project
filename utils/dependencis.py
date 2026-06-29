from fastapi import Request
from sqlalchemy.orm import Session

# 依赖注入函数


def get_db(request: Request) -> Session:
    """
    session依赖注入函数
    """
    # 从请求状态中获取session, 即session_middleware中注入的session
    return request.state.session


class CommonQueryParams:
    """
    定义分页参数的依赖注入
    """

    def __init__(self, page: int = 1, page_size: int = 10):
        if page <= 0:
            page = 1
        if page_size <= 0:
            page_size = 10

        self.page = page
        self.page_size = page_size

        self.offset = (page - 1) * page_size
        self.limit = page_size
