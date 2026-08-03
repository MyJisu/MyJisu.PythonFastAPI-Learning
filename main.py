# # 知识点：FastAPI 应用实例化；Path/Query 参数校验组件；Depends 依赖注入；Pydantic BaseModel/Field 字段配置
# # 用途：导入所需组件并创建 app 对象，所有接口通过 app 装饰器注册
from fastapi import FastAPI,Path,Query,Depends
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi import FastAPI,HTTPException,Depends

app = FastAPI()
#
# 第一天
# # 知识点：@app.get 路由装饰器、async 异步函数、JSON 响应
# # 用途：根路径 GET 接口，访问 / 返回欢迎信息，用于确认服务已启动
@app.get("/")
async def root():
    return {"message": "Hello World"}


# 知识点：路径参数（{name}）与类型标注、f-string 字符串拼接
# 用途：从 URL 路径中取出 name 参数，返回动态问候语
@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# 知识点：无参数 GET 接口；与 /hello/{name} 路径区分，函数名可复用
# 用途：对比展示有无路径参数的两种路由写法
@app.get("/hello")
async def say_hello():
    return {"message": "Hello FastAPI!"}


# 知识点：Path() 参数校验——ge/le 数值范围限制、description 接口文档描述
# 用途：限制路径中的书籍 id 在 1-100，超出范围自动返回 422 校验错误
@app.get("/book/{id}")
async def findbook(id: int = Path(..., ge=1,le=100,description="书籍ID取值范围1-100")):
    return {"id": id, "title": f"这是编号为{id}的书"}

# 知识点：Path() 字符串校验——min_length/max_length 长度限制
# 用途：限制作者名字长度为 2-10 个字符，不符合则校验失败
@app.get("/writer/{name}")
async def findwriter(name: str = Path(max_length=10,min_length=2,description="查询作者名字长度为2-10")):
    return {"作者": name}


# 知识点：Query() 查询参数——默认值、le 上限校验
# 用途：实现分页/列表接口，通过 ?skip=&limit= 控制跳过的记录数和返回条数
@app.get("/news/list")
async def findnews(
        skip: int = Query(0,le = 1000,description="跳过的记录数"),
        limit: int = Query(10,le = 100000,description="返回的记录数")
):
    return {"skip": skip, "limit": limit}


# 知识点：Pydantic BaseModel 数据模型 + Field() 字段配置——默认值、min_length/max_length 校验
# 用途：定义注册请求的数据结构；username 带默认值（可不传），password 必填
class User(BaseModel):
    username: str = Field(default="MyJisu",min_length=2,max_length=10)
    password: str


# 知识点：POST 请求；请求体模型参数；FastAPI 自动校验并序列化模型为 JSON 返回
# 用途：注册接口，接收用户提交的数据并回显（学习用；实际项目不应把密码回传给客户端）
@app.post("/register")
async def register(user: User):
    return user

# 第二天
# # 知识点：response_class=HTMLResponse 指定响应类型；with open 读取本地文件
# # 用途：读取 index.html 文件内容返回给浏览器，实现前端页面与后端代码分离
@app.get("/html",response_class=HTMLResponse)
async def get_html():
    with open("index.html","r",encoding="utf-8") as f:
        html=f.read()
        return html


# # 知识点：response_class=FileResponse 文件流式响应，直接返回服务器上的静态文件
# # 用途：访问 /files 直接返回本地视频文件，浏览器可在线播放或下载
@app.get("/files",response_class=FileResponse)
async def get_files():
    path = "./files/MC.mp4"
    return FileResponse(path)


# # 知识点：Pydantic BaseModel 定义响应数据模型
# # 用途：定义新闻的数据结构（id/title/content），作为接口返回的数据模板
class News(BaseModel):
    id: int
    title: str
    content: str


# # 知识点：response_model 响应模型——按模型自动过滤多余字段并序列化为 JSON 返回
# # 用途：按 id 返回一条模拟新闻数据，展示响应模型的使用方式
@app.post("/news/{id}",response_model=News)
async def get_news(id: int):
    return {
        "id": id,
        "title": f"这是第{id}本书",
        "content": "这是一本好书"
    }


# # 知识点：HTTPException 手动抛出异常——status_code 状态码 + detail 错误信息
# # 用途：判断 id 是否在预置列表中，不在则返回 404 和提示信息，实现标准的资源不存在处理
@app.get("/News/{id}")
async def get_News(id: int):
    id_list = [1,2,3,4,5,6,7,8,9,10]
    if id not in id_list:
        raise HTTPException(status_code=404,detail="不存在")
    return {"id": id}


# # 知识点：@app.middleware("http") 中间件；call_next 调用后续处理流程
# # 用途：在请求进入和离开时打印日志，观察请求经过中间件的处理顺序（类似全局拦截器）
@app.middleware("http")
async def middleware1(request,call_next):
    print("中间件1 start")
    response = await call_next(request)
    print("中间件1 end")
    return response

@app.middleware("http")
async def middleware2(request,call_next):
    print("中间件2 start")
    response = await call_next(request)
    print("中间件2 end")
    return response


# # 知识点：Depends 依赖注入——把公共参数提取为独立函数，接口通过 Depends() 传入复用
# # 用途：定义公共分页参数 skip/limit，供多个接口共用，避免重复定义
async def common_parameters(
        skip: int = Query(0,ge = 0),
        limit: int = Query(10,le = 60)
):
    return {"skip": skip, "limit": limit}

# # 知识点：依赖注入的实际应用——不同接口共用同一个依赖函数
# # 用途：新闻列表接口复用分页依赖，返回分页参数
@app.get("/news/news_list")
async def get_news_list(commons = Depends(common_parameters)):
    return commons

# # 知识点：同一依赖可被多个接口复用，实现代码复用
# # 用途：用户列表接口复用同一套分页逻辑
@app.get("/user/user_list")
async def get_user_list(commons = Depends(common_parameters)):
    return commons