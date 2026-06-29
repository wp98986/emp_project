from fastapi import FastAPI, Request

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from fastapi.responses import JSONResponse


async def handle_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """处理异常"""
    return JSONResponse(content={"error": exc.detail}, status_code=exc.status_code)


async def handle_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """处理参数验证错误"""
    errors = exc.errors()
    error_messages = []
    for error in errors:
        loc = ".".join(str(l) for l in error["loc"])
        msg = error["msg"]
        error_messages.append(f"{loc}: {msg}")
    return JSONResponse(
        content={"error": "参数错误", "details": error_messages},
        status_code=422
    )

def init_error_handler(app: FastAPI) -> None:
    """初始化异常处理"""
    #  注意必须是：starlette.exceptions 中的 HTTPException
    app.add_exception_handler(HTTPException, handle_exception_handler)
    #  注意必须是：fastapi.exceptions 中的 RequestValidationError
    app.add_exception_handler(RequestValidationError, handle_validation_exception_handler)  
