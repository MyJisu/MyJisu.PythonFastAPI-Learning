# # 知识点：FastAPI 应用实例化；Path/Query 参数校验组件；Depends 依赖注入；Pydantic BaseModel/Field 字段配置
# # 用途：导入所需组件并创建 app 对象，所有接口通过 app 装饰器注册
from datetime import datetime

from fastapi import FastAPI,Path,Query,Depends
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi import FastAPI,HTTPException,Depends
from rich import status
from sqlalchemy import DateTime, func, Integer, String, Float, select
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
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
# @app.get("/book/{id}")
# async def findbook(id: int = Path(..., ge=1,le=100,description="书籍ID取值范围1-100")):
#     return {"id": id, "title": f"这是编号为{id}的书"}

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


# 第三天 ORM
# # 知识点：create_async_engine 异步数据库引擎；连接串格式；echo/pool_size/max_overflow 连接池配置
# # 用途：创建异步引擎连接本机 MySQL，统一管理数据库连接；echo 在控制台打印 SQL 便于调试
ASYNC_DATABASE_URL = "mysql+aiomysql://root:myy20050921@localhost:3306/FastAPI_second?charset=utf8"
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)


# # 知识点：DeclarativeBase 声明式基类；Mapped 类型标注；mapped_column 字段映射；func.now() 数据库当前时间
# # 用途：定义公共基类 Base，抽取所有表共有的创建/修改时间字段，供子模型继承复用
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime, default=func.now(), comment="创建的时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), comment="修改的时间")


# # 知识点：ORM 模型定义（class 继承 Base）；__tablename__ 指定表名；primary_key 主键；String/Float 字段类型
# # 用途：定义 book 数据表结构，模型属性与数据库字段一一对应
class Book(Base):
    __tablename__= "book"
    id: Mapped[int] = mapped_column(primary_key=True,comment="书籍id")
    bookname: Mapped[str] = mapped_column(String(255),comment="书名")
    author: Mapped[str] = mapped_column(String(255),comment="作者")
    price: Mapped[float] = mapped_column(Float,comment="价格")
    publisher: Mapped[str] = mapped_column(String(255),comment="出版社")


# # 知识点：Base.metadata.create_all 建表；conn.run_sync 在异步连接中执行同步操作
# # 用途：按所有模型定义创建数据库中不存在的表，应用启动时调用
async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# # 知识点：@app.on_event("startup") 启动事件，应用启动时自动执行一次
# # 用途：启动服务时自动建表，无需手动执行建表 SQL
@app.on_event("startup")
async def startup():
    await create_tables()


# # 知识点：async_sessionmaker 会话工厂；bind 绑定引擎；class_ 会话类型；expire_on_commit 提交后对象不过期
# # 用途：创建会话工厂，供依赖注入统一生成操作数据库的会话
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# # 知识点：带 yield 的依赖注入（生成器依赖）；commit 提交 / rollback 回滚 / close 关闭会话
# # 用途：为接口提供数据库会话；接口执行完自动提交，异常时自动回滚，最后关闭会话释放连接
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# # 知识点：select 查询所有；await db.execute 执行查询；.scalars().all() 取出全部结果
# # 用途：查询 book 表全部记录（等价于 SELECT * FROM book）
@app.get("/book/select1")
async def get_books_list(db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Book))
    book = result.scalars().all()
    return book


# # 知识点：.where(条件) 条件过滤；.scalar_one_or_none() 取至多一条结果
# # 用途：按 id>=2 过滤，取唯一一条数据（没有则返回 None）
@app.get("/book/select2")
async def get_books_list(db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Book).where(Book.id >= 2))
    book = result.scalar_one_or_none()
    return book


# # 知识点：.like("曹%") 模糊查询，% 匹配任意多个字符
# # 用途：查询作者以"曹"开头的书籍
@app.get("/book/select3")
async def get_books_list(db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Book).where(Book.author.like("曹%")))
    book = result.scalars().all()
    return book


# # 知识点：路径参数作查询条件 select(Book).where(Book.id == book_id)
# # 用途：按路径中的书籍 id 精确查询单条记录（无则返回 None）
@app.get("/book/get_book/{book_id}")
async def get_books_list(book_id: int,db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    return book


# # 知识点：db.get(模型, 主键值) 按主键直接查询
# # 用途：按主键 1 查询书籍（查不到返回 None），写法最简洁
@app.get("/book/get")
async def get_books_list(db: AsyncSession = Depends(get_database)):
    book = await db.get(Book,1)
    return book


# # 知识点：func.聚合函数（count/max/sum/avg）；.scalar() 取单个标量结果
# # 用途：统计 book 表价格的聚合值（当前演示平均值，其余聚合函数可切换注释使用）
@app.get("/book/count")
async def get_books_count(db: AsyncSession = Depends(get_database)):
    # result = await db.execute(select(func.count(Book.id)))  # 总行数
    # result = await db.execute(select(func.max(Book.price)))  # 最高价
    # result = await db.execute(select(func.sum(Book.price)))  # 总价
    result = await db.execute(select(func.avg(Book.price)))   # 平均价
    count = result.scalar()
    return count


# # 知识点：分页查询——skip=(page-1)*page_size；.offset(跳过条数).limit(每页条数)
# # 用途：按页码/每页条数分页返回书籍列表，通过 ?page=&page_size= 传参
@app.get("/book/get_books/list")
async def get_books_list(
        page: int = 1,
        page_size: int = 2,
        db: AsyncSession = Depends(get_database)
):
    skip = (page - 1)*page_size
    stmt = select(Book).offset(skip).limit(page_size)
    result = await db.execute(stmt)
    books = result.scalars().all()
    return books


# # 知识点：Pydantic 模型定义新增数据——id 可选（int | None），其余字段必填
# # 用途：定义新增书籍时的请求体结构；id 不传时由后端自动补号
class BookBase(BaseModel):
    id: int | None = None   # 可选：不传则自动分配最小的空闲 id（自动补号）
    bookname: str
    author: str
    price: float
    publisher: str


# # 知识点：POST 新增——model_dump() 模型转字典；db.add() 添加对象；commit 提交事务
# # 用途：新增书籍接口；未传 id 时自动分配最小空闲 id，提交后返回新增记录
@app.post("/book/add_book")
async def add_book(book:BookBase,db: AsyncSession = Depends(get_database)):
    data = book.model_dump()
    # 自动补号：没传 id 时，找出当前最小的空闲 id（复用被删除的编号）
    if data["id"] is None:
        result = await db.execute(select(Book.id).order_by(Book.id))
        used_ids = result.scalars().all()
        next_id = 1
        for i in used_ids:          # 遍历已占用的 id，跳过连续的，找到第一个空位
            if i == next_id:
                next_id += 1
            else:
                break
        data["id"] = next_id
    book_obj = Book(**data)
    db.add(book_obj)
    await db.commit()
    return book_obj


# # 知识点：Pydantic 模型定义更新数据——所有字段必填
# # 用途：定义更新书籍时的请求体结构，配合路径参数定位要修改的记录
class BookUpdate(BaseModel):
    id: int
    bookname: str
    author: str
    price: float
    publisher: str


# # 知识点：PUT 更新——路径参数定位记录；db.get() 判断是否存在；修改对象属性 + commit 保存
# # 用途：按书籍 id 更新书名/作者/价格/出版社，未找到则返回 404
@app.put("/book/up_date_book/{book_id}")
async def up_data_book(book_id: int,data: BookUpdate,db: AsyncSession = Depends(get_database)):
    db_book = await db.get(Book,book_id)
    if db_book is None:
        raise HTTPException(
            status_code=404,
            detail="未找到此书"
        )

    db_book.bookname = data.bookname
    db_book.author = data.author
    db_book.price = data.price
    db_book.publisher = data.publisher

    await db.commit()
    return db_book


# # 知识点：DELETE 删除——db.get() 判断是否存在；db.delete() 删除对象；commit 提交
# # 用途：按书籍 id 删除记录，未找到则返回 404，成功返回删除提示
@app.delete("/book/delete_book/{book_id}")
async def delete_book(book_id: int,db: AsyncSession = Depends(get_database)):
    db_book = await db.get(Book,book_id)
    if db_book is None:
        raise HTTPException(
            status_code=404,
            detail="未找到此书"
        )

    await db.delete(db_book)
    await db.commit()
    return {"msg":"删除成功"}
