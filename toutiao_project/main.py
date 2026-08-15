from fastapi import FastAPI
from routers import news, users, favorite
from fastapi.middleware.cors import CORSMiddleware
from utils.exception_handlers import register_exception_handlers

# 运行
# netstat -ano | findstr ":8000" | ForEach-Object { $parts = $_ -split '\s+'; taskkill /F /PID $parts[-1] }
# uvicorn main:app --reload
app = FastAPI()
# 注册异常处理器
register_exception_handlers(app)
# 跨域资源共享中间件：解决前端页面（Vue/HTML 等）和后端 FastAPI跨域请求被浏览器拦截的问题。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # 允许的源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],     # 允许的请求方法
    allow_headers=["*"],     # 允许的请求头
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

# 挂载注册路由
app.include_router(news.router)
app.include_router(users.router)

app.include_router(favorite.router)
