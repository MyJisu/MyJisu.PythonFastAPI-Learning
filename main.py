# 知识点：FastAPI 应用实例化；Path/Query 参数校验组件；Depends 依赖注入；Pydantic BaseModel/Field 字段配置
# 用途：导入所需组件并创建 app 对象，所有接口通过 app 装饰器注册
from fastapi import FastAPI,Path,Query,Depends
from pydantic import BaseModel,Field
app = FastAPI()


# 知识点：@app.get 路由装饰器、async 异步函数、JSON 响应
# 用途：根路径 GET 接口，访问 / 返回欢迎信息，用于确认服务已启动
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
