# 封装统一格式的成功 JSON 响应，借助 jsonable_encoder 自动处理各类对象序列化，和全局异常处理器保持返回结构一致。
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(message: str = "success", data=None):
    content = {
        "code": 200,
        "message": message,
        "data": data
    }
    return JSONResponse(content=jsonable_encoder(content))
