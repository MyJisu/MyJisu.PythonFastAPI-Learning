# FastAPI 知识点汇总

> 一个通过「写代码 + 写笔记」逐步学习 FastAPI 的练习仓库。用 **3 天渐进式示例代码**
> （集中在 [`main.py`](main.py)）覆盖 FastAPI 的核心知识点：路由与参数校验 → 响应 / 异常 /
> 中间件 / 依赖注入 → 异步 ORM 数据库操作。正文按天逐条讲解**每个知识点实现了什么、为什么
> 这么写、怎么用**，每个示例都给出完整、可直接运行的代码。

---

## 一、项目简介

| 项 | 说明 |
|----|------|
| **学习目标** | 从零掌握 FastAPI 的路由、参数校验、响应类型、异常处理、中间件、依赖注入与异步数据库操作 |
| **学习路线** | 第 1 天：路由与参数校验 → 第 2 天：响应 / 异常 / 中间件 / 依赖注入 → 第 3 天：SQLAlchemy 异步数据库 |
| **代码形式** | 所有接口集中在 `main.py`，按天分区，每段代码上方有「知识点 / 用途」注释，可直接运行 |
| **配套笔记** | 正文按天详解知识点；附录 A / B / C 分别汇总专业术语、关键字规范用法、关键字分类速查 |
| **接口文档** | FastAPI 自动生成交互式文档（Swagger UI），启动后访问 `http://127.0.0.1:8000/docs` |

## 二、技术栈

| 技术 | 版本 | 作用 |
|------|------|------|
| Python | 3.12 | 开发语言 |
| FastAPI | 0.141 | Web 框架，自动校验参数并生成接口文档 |
| Uvicorn | 0.52 | ASGI 服务器，负责启动应用、监听端口 |
| Pydantic | 2.x | 数据模型校验与序列化 |
| SQLAlchemy | 2.x | ORM 框架（异步），用 Python 类操作数据库表 |
| aiomysql | — | 连接 MySQL 的异步驱动（第 3 天用） |
| MySQL | 8.x | 关系型数据库（第 3 天用） |

> 依赖已安装在项目虚拟环境 `.venv` 中，可用 `.venv\Scripts\python -m pip list` 查看。

## 三、环境要求与快速开始

**环境要求：**

- Python 3.10+（本仓库在 Python 3.12 下编写）
- MySQL 8.x（仅第 3 天 ORM 部分需要，需提前创建好数据库）

**快速开始：**

```bash
# 1. 创建并激活虚拟环境（可选，但推荐）
python -m venv .venv
# Windows：
.venv\Scripts\activate
# macOS / Linux：
source .venv/bin/activate

# 2. 安装依赖（第 1、2 天所需）
pip install fastapi "uvicorn[standard]"
# 第 3 天额外安装数据库相关依赖
pip install "sqlalchemy[asyncio]" aiomysql

# 3.（第 3 天代码需要）修改数据库连接串
#    编辑 main.py 中的 ASYNC_DATABASE_URL，替换为自己的 MySQL 账号密码：
#    ASYNC_DATABASE_URL = "mysql+aiomysql://用户名:密码@localhost:3306/数据库名?charset=utf8"

# 4. 启动应用（--reload：修改代码后自动重启）
uvicorn main:app --reload

# 5. 访问验证
#   接口文档（Swagger UI）：http://127.0.0.1:8000/docs
#   根路径接口：            http://127.0.0.1:8000/
```

**常用调试方式：**

- 接口测试：浏览器访问 `/docs` 在线调试；或用 Postman / IDEA 的 HTTP Client（仓库内已有 `test_main.http`）。
- 查看日志：`main.py` 中数据库引擎设置了 `echo=True`，控制台会打印每条 SQL，便于观察第 3 天的查询语句。

## 四、目录结构

```
FastAPI_Learning1/
├── main.py           # 全部示例代码，按天分区（第 1~3 天）
├── index.html        # 第 2 天 HTMLResponse 示例读取的网页
├── test_main.http    # IDEA HTTP Client 接口测试脚本
├── files/
│   └── MC.mp4        # 第 2 天 FileResponse 示例返回的视频（大文件，已加入 .gitignore）
├── toutiao_project/  # FastAPI 新闻后端：用户、新闻、收藏、历史
├── xwzx-news/        # Vue 3 + Vite 新闻前端：首页、详情、AI 问答
├── .venv/            # 虚拟环境（已加入 .gitignore）
└── README.md         # 学习笔记（本文件）
```

## 五、接口一览

> 全部接口集中在 `main.py`，按天分组；「对应知识点」指向正文各小节，详细讲解见正文。

**第 1 天 —— 路由与参数校验：**

| 方法 | 路径 | 功能 | 对应知识点 |
|------|------|------|-----------|
| GET | `/` | 返回欢迎信息 | 1.2 路由 / 1.3 async |
| GET | `/hello/{name}` | 路径参数动态问候 | 1.4 路径参数 / 1.5 f-string |
| GET | `/hello` | 无参数问候 | 1.6 函数名可复用 |
| GET | `/writer/{name}` | 作者名长度校验 | 1.8 Path 字符串长度 |
| GET | `/news/list` | 分页参数（skip / limit） | 1.9 Query 默认值与上限 |
| POST | `/register` | 注册（请求体模型） | 1.10 ~ 1.12 BaseModel |

**第 2 天 —— 响应、异常、中间件、依赖注入：**

| 方法 | 路径 | 功能 | 对应知识点 |
|------|------|------|-----------|
| GET | `/html` | 返回本地 HTML 页面 | 2.1 HTMLResponse |
| GET | `/files` | 返回本地视频文件 | 2.2 FileResponse |
| POST | `/news/{id}` | 按 id 返回新闻（响应模型过滤） | 2.4 response_model |
| GET | `/News/{id}` | 校验 id，不存在抛 404 | 2.5 HTTPException |
| GET | `/news/news_list` | 复用分页依赖 | 2.8 依赖注入 |
| GET | `/user/user_list` | 复用同一分页依赖 | 2.8 依赖注入 |

**第 3 天 —— ORM 数据库：**

| 方法 | 路径 | 功能 | 对应知识点 |
|------|------|------|-----------|
| GET | `/book/select1` | 查询全部书籍 | 3.6 select + scalars().all() |
| GET | `/book/select2` | 条件查询取单条 | 3.7 where + scalar_one_or_none() |
| GET | `/book/select3` | 作者模糊查询 | 3.9 like("曹%") |
| GET | `/book/get_book/{book_id}` | 按路径参数精确查询 | 3.8 where(字段 == 参数) |
| GET | `/book/get` | 按主键查询 | 3.10 db.get() |
| GET | `/book/count` | 聚合统计（平均价） | 3.11 func.avg + scalar() |
| GET | `/book/get_books/list` | 分页查询 | 3.12 offset + limit |
| POST | `/book/add_book` | 新增书籍（自动补号） | 3.13 db.add() + model_dump() |
| PUT | `/book/up_date_book/{book_id}` | 更新书籍 | 3.14 修改对象属性 + commit |
| DELETE | `/book/delete_book/{book_id}` | 删除书籍 | 3.15 db.delete() |

---

## 目录

- [项目简介 / 技术栈 / 快速开始 / 接口一览](#一项目简介)
- [第 1 天：FastAPI 基础与参数校验](#第-1-天fastapi-基础与参数校验)
- [第 2 天：响应类型、异常、中间件与依赖注入](#第-2-天响应类型异常中间件与依赖注入)
- [第 3 天：ORM 数据库（SQLAlchemy 异步）](#第-3-天orm-数据库sqlalchemy-异步)
- [已学知识点速查](#已学知识点速查)
- [附录 A：专业术语详解](#附录-a专业术语详解)
- [附录 B：关键字详解](#附录-b关键字详解)
- [附录 C：关键字分类总览（按功能角色）](#附录-c-关键字分类总览按功能角色)

---

## 第 1 天：FastAPI 基础与参数校验

### 1.1 导入与创建应用

```python
from fastapi import FastAPI, Path, Query, Depends, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse, FileResponse

app = FastAPI()
```

**`from 包 import 组件`**

从指定包（`fastapi`、`pydantic`、`fastapi.responses`）中导入所需的组件（类、函数、装饰器），导入后才能在当前文件中使用。

**`app = FastAPI()`**

实例化一个 FastAPI 应用对象。所有路由（接口）都通过 `app` 上的装饰器（`@app.get`、`@app.post` 等）注册到这个应用上。一个文件中通常只创建一次，放在文件开头。

---

### 1.2 路由装饰器 `@app.get`

```python
@app.get("/")
async def root():
    return {"message": "Hello World"}
```

**`@app.get(路径)`**

路由装饰器。将下面的函数注册为应用的一个接口：当客户端以 GET 方式访问该路径时，FastAPI 会调用这个函数并返回其结果。

**HTTP 常用方法对应的装饰器：**

| 装饰器 | HTTP 方法 | 用途 |
|--------|-----------|------|
| `@app.get` | GET | 获取数据 |
| `@app.post` | POST | 提交数据 |
| `@app.put` | PUT | 更新数据 |
| `@app.delete` | DELETE | 删除数据 |

**返回值的处理：**

函数返回的 Python 字典（`dict`）会被 FastAPI 自动序列化为 JSON 格式返回给客户端。例如返回 `{"message": "Hello World"}`，客户端收到的是 JSON 对象。

---

### 1.3 异步函数 `async`

```python
@app.get("/")
async def root():
    return {"message": "Hello World"}
```

**`async` 关键字**

声明该函数为异步函数（coroutine）。异步函数在遇到耗时的 I/O 操作（如读写文件、查询数据库）时，可以主动让出执行权，让服务器处理其他请求，而不是阻塞等待。FastAPI 中的接口函数建议统一使用 `async` 定义。

---

### 1.4 路径参数与类型标注

```python
@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
```

**路径参数**

在路由路径中使用花括号 `{}` 包裹参数名（如 `{name}`），客户端访问时把实际值填入对应位置。例如访问 `/hello/小明` 时，`name` 会被赋值为 `"小明"`。

**类型标注 `参数名: 类型`**

声明参数的数据类型。FastAPI 会根据标注自动完成类型转换、数据校验，并反映在自动生成的接口文档中。常用类型：

| 标注 | 类型 | 示例 |
|------|------|------|
| `str` | 字符串 | `"abc"` |
| `int` | 整数 | `3` |
| `float` | 浮点数 | `3.14` |
| `bool` | 布尔值 | `True` |

---

### 1.5 f-string 字符串格式化

```python
f"Hello {name}"
```

**f-string（格式化字符串）**

在字符串引号前加字母 `f`，字符串内部用 `{表达式}` 把变量或表达式的值插入到字符串中。`f"Hello {name}"` 中 `name = "小明"` 时，结果为 `"Hello 小明"`。

**与字符串拼接的对比：**

```python
# 使用 + 拼接（需手动处理类型）
"Hello " + name

# 使用 f-string（更简洁，自动处理）
f"Hello {name}"
```

注意 `f` 前缀不可省略，否则 `{name}` 会被当作普通字符原样输出。

---

### 1.6 无参数接口与函数名复用

```python
@app.get("/hello")
async def say_hello():
    return {"message": "Hello FastAPI!"}
```

FastAPI 区分接口的依据是 **HTTP 方法 + 路径**，而不是函数名。因此多个接口可以同名函数（如上面两个接口都叫 `say_hello`），只要路径不同即可。

---

### 1.7 `Path()` 参数校验 —— 数值范围

```python
@app.get("/book/{id}")
async def findbook(id: int = Path(..., ge=1, le=100, description="书籍ID取值范围1-100")):
    return {"id": id, "title": f"这是编号为{id}的书"}
```

**`Path(...)`**

路径参数的校验组件。通过关键字参数设置校验规则。

**`...`（Ellipsis）**

表示"必填"，即该参数没有默认值，客户端必须传入。若设置了 `default` 值则可不传。

**校验关键字参数：**

| 参数 | 含义 | 示例 |
|------|------|------|
| `ge` | greater/equal，≥ 指定值 | `ge=1` 要求 ≥ 1 |
| `gt` | greater than，> 指定值 | `gt=1` 要求 > 1 |
| `le` | less/equal，≤ 指定值 | `le=100` 要求 ≤ 100 |
| `lt` | less than，< 指定值 | `lt=100` 要求 < 100 |
| `min_length` | 字符串最短长度 | `min_length=2` |
| `max_length` | 字符串最长长度 | `max_length=10` |
| `description` | 接口文档中的描述文字 | `description="..."` |
| `default` | 默认值，不传时使用 | `default=0` |

**校验失败的结果：**

参数不符合规则时，FastAPI 自动返回 HTTP 422 错误（请求校验失败），无需手动编写判断逻辑。例如访问 `/book/999`（超出 `le=100`），会返回包含错误详情的 422 响应。

---

### 1.8 `Path()` 参数校验 —— 字符串长度

```python
@app.get("/writer/{name}")
async def findwriter(name: str = Path(max_length=10, min_length=2, description="查询作者名字长度为2-10")):
    return {"作者": name}
```

**`min_length` / `max_length`**

限制字符串参数的长度范围。`min_length=2` 表示至少 2 个字符，`max_length=10` 表示最多 10 个字符，超出范围自动返回 422 校验错误。

**注意：**

路径参数即使不写 `...`，由于它位于路径 `{}` 中，FastAPI 默认也视为必填。

---

### 1.9 `Query()` 查询参数

```python
@app.get("/news/list")
async def findnews(
        skip: int = Query(0, le=1000, description="跳过的记录数"),
        limit: int = Query(10, le=100000, description="返回的记录数")
):
    return {"skip": skip, "limit": limit}
```

**查询参数**

URL 中 `?` 之后的键值对，多个参数用 `&` 连接。例如 `/news/list?skip=20&limit=5`。

**`Query()`**

查询参数的校验组件，用法与 `Path()` 一致，支持 `ge/le/min_length/max_length/description/default` 等关键字参数。

**默认值 `Query(0, ...)`**

`Query(0, ...)` 中的 `0` 是默认值：客户端未传该参数时使用默认值；传入了才覆盖。有默认值的参数为可选参数，无默认值（写 `...`）的参数为必填参数。

**分页用法：**

```text
/news/list            # skip=0, limit=10（均使用默认值）
/news/list?skip=20    # skip=20, limit=10
/news/list?skip=20&limit=5   # skip=20, limit=5
```

---

### 1.10 Pydantic 数据模型 `BaseModel`

```python
class User(BaseModel):
    username: str = Field(default="MyJisu", min_length=2, max_length=10)
    password: str
```

**`class 类名(BaseModel)`**

继承 Pydantic 的 `BaseModel` 定义一个数据模型。类中的类属性（字段）声明了数据的结构。Pydantic 模型具备三种能力：

1. **校验**：字段不满足约束时抛错（FastAPI 中表现为返回 422）。
2. **类型转换**：自动把字符串 `"5"` 转为整数 `5`。
3. **序列化**：模型对象可自动转换为 JSON。

**字段定义规则：**

- 有默认值的字段（如 `username`）为可选字段，客户端可以不传。
- 没有默认值的字段（如 `password`）为必填字段，不传则校验失败。

---

### 1.11 Pydantic `Field()` 字段配置

```python
username: str = Field(default="MyJisu", min_length=2, max_length=10)
```

**`Field(关键字参数...)`**

Pydantic 的字段配置组件，为模型字段设置校验规则与元信息。常用参数：

| 参数 | 含义 |
|------|------|
| `default` | 字段默认值 |
| `min_length` | 字符串最短长度 |
| `max_length` | 字符串最长长度 |
| `ge` / `le` | 数值范围 |
| `description` | 字段说明（显示在接口文档中） |

---

### 1.12 POST 请求与请求体模型

```python
@app.post("/register")
async def register(user: User):
    return user
```

**`@app.post(路径)`**

POST 路由装饰器，用于处理客户端提交数据的请求。

**请求体参数**

函数参数的类型为某个 `BaseModel` 子类（如 `User`）时，FastAPI 会读取请求体（body）中的 JSON 数据，按该模型进行校验、转换，并传入函数。

**返回模型对象**

`return user` 直接返回模型对象，FastAPI 会自动将其序列化为 JSON 返回给客户端。

**请求示例：**

```text
POST /register
请求体：
{
    "username": "大猩猩",
    "password": "123456"
}
```

返回：

```json
{
    "username": "大猩猩",
    "password": "123456"
}
```

如果请求体不合法（例如 `username` 只有 1 个字、或缺少必填的 `password`），返回 422 校验错误。

> 注意：真实项目中不应把密码原样返回给客户端，密码应加密存储，此处仅为学习演示。

---

## 第 2 天：响应类型、异常、中间件与依赖注入

### 2.1 `HTMLResponse` 与读取本地文件

```python
@app.get("/html", response_class=HTMLResponse)
async def get_html():
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
        return html
```

**`response_class=HTMLResponse`**

路由装饰器的参数，指定该接口的响应类型为 HTML（网页），而不是默认的 JSON。浏览器收到后会直接渲染成页面。

**`with open() as f:` 读取文件**

```python
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()
```

| 部分 | 说明 |
|------|------|
| `with` | 上下文管理器，代码块结束后自动关闭文件，避免资源泄漏 |
| `open("index.html")` | 打开指定文件 |
| `"r"` | 打开模式：只读 |
| `encoding="utf-8"` | 指定字符编码，读取中文内容时必须指定，否则可能乱码 |
| `as f` | 将文件对象命名为 `f`，便于后续使用 |
| `f.read()` | 一次性读取文件的全部内容 |

**常用打开模式：**

| 模式 | 含义 |
|------|------|
| `"r"` | 只读（默认） |
| `"w"` | 写入（覆盖原内容） |
| `"a"` | 追加（在文件末尾写入） |
| `"rb"` | 二进制只读（用于视频、图片等二进制文件） |

通过读取本地 HTML 文件并返回，可以实现前端页面与后端代码分离：修改页面只需编辑 HTML 文件，无需改动后端代码。

---

### 2.2 `FileResponse` 文件响应

```python
@app.get("/files", response_class=FileResponse)
async def get_files():
    path = "./files/MC.mp4"
    return FileResponse(path)
```

**`response_class=FileResponse`**

指定该接口返回一个本地静态文件（视频、图片、PDF 等）。浏览器收到后可在线预览或下载。

**`FileResponse(路径)`**

文件流式响应对象。传入服务器上的文件路径，FastAPI 会将文件内容分块（流式）发送给客户端，避免大文件一次性载入内存。路径支持相对路径（`./files/MC.mp4` 表示当前目录下 `files` 文件夹中的 `MC.mp4`）。

**注意事项：**

文件名、文件夹名必须与磁盘上的实际名称完全一致（包括大小写），否则返回 404。

---

### 2.3 响应数据模型

```python
class News(BaseModel):
    id: int
    title: str
    content: str
```

定义一个数据模型，规定接口返回数据应有的字段结构与类型。此例中一条新闻必须包含整数 `id`、字符串 `title`、字符串 `content`。

---

### 2.4 响应模型 `response_model`

```python
@app.post("/news/{id}", response_model=News)
async def get_news(id: int):
    return {
        "id": id,
        "title": f"这是第{id}本书",
        "content": "这是一本好书"
    }
```

**`response_model=模型`**

路由装饰器参数，指定接口的响应数据按该模型进行过滤与序列化。

**核心特性：自动过滤多余字段**

即使函数返回的字典中包含模型未定义的字段，FastAPI 也会自动将其剔除，只保留模型声明的字段。

```python
return {
    "id": 1,
    "title": "标题",
    "content": "内容",
    "secret": "机密字段",   # News 模型未定义 → 自动剔除
    "extra": "多余字段"      # News 模型未定义 → 自动剔除
}
```

最终返回：

```json
{
    "id": 1,
    "title": "标题",
    "content": "内容"
}
```

**作用：** 后端可额外计算内部字段，但只把模型允许的字段暴露给客户端，保证返回结构可控、安全。

> 补充说明：该接口使用 `@app.post` 仅为演示 `response_model` 用法，语义上取一条新闻更常使用 GET。

---

### 2.5 手动抛出异常 `HTTPException`

```python
@app.get("/News/{id}")
async def get_News(id: int):
    id_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    if id not in id_list:
        raise HTTPException(status_code=404, detail="不存在")
    return {"id": id}
```

**`HTTPException(status_code=..., detail=...)`**

手动抛出 HTTP 错误响应。`raise` 抛出后，函数立即终止，不再执行后续代码。

**参数：**

| 参数 | 说明 |
|------|------|
| `status_code` | HTTP 状态码，如 404 表示资源不存在 |
| `detail` | 错误详情，返回给客户端的信息 |

**`in` / `not in`**

成员判断运算符。`id not in id_list` 判断 `id` 是否不在列表 `id_list` 中，不在则为 `True`。

**流程：** 若请求的 `id` 不在预置列表中 → 抛出 404 与提示信息；否则正常返回数据。

**常用 HTTP 状态码：**

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求格式错误 |
| 401 | 未登录 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 422 | 参数校验失败 |
| 500 | 服务器内部错误 |

---

### 2.6 HTTP 中间件 `@app.middleware`

```python
@app.middleware("http")
async def middleware1(request, call_next):
    print("中间件1 start")
    response = await call_next(request)
    print("中间件1 end")
    return response

@app.middleware("http")
async def middleware2(request, call_next):
    print("中间件2 start")
    response = await call_next(request)
    print("中间件2 end")
    return response
```

**`@app.middleware("http")`**

HTTP 中间件装饰器。被装饰的函数会在每个请求进入时、以及响应返回前执行，用于在请求处理前后统一做一些操作（打日志、鉴权、统计耗时、跨域处理等），类似全局拦截器。

**参数：**

| 参数 | 说明 |
|------|------|
| `request` | 请求对象 |
| `call_next` | 回调函数，调用它把请求交给下一个处理环节 |
| `response` | 后续环节处理完成后返回的响应对象 |

**`await call_next(request)`**

中间件最关键的一步：把请求交给后续处理流程，等待其完成并拿到响应对象。`start` 输出在调用 `call_next` 之前，`end` 输出在调用之后。

**多个中间件的执行顺序：**

中间件遵循"后定义先执行、后执行先结束"的嵌套顺序。上面的代码在访问任意接口时，控制台输出顺序为：

```text
中间件2 start
中间件1 start
（接口真正的处理逻辑）
中间件1 end
中间件2 end
```

---

### 2.7 依赖注入 `Depends`

```python
async def common_parameters(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, le=60)
):
    return {"skip": skip, "limit": limit}
```

**依赖注入**

把多个接口共用的参数、逻辑提取到一个独立的函数（依赖）中，由 FastAPI 统一准备并注入到各接口，实现代码复用。

**`common_parameters` 函数的作用：**

集中定义分页参数 `skip`、`limit` 及其校验规则（`skip ≥ 0`、`limit ≤ 60`），并将两个参数打包成字典返回：`{"skip": 0, "limit": 10}`。

---

### 2.8 依赖注入的应用

```python
@app.get("/news/news_list")
async def get_news_list(commons=Depends(common_parameters)):
    return commons

@app.get("/user/user_list")
async def get_user_list(commons=Depends(common_parameters)):
    return commons
```

**`Depends(依赖函数)`**

在接口函数参数中以 `参数名 = Depends(依赖函数)` 的方式使用。FastAPI 会调用依赖函数，将其返回值注入到该参数中。

**效果：**

多个接口共用同一套分页逻辑，只需写一行 `Depends(...)`，无需重复定义参数与校验规则。之后如需修改校验规则，只需改依赖函数一处。

**示例：**

访问 `/news/news_list?skip=5&limit=20`，返回：

```json
{
    "skip": 5,
    "limit": 20
}
```

---

## 第 3 天：ORM 数据库（SQLAlchemy 异步）

> 第 3 天用 SQLAlchemy 2.0 的异步组件操作 MySQL。本天开头的代码默认已具备以下导入与公共配置，
> 后续小节不再重复书写导入语句。

**本天新增的导入：**

```python
from datetime import datetime
from sqlalchemy import DateTime, func, Integer, String, Float, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
```

**本天整体流程：**

```text
创建异步引擎（连接池） → 定义模型基类与数据模型 → 应用启动时自动建表
→ 创建会话工厂 → 接口通过依赖注入获取会话 → 用 select 查询数据库
```

### 3.1 创建异步数据库引擎 `create_async_engine`

```python
ASYNC_DATABASE_URL = "mysql+aiomysql://root:密码@localhost:3306/FastAPI_first?charset=utf8"
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)
```

**连接字符串 `ASYNC_DATABASE_URL`**

```text
数据库驱动://用户名:密码@主机:端口/数据库名?charset=utf8
```

- `mysql+aiomysql`：使用 `aiomysql` 异步驱动连接 MySQL 数据库。
- `localhost:3306`：本机 MySQL 的地址和默认端口。
- `?charset=utf8`：指定字符集为 utf8，避免中文乱码。

> 注意：连接串中的密码仅作演示。真实项目中应通过环境变量读取，切勿把密码提交到代码仓库。

**`create_async_engine(连接串, ...)`**

创建异步数据库引擎（Engine）。引擎是连接数据库的"总入口"，负责管理底层连接、执行 SQL。

| 参数 | 说明 |
|------|------|
| `echo=True` | 在控制台打印引擎执行的每条 SQL 语句，方便调试 |
| `pool_size=10` | 连接池中常驻的连接数量 |
| `max_overflow=20` | 连接池用尽后，高峰期最多还能临时创建的连接数 |

**连接池（Connection Pool）**

预先创建并复用一批数据库连接，避免每次请求都重新建立连接（建连耗时较高）。`pool_size` 是常驻数量，`max_overflow` 是弹性上限。

---

### 3.2 声明式基类 `DeclarativeBase` 与公共字段

```python
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), default=func.now(), comment="创建的时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now, onupdate=func.now(), comment="修改的时间")
```

**`class Base(DeclarativeBase)`**

SQLAlchemy 2.0 的声明式基类。之后所有模型类（如 `Book`）都继承它，SQLAlchemy 会自动收集模型定义，最终生成对应的数据表。**`Base` 不要实例化，只作为模型的公共父类。**

**公共字段的作用：**

把每张表都需要的"创建时间、修改时间"抽到基类中，子表自动继承，无需重复定义。后续想在所有表上追加公共字段，只需修改这一处。

**`Mapped[类型]`**

声明字段的 Python 数据类型，配合 `mapped_column` 使用，供 IDE 类型检查与 SQLAlchemy 映射。

**`mapped_column(...)`**

SQLAlchemy 2.0 定义字段的写法（等价于旧版 `Column()`）。

| 参数 | 说明 |
|------|------|
| `DateTime` | 字段类型：日期时间 |
| `insert_default=func.now()` | 插入数据时由数据库写入当前时间 |
| `default=func.now()` | ORM 层默认值 |
| `onupdate=func.now()` | 数据更新时自动刷新为当前时间 |
| `comment="创建的时间"` | 字段注释，写入数据表结构便于查看 |

**`func.now()`**

数据库提供的函数，返回数据库当前的日期时间。由数据库统一生成时间，保证所有数据的时间来源一致。

---

### 3.3 定义模型 `class Book(Base)` 与 `__tablename__`

```python
class Book(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True, comment="书籍id")
    bookname: Mapped[str] = mapped_column(String(255), comment="书名")
    author: Mapped[str] = mapped_column(String(255), comment="作者")
    price: Mapped[float] = mapped_column(Float, comment="价格")
    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")
```

**`class 模型名(Base)`**

继承 `Base` 定义一个 ORM 模型，一个模型对应一张数据表。

**`__tablename__`**

指定模型在数据库中对应的表名（此处为 `"book"`）。不写则 SQLAlchemy 根据类名自动生成。

**`primary_key=True`**

将该字段设为主键。主键唯一标识一行数据，查询、关联都靠它。

**常用字段类型：**

| 类型 | 对应数据库类型 | 用途 |
|------|--------------|------|
| `String(255)` | VARCHAR(255) | 可变长字符串 |
| `Integer` | INT | 整数 |
| `Float` | FLOAT | 浮点数 |
| `DateTime` | DATETIME | 日期时间 |

---

### 3.4 建表 `create_all` 与启动事件

```python
async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await create_tables()
```

**`Base.metadata.create_all`**

根据所有模型的定义，在数据库中创建"还不存在的表"。已存在的表不会重复创建，也不会改动表结构。

**`conn.run_sync(同步操作)`**

在异步引擎中执行同步操作（`create_all` 是同步方法），由 `run_sync` 包装后在异步连接上运行。

**`@app.on_event("startup")`**

FastAPI 的启动事件装饰器：应用启动（运行 `uvicorn`）时自动执行一次被装饰的函数。适合建表、加载配置等一次性初始化工作。

**`async with async_engine.begin() as conn:`**

上下文管理器：进入时开启一个数据库连接（并开启事务），退出时自动提交并释放连接。

---

### 3.5 会话工厂 `async_sessionmaker` 与会话依赖

```python
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

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
```

**`async_sessionmaker(...)`**

创建"会话工厂"。会话（Session）是操作数据库的入口，查询、增删改、事务都通过会话执行。

| 参数 | 说明 |
|------|------|
| `bind=async_engine` | 绑定到指定引擎 |
| `class_=AsyncSession` | 使用异步会话类 |
| `expire_on_commit=False` | 提交后不让对象过期（提交后仍可正常读取字段） |

**`yield session` 依赖注入（生成器依赖）**

`get_database` 是带 `yield` 的依赖函数：FastAPI 先执行到 `yield session`，把会话注入到接口函数；接口执行完毕后，`yield` 后面的代码继续执行，完成提交/回滚/关闭。

**事务三步：**

| 操作 | 说明 |
|------|------|
| `await session.commit()` | 提交事务，把本次更改真正写入数据库 |
| `await session.rollback()` | 出现异常时回滚，撤销本次全部未提交的更改 |
| `await session.close()` | 关闭会话，释放连接 |

**接口使用方式：**

```python
@app.get("/book/select1")
async def get_books_list(db: AsyncSession = Depends(get_database)):
    ...
```

接口通过 `db: AsyncSession = Depends(get_database)` 拿到会话，用完自动关闭，无需手动管理。

---

### 3.6 查询所有 `select` 与 `.scalars().all()`

```python
result = await db.execute(select(Book))
book = result.scalars().all()
```

**`select(模型)`**

构建一条查询语句，等价于 `SELECT * FROM book`。

**`await db.execute(查询)`**

异步执行查询，返回结果对象 `Result`。

**`.scalars().all()`**

`.scalars()` 把结果按模型对象逐行提取，`.all()` 取出全部行，返回一个列表。

---

### 3.7 条件查询 `.where()` 与单条结果

```python
result = await db.execute(select(Book).where(Book.id >= 2))
book = result.scalar_one_or_none()
```

**`.where(条件)`**

为查询添加过滤条件，等价于 SQL 的 `WHERE`。支持比较运算符：`Book.id >= 2`、`Book.id == book_id` 等。

**`.scalar_one_or_none()`**

取"至多一条"结果：有数据返回该行模型对象；没有数据返回 `None`；若查到多行会报错。适合按主键、唯一字段查询。

---

### 3.8 按路径参数精确查询 `where(模型.字段 == 参数)`

```python
@app.get("/book/get_book/{book_id}")
async def get_books_list(book_id: int, db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    return book
```

**`where(Book.id == book_id)`**

把 URL 路径中的 `book_id` 作为查询条件，精确匹配主键字段。等价于 SQL 的 `WHERE id = ?`。

**与 3.7 的区别：**

- 3.7 的过滤条件是写死的常量（`Book.id >= 2`）；
- 本节的过滤条件是**动态的路径参数**（`Book.id == book_id`），参数在运行时被替换为客户端传入的值，实现"传入哪个 id 就查哪一条"。

**执行流程：** 客户端访问 `/book/get_book/3` → `book_id` 被赋值为 `3` → 执行 `select(Book).where(Book.id == 3)` → 查到则返回该书籍对象，查不到返回 `None`。

> 提示：这里的"路径参数"就是 1.4 学的 `/{参数名}` 写法。区别在于：1.4 只是把参数拼进返回字符串，本节用它真正去查询数据库。

---

### 3.9 模糊查询 `.like()`

```python
result = await db.execute(select(Book).where(Book.author.like("曹%")))
book = result.scalars().all()
```

**`.like("曹%")`**

对应 SQL 的 `LIKE` 模糊匹配。`%` 匹配任意多个字符：`"曹%"` 表示"以曹开头"；`"%曹"` 表示"以曹结尾"；`"%曹%"` 表示"包含曹"。

---

### 3.10 主键查询 `db.get()`

```python
book = await db.get(Book, 1)
```

**`db.get(模型, 主键值)`**

按主键直接查询：查到返回对象，查不到返回 `None`。写法最简洁，相当于 `select(Book).where(Book.id == 1)`。

---

### 3.11 聚合函数 `func.count/max/sum/avg`

```python
# result = await db.execute(select(func.count(Book.id)))  # 总行数
# result = await db.execute(select(func.max(Book.price)))  # 最高价
# result = await db.execute(select(func.sum(Book.price)))  # 总价
result = await db.execute(select(func.avg(Book.price)))   # 平均价
count = result.scalar()
```

**`func.聚合函数(字段)`**

调用数据库的聚合函数，对多行做汇总计算。

| 函数 | 含义 |
|------|------|
| `func.count(字段)` | 统计总行数 |
| `func.max(字段)` | 求最大值 |
| `func.sum(字段)` | 求和 |
| `func.avg(字段)` | 求平均值 |

**`.scalar()`**

取单个标量值（一行一列），适合拿聚合统计结果。

---

### 3.12 分页查询 `.offset()` 与 `.limit()`

```python
@app.get("/book/get_books/list")
async def get_books_list(
        page: int = 1,
        page_size: int = 2,
        db: AsyncSession = Depends(get_database)
):
    skip = (page - 1) * page_size
    stmt = select(Book).offset(skip).limit(page_size)
    result = await db.execute(stmt)
    books = result.scalars().all()
    return books
```

**分页公式 `skip = (page - 1) * page_size`**

第 1 页跳过 0 条，第 2 页跳过 `page_size` 条，第 3 页跳过 `2 * page_size` 条……

**`.offset(skip)`**

跳过前 `skip` 条记录，等价于 SQL 的 `OFFSET`。

**`.limit(page_size)`**

最多返回 `page_size` 条记录，等价于 SQL 的 `LIMIT`。

**示例：** 访问 `/book/get_books/list?page=2&page_size=2`，跳过前 2 条，返回第 3、4 条记录。

---

### 3.13 新增数据 `db.add()` 与自动补号

```python
class BookBase(BaseModel):
    id: int | None = None   # 可选：不传则自动分配最小的空闲 id（自动补号）
    bookname: str
    author: str
    price: float
    publisher: str

@app.post("/book/add_book")
async def add_book(book: BookBase, db: AsyncSession = Depends(get_database)):
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
```

**`model_dump()`**

把 Pydantic 模型对象转换为普通字典，便于按 `data["字段"]` 读取/修改字段。这里先把请求体 `book` 转成字典 `data`，后面用它构造 ORM 对象。

**`Book(**data)`**

用 `**` 把字典展开为关键字参数传给 `Book` 构造函数，一步创建 ORM 对象，等价于 `Book(bookname=..., author=..., price=..., publisher=...)`。

**`db.add(对象)` 与 `await db.commit()`**

`db.add()` 把新对象加入会话（还没有写入数据库）；`await db.commit()` 提交事务，新增记录才真正落盘。两条缺一不可。

**自动补号逻辑：**

新增时若不传 `id`，找出当前最小的空闲 id（复用被删除过的编号，避免编号越加越大）：

- `select(Book.id).order_by(Book.id)` 查出已占用的全部 id，升序排列；
- `next_id` 从 1 开始：遇到连续存在的 id 就 `+1`，遇到第一个空缺就 `break` 停下，该空缺即最小空闲 id。

**请求示例：**

```text
POST /book/add_book
请求体：
{
    "bookname": "三国演义",
    "author": "罗贯中",
    "price": 59.9,
    "publisher": "人民文学出版社"
}
```

不传 `id` 时后端自动分配编号并返回新增的记录（含自动生成的 `id`）。

---

### 3.14 更新数据 PUT 与对象属性修改

```python
class BookUpdate(BaseModel):
    id: int
    bookname: str
    author: str
    price: float
    publisher: str

@app.put("/book/up_date_book/{book_id}")
async def up_data_book(book_id: int, data: BookUpdate, db: AsyncSession = Depends(get_database)):
    db_book = await db.get(Book, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="未找到此书")

    db_book.bookname = data.bookname
    db_book.author = data.author
    db_book.price = data.price
    db_book.publisher = data.publisher

    await db.commit()
    return db_book
```

**`@app.put(路径)`**

PUT 路由装饰器，语义为"更新资源"。对应 1.2 中"更新数据"的 HTTP 方法。

**更新三步：**

1. **定位记录**：`await db.get(Book, book_id)` 按路径参数 `book_id` 查出目标记录（3.10）；
2. **判空**：查不到（返回 `None`）则抛 404，避免对不存在的记录做无效修改；
3. **改属性 + 提交**：直接给对象字段赋新值（如 `db_book.bookname = data.bookname`），`await db.commit()` 时写入数据库。

**关键点：** 修改 ORM 对象属性后无需手动执行 UPDATE 语句，SQLAlchemy 会自动跟踪字段变化，在 `commit` 时生成更新 SQL 并只更新发生变化的字段。

**请求示例：**

```text
PUT /book/up_date_book/1
请求体：
{
    "id": 1,
    "bookname": "水浒传",
    "author": "施耐庵",
    "price": 39.9,
    "publisher": "中华书局"
}
```

若 `id` 对应的书籍不存在，返回 404 `{"detail": "未找到此书"}`。

---

### 3.15 删除数据 DELETE `db.delete()`

```python
@app.delete("/book/delete_book/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_database)):
    db_book = await db.get(Book, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="未找到此书")

    await db.delete(db_book)
    await db.commit()
    return {"msg": "删除成功"}
```

**`@app.delete(路径)`**

DELETE 路由装饰器，语义为"删除资源"。

**`await db.delete(对象)`**

把查询到的对象标记为删除，`await db.commit()` 提交后从数据库中真正删除。

**与更新相同的判空逻辑：**

先 `db.get()` 确认记录存在，不存在则抛 404，保证删除的是有效记录。

**增删改查（CRUD）小结：**

至此第 3 天已覆盖数据库的完整增删改查：

| 操作 | 接口 | 关键代码 |
|------|------|---------|
| 新增（Create） | `POST /book/add_book` | `db.add(对象)` + `await db.commit()` |
| 查询（Read） | `GET /book/...`（3.6~3.12） | `await db.execute(select(...))` |
| 更新（Update） | `PUT /book/up_date_book/{id}` | 修改对象属性 + `await db.commit()` |
| 删除（Delete） | `DELETE /book/delete_book/{id}` | `await db.delete(对象)` + `await db.commit()` |

---

## 已学知识点速查

| 类别 | 知识点 | 关键字/用法 |
|------|--------|-------------|
| 应用 | 创建应用 | `app = FastAPI()` |
| 路由 | GET / POST 路由 | `@app.get(路径)` / `@app.post(路径)` |
| 异步 | 异步函数 | `async def` |
| 路径参数 | URL 路径传参 | `/{参数名}` |
| 类型标注 | 参数类型声明 | `参数: str/int/float/bool` |
| 字符串 | 格式化字符串 | `f"文本{变量}"` |
| 校验 | 路径参数校验 | `Path(..., ge=, le=, min_length=, max_length=, description=)` |
| 校验 | 查询参数校验 | `Query(默认值, le=, ...)` |
| 模型 | 数据模型 | `class X(BaseModel)` |
| 模型 | 字段配置 | `Field(default=, min_length=, max_length=)` |
| 请求 | 请求体模型 | `def 接口(参数: 模型)` |
| 响应 | HTML 响应 | `response_class=HTMLResponse` |
| 文件 | 读取文件 | `with open(路径, "r", encoding="utf-8") as f` |
| 响应 | 文件响应 | `response_class=FileResponse` / `FileResponse(路径)` |
| 响应 | 响应模型过滤 | `response_model=模型` |
| 异常 | 手动抛错 | `raise HTTPException(status_code=404, detail="信息")` |
| 中间件 | HTTP 中间件 | `@app.middleware("http")` + `await call_next(request)` |
| 依赖注入 | 复用公共参数 | `参数 = Depends(依赖函数)` |
| ORM | 异步引擎 | `create_async_engine(连接串, echo=, pool_size=, max_overflow=)` |
| ORM | 声明式基类 | `class Base(DeclarativeBase)` |
| ORM | 字段类型标注 | `Mapped[类型]` |
| ORM | 字段映射 | `mapped_column(类型, primary_key=, comment=, default=)` |
| ORM | 指定表名 | `__tablename__ = "表名"` |
| ORM | 建表 | `Base.metadata.create_all` + `@app.on_event("startup")` |
| ORM | 会话工厂 | `async_sessionmaker(bind=, class_=, expire_on_commit=)` |
| ORM | 会话依赖 | `async def 依赖(): ... yield session`（自动提交/回滚/关闭） |
| ORM | 查询所有 | `await db.execute(select(模型))` + `.scalars().all()` |
| ORM | 条件过滤 | `.where(模型.字段 比较值)` |
| ORM | 按参数精确查询 | `.where(模型.字段 == 路径参数)` |
| ORM | 模糊查询 | `.like("曹%")` |
| ORM | 主键查询 | `await db.get(模型, 主键值)` |
| ORM | 聚合函数 | `func.count/max/sum/avg(字段)` + `.scalar()` |
| ORM | 分页 | `.offset(跳过条数).limit(每页条数)` |
| ORM | 单条结果 | `.scalar_one_or_none()` |
| 模型 | 模型转字典 | `model_dump()` |
| ORM | 判断记录是否存在 | `await db.get(模型, 主键)`（查不到返回 `None`） |
| ORM | 新增记录 | `db.add(对象)` + `await db.commit()` |
| ORM | 更新记录 | 修改对象属性 + `await db.commit()` |
| ORM | 删除记录 | `await db.delete(对象)` + `await db.commit()` |

---

## 附录 A：专业术语详解

> 汇总笔记中出现的专业术语，按类别整理。每个术语说明它**实现了什么功能**以及**解决了什么问题**。
> 后续新增知识点时，请在对应类别下同步补充。

### A.1 框架与运行环境

| 术语 | 实现了什么功能 | 解决了什么问题 |
|------|---------------|---------------|
| **FastAPI** | 一个 Python Web 框架：用少量代码定义 HTTP 接口，并自动生成 Swagger 交互式接口文档 | 传统框架代码量大、文档与代码易不一致、参数校验需手写的问题 |
| **Uvicorn** | Python 的 ASGI 服务器，负责启动应用、监听端口并处理每个 HTTP 请求（启动命令如 `uvicorn main:app --reload`） | 让 FastAPI 应用真正跑起来、对外提供服务（FastAPI 本身不含服务器） |
| **ASGI** | Python 异步服务器网关接口，是 Web 服务器与 Web 应用之间的通信规范 | 让支持异步的应用（如 FastAPI）能接入各类服务器 |
| **API** | 程序之间的调用接口（本笔记中指 HTTP 接口：一个"方法+地址"对应一个功能） | 前端或其他程序无需了解后端内部实现，即可通过标准 HTTP 请求调用后端能力 |
| **HTTP** | Web 通信协议，规定请求方法（GET/POST/PUT/DELETE）与状态码等标准 | 统一了客户端与服务器之间的通信格式，让不同系统可以互通 |
| **HTTP 方法** | GET 获取、POST 提交、PUT 更新、DELETE 删除，各自表示一种操作语义 | 用统一的方法名表达操作意图，避免自定义规则 |
| **RESTful** | 一种接口设计风格：用"资源路径 + HTTP 方法"描述对资源的操作 | 让接口风格统一、语义清晰，便于维护与调用 |
| **端点（Endpoint）** | 一个具体的"方法 + URL"接口，如 `GET /book/{id}` | 让请求能精确命中唯一一个处理逻辑 |
| **服务器（Server）** | 运行在后台、持续监听端口并提供服务的程序 | 响应客户端请求、返回数据 |
| **客户端（Client）** | 发起请求的一方，如浏览器、手机 App、Postman | 让用户/程序能访问服务器提供的服务 |
| **前端 / 后端** | 前端负责展示与交互（浏览器页面），后端负责业务逻辑与数据（本笔记代码） | 把界面与逻辑分离，各司其职、便于协作 |
| **接口文档** | FastAPI 根据代码自动生成的文档（默认 `/docs`，基于 OpenAPI/Swagger） | 文档与代码不一致、手动维护文档耗时的问题 |

### A.2 数据与类型

| 术语 | 实现了什么功能 | 解决了什么问题 |
|------|---------------|---------------|
| **JSON** | 一种文本数据交换格式，形如 `{"键": "值"}` | 让 Python 对象与网络传输之间用统一、可读的文本表示数据 |
| **字符串（String）** | 用引号包裹的文本类型，如 `"abc"` | 表示名称、消息等文字数据 |
| **整数（Integer）** | 正整数/负整数/零，如 `3`、`-1` | 表示数量、ID 等数值数据 |
| **浮点数（Float）** | 带小数的数值，如 `3.14` | 表示价格、比例等非整数数值 |
| **布尔值（Boolean）** | 只有 `True`/`False` 两种取值 | 表示"是/否"等二值状态 |
| **字典（dict）** | 键值对集合，如 `{"id": 1}`，用 `字典["键"]` 取值 | 组织有名称的多个相关数据 |
| **列表（list）** | 有序的元素集合，如 `[1, 2, 3]`，用下标 `列表[0]` 访问 | 存放一组同类数据、便于遍历 |
| **类型标注（Type Annotation）** | 用 `参数: 类型` 声明数据类型 | FastAPI 据此自动校验、类型转换并生成接口文档 |
| **序列化（Serialization）** | 把 Python 对象转换为 JSON 等可传输文本 | Python 对象不能直接传输，需要转换成文本 |
| **反序列化（Deserialization）** | 把接收到的 JSON 文本还原成 Python 对象/模型 | 客户端发来的文本无法直接当对象使用 |

### A.3 请求与响应

| 术语 | 实现了什么功能 | 解决了什么问题 |
|------|---------------|---------------|
| **路径参数** | URL 路径中 `{xxx}` 的动态部分，运行时取实际值 | 用同一接口处理不同参数，无需为每个取值单独写路由 |
| **查询参数** | URL `?` 后的键值对，如 `?skip=20&limit=5` | 不修改路径即可传递分页、过滤等可选条件 |
| **请求体（Body）** | POST 等请求携带的结构化数据 | 让客户端把注册信息等结构化数据传给后端 |
| **请求（Request）** | 封装客户端发来的一切信息（地址、方法、参数、请求体） | 让后端能读取调用方发来的数据 |
| **响应（Response）** | 服务器返回给客户端的数据 | 统一返回格式，客户端易于解析 |
| **response_model** | 按模型过滤并序列化响应数据 | 防止多余/敏感字段泄漏给客户端，保证返回结构稳定 |
| **response_class** | 指定接口的响应类型 | 默认只能返回 JSON，需要返回网页/文件时的扩展问题 |
| **HTMLResponse** | 把 HTML 字符串作为网页返回 | 需要后端渲染页面/返回静态网页，而非 JSON |
| **FileResponse** | 把服务器本地文件流式返回给客户端 | 大文件一次性载入内存导致内存溢出、无法传文件 |
| **静态文件（Static File）** | 图片、视频、CSS、JS 等无需后端计算、直接返回的本地文件 | 让浏览器能加载多媒体与样式资源 |
| **流式响应（Streaming）** | 将数据分块、逐段发送给客户端 | 大文件/大响应整体占满内存 |
| **状态码（Status Code）** | HTTP 响应的三位数字，标识结果类别（200/404/422/500...） | 客户端不解析内容即可判断请求结果 |
| **URL** | 网络资源地址，如 `http://localhost:8000/book/1?limit=5` | 唯一确定"从哪台服务器、取哪个资源" |
| **分页（Pagination）** | 通过 `skip`（跳过条数）与 `limit`（返回条数）切分数据 | 数据量过大时一次返回过多、传输与渲染卡顿 |

### A.4 核心机制

| 术语 | 实现了什么功能 | 解决了什么问题 |
|------|---------------|---------------|
| **装饰器（Decorator）** | `@xxx` 语法，给函数附加额外功能而不修改函数内部代码 | 把"路由注册"等横切逻辑与业务逻辑分离 |
| **路由（Route）** | "方法 + URL" 与处理函数之间的映射关系 | 客户端请求某个地址时能准确找到对应处理逻辑 |
| **Pydantic** | 数据校验与序列化库，自动完成校验、类型转换、转 JSON | 手动校验、类型转换繁琐且易遗漏 |
| **BaseModel** | Pydantic 的模型基类，继承后字段自动具备校验/转换/序列化能力 | 用声明式写法描述数据结构，代替手写 if 判断 |
| **Field()** | 字段配置组件，为字段附加默认值、长度/范围校验、说明文字 | 校验规则无法内联在类型标注中、且无法携带默认值与描述 |
| **Path()** | 路径参数校验组件，给 URL 路径中的 `{参数}` 加校验规则 | 路径参数无法声明校验规则、不合法请求会进入接口内部 |
| **Query()** | 查询参数校验组件，给 `?` 后的查询参数加校验规则与默认值 | 查询参数类型与范围的规范校验、未传时需有默认值 |
| **校验（Validation）** | 自动检查数据是否符合规则，失败返回 422 | 手写 if 判断校验的繁琐与遗漏 |
| **HTTPException** | HTTP 错误类，可携带状态码与详情主动抛出 | 错误响应不标准、只能靠返回特殊值表示失败 |
| **异常（Exception）** | 程序运行中出现的错误情况，可被捕获或主动抛出 | 让错误能被识别、定位和按规则处理 |
| **中间件（Middleware）** | 在请求进入、响应返回时统一执行的拦截层 | 日志、鉴权、统计耗时等横切需求在每个接口重复编写 |
| **拦截器（Interceptor）** | 与中间件类似的拦截概念，在请求前后统一处理 | 在不侵入每个接口的前提下统一做横切处理 |
| **依赖注入（Dependency Injection）** | 由框架准备好依赖并自动传入函数的设计模式 | 高耦合、公共逻辑无法复用 |
| **Depends()** | 依赖注入组件，把公共参数/逻辑提取为独立函数并注入到接口 | 多个接口重复定义相同参数与校验、后期难以统一修改 |
| **回调函数（Callback）** | 作为参数传给别的函数、由对方在适当时机调用的函数（如 `call_next`） | 让框架能在特定时机执行自定义逻辑 |
| **上下文管理器（Context Manager）** | `with` 语句背后的机制，进入/退出时自动执行特定逻辑 | 文件、连接等资源忘记关闭导致泄漏 |
| **默认值（Default）** | 参数未传入时使用的预设值 | 让参数可选、接口更易用 |
| **必填 / 可选参数** | 无默认值的参数必填，有默认值的参数可选 | 明确告知调用方哪些参数必须提供 |
| **Ellipsis（`...`）** | Python 内置字面量，本笔记中表示"必填、无默认值" | 区分必填参数与可选参数 |
| **元数据（Metadata）** | 描述数据的数据，如 `description`、`title` | 让字段/接口带有说明信息，供文档展示 |

### A.5 并发与工程概念

| 术语 | 实现了什么功能 | 解决了什么问题 |
|------|---------------|---------------|
| **异步 / 协程（Async/Coroutine）** | `async def` 定义、`await` 等待的并发模型，I/O 等待时让出控制权 | 单个耗时请求阻塞整个服务器、并发能力低 |
| **事件循环（Event Loop）** | 异步程序的核心调度器，不断"取任务→执行→遇等待就切换" | 让大量 I/O 任务在单线程内交错执行、提高吞吐 |
| **并发（Concurrency）** | 多个任务交替执行，看似同时进行 | 在高延迟 I/O（数据库、网络）场景下提升整体效率 |
| **f-string** | 格式化字符串，用 `{变量}` 直接把值插入到字符串中 | 字符串拼接繁琐、数字需手动转字符串 |
| **相对路径 / 绝对路径** | 相对当前目录的路径（`./files/MC.mp4`）与从盘符开始的完整路径 | 跨机器/跨目录引用文件时路径不失效 |
| **作用域（Scope）** | 变量可被访问的范围（函数内/模块内） | 避免变量互相干扰、命名冲突 |

### A.6 ORM 与数据库

| 术语 | 实现了什么功能 | 解决了什么问题 |
|------|---------------|---------------|
| **ORM** | 对象关系映射：用 Python 类（模型）描述数据表，操作对象即操作数据库记录 | 手写 SQL 繁琐、易错、与 Python 代码割裂 |
| **SQLAlchemy** | Python 的 ORM 框架（本笔记用其异步组件操作 MySQL） | 让数据库操作以 Python 对象方式完成，同时支持同步/异步 |
| **异步引擎（AsyncEngine）** | `create_async_engine` 创建，负责管理连接、执行 SQL | 让数据库操作在事件循环中执行，不阻塞服务器 |
| **连接池（Connection Pool）** | 预先创建并复用的一批数据库连接（`pool_size`/`max_overflow` 控制大小） | 每次请求都重新连接数据库，耗时高、连接数爆炸 |
| **会话（Session）** | 与数据库交互的工作单元：查询、增删改、事务都通过它执行 | 把"连接"与"业务操作"解耦，事务边界清晰 |
| **会话工厂（sessionmaker）** | 生成会话的工厂，统一会话配置（`async_sessionmaker`） | 无需每次手写创建/配置会话的代码 |
| **声明式基类（DeclarativeBase）** | 所有模型的公共父类，自动收集模型并生成表结构 | 避免手写建表 SQL，模型定义即表结构 |
| **模型（Model）** | 与数据表一一对应的 Python 类（如 `Book`） | 用面向对象的方式操作数据表 |
| **数据表（Table）** | 数据库中的二维表，`__tablename__` 指定表名 | 结构化存储一类数据 |
| **字段 / 列（Column）** | 表中一列，由 `mapped_column` 定义类型与约束 | 规定一行数据包含哪些属性 |
| **主键（Primary Key）** | 唯一标识一行数据的字段（`primary_key=True`） | 精准定位单条记录，防止数据重复 |
| **事务（Transaction）** | 一组要么全部成功、要么全部回滚的数据库操作 | 多步操作中途出错导致数据不完整 |
| **提交（Commit）** | `session.commit()` 将事务中的更改写入数据库 | 让更改生效并持久化 |
| **回滚（Rollback）** | `session.rollback()` 撤销事务中未提交的更改 | 出错时恢复原状，保证数据一致性 |
| **查询（select）** | `select(模型)` 构建查询语句 | 取代手写 SELECT SQL，更安全不易出错 |
| **结果集（Result）** | `db.execute()` 返回的结果对象，用 `.scalars()` 等提取 | 承载并解析查询结果 |
| **聚合函数（Aggregate）** | `func.count/max/sum/avg` 对多行做汇总计算 | 统计总数、最值、求和、平均值 |
| **模糊查询（LIKE）** | `.like("曹%")` 按部分内容匹配 | 精确匹配无法处理"以…开头/包含"类查询 |
| **分页（offset/limit）** | `.offset(n).limit(m)` 跳过 n 条、取 m 条 | 数据量大时一次返回全部导致卡顿 |
| **启动事件（Startup Event）** | `@app.on_event("startup")` 在应用启动时执行的逻辑 | 启动时自动建表/初始化，无需手动执行 SQL |
| **MySQL** | 开源关系型数据库，通过 `mysql+aiomysql` 异步驱动连接 | 持久化存储业务数据 |
| **DDL** | 定义数据库结构的语句（建表等，如 `create_all`） | 让表结构用代码声明、可纳入版本管理 |
| **DML** | 操作数据的语句（增删改查） | 日常读写数据 |

---

## 附录 B：关键字详解

> 分五类：**Python 关键字**、**FastAPI/Pydantic 关键字参数**、**常用运算符与符号**、**常用内置函数与文件方法**、**SQLAlchemy 常用参数与方法**。
> 每个都说明**规范用法**与**能处理什么问题**。带（拓展）标记的是后续学习会用到、目前尚未出现的用法。

### B.1 Python 关键字

| 关键字 | 规范用法 | 能处理什么问题 |
|--------|---------|---------------|
| `from` | `from 包 import 组件`，只导入需要的部分 | 避免整包引入造成命名空间污染、内存浪费 |
| `import` | `import 模块`，使用时用 `模块.成员` 访问 | 复用别人写好的功能，不用重复造轮子 |
| `class` | `class 类名(父类):`，类名用大驼峰，类体缩进 | 把相关的数据字段和行为封装成整体（如请求/响应模型） |
| `def` | `def 函数名(参数):`，函数名小写+下划线，函数体缩进 | 把一段可复用的逻辑封装成函数，避免重复代码 |
| `async` | `async def 函数名():`，内部配合 `await` 使用 | 定义异步函数，I/O 等待时让出执行权，提升并发处理能力 |
| `await` | `await 异步操作`，只能写在 `async` 函数里 | 等待异步操作完成并取得结果，期间不阻塞服务器 |
| `return` | `return 值`，函数执行到此立即结束并返回 | 把计算结果交回调用方；在 FastAPI 中即响应内容 |
| `with` | `with 表达式 as 变量:` 后缩进使用 | 自动管理资源，代码块结束自动清理（如关闭文件） |
| `as` | `... as 名字`，给对象起别名 | 让后续代码用简短名字引用同一对象 |
| `raise` | `raise HTTPException(status_code=404, detail="...")` | 检测到异常情况时主动终止并抛出标准错误响应 |
| `in` / `not in` | `值 in 容器` / `值 not in 容器`，返回布尔值 | 判断某个值是否存在于/不存在于列表、字典等容器中 |
| `if` / `elif` / `else` | `if 条件:` / `elif 条件:` / `else:` 分支缩进 | 按条件走不同逻辑分支，实现判断 |
| `for` | `for 变量 in 容器:` 遍历容器 | 依次处理容器中的每个元素 |
| `while` | `while 条件:`，条件为真时重复执行 | 处理循环次数不定的重复逻辑 |
| `break` | 写在循环体内 | 立即结束整个循环 |
| `continue` | 写在循环体内 | 跳过本次循环、直接进入下一次 |
| `and` / `or` / `not` | 逻辑运算"且 / 或 / 取反"，如 `x > 0 and x < 10` | 组合多个条件，表达复杂判断逻辑 |
| `True` / `False` | 布尔值本身，作判断结果或直接作条件 | 表示真假状态 |
| `None` | 表示"空值、没有东西" | 区分"无值"与"0/空字符串"等有值但为空的场景 |
| `pass` | 占位语句，什么都不做 | 先搭好结构、逻辑后续再填时避免语法错误 |
| `try` / `except` | `try:` 里放可能出错的代码，`except:` 捕获并处理 | 在程序崩溃前拦截异常、优雅降级 |
| `...`（Ellipsis） | 写在 `Path(...)`/`Query(...)` 的参数位置 | 明确表示"该参数必填、无默认值"，语义清晰可读 |

### B.2 FastAPI / Pydantic 关键字参数

| 关键字 | 规范用法 | 能处理什么问题 |
|--------|---------|---------------|
| `ge` | `ge=1`，要求数值 ≥ 1 | 校验数值下限，防止非法小值（如页码 < 1） |
| `gt` | `gt=1`，要求数值 > 1 | 校验必须大于某值的场景 |
| `le` | `le=100`，要求数值 ≤ 100 | 校验数值上限，防止非法大值（如一次取 10 万条） |
| `lt` | `lt=100`，要求数值 < 100 | 校验必须小于某值的场景 |
| `min_length` | `min_length=2` | 校验字符串最短长度，防空值/过短输入 |
| `max_length` | `max_length=10` | 校验字符串最长长度，防超长输入 |
| `min` / `max` | `Field(min=0)`、`Query(max=100)`（拓展） | 与 `ge`/`le` 类似的数值范围约束 |
| `pattern` | `Field(pattern=r"^1\d{10}$")`，正则表达式校验（拓展） | 校验手机号、邮箱等有固定格式的字符串 |
| `description` | `description="书籍ID取值范围1-100"` | 在自动生成的接口文档中显示说明，便于他人正确调用 |
| `title` | `Field(title="用户名")`（拓展） | 给字段一个简短标题，让文档更易读 |
| `default` | `Query(0, ...)` 中的 `0` | 未传该参数时使用默认值，让参数变为可选 |
| `example` | `Field(example="张三")`（拓展） | 在文档中展示示例值，方便他人参照调用 |
| `exclude` / `include` | `model_dump(exclude={"secret"})`（拓展） | 按需控制序列化结果中包含哪些字段 |
| `model_dump` | `book.model_dump()` | 把模型对象转成普通字典，便于读取字段或传给 ORM 构造对象 |
| `status_code` | `status_code=404` | 指定/抛出 HTTP 状态码，语义化表达请求结果 |
| `detail` | `detail="不存在"` | 给出错误的具体原因，返回给客户端展示 |
| `response_model` | `response_model=News` | 过滤响应中未声明的字段，防止敏感信息泄漏 |
| `response_class` | `response_class=HTMLResponse` | 切换响应类型（网页、文件、JSON 等） |

### B.3 常用运算符与符号

| 符号 | 规范用法 | 能处理什么问题 |
|------|---------|---------------|
| `=` | 赋值：`name = "小明"` | 把值存入变量 |
| `==` | 相等判断：`if id == 1:` | 判断两个值是否相等 |
| `!=` | 不等判断：`if x != 0:` | 判断两个值是否不相等 |
| `>` `<` `>=` `<=` | 大小比较：`id > 100` | 比较数值大小，配合 `if` 使用 |
| `+` | 数值相加 / 字符串拼接：`"Hello " + name` | 数值计算与字符串连接 |
| `{}` | 路径参数、字典、f-string：`/book/{id}`、`{"id": 1}`、`f"{name}"` | 同一符号在不同语境表示动态参数/键值集合/插入值 |
| `:` | 类型标注、字典键值分隔、语句结尾：`name: str`、`{"id": 1}`、`def f():` | 声明类型、组织字典、标识代码块 |
| `f` | 字符串前缀：`f"Hello {name}"` | 在字符串中直接插入变量值 |
| `?` / `&` | URL 中分隔查询参数：`/news/list?skip=20&limit=5` | 在地址中传递多个键值参数 |
| `#` | 注释：`# 这是一行注释` | 说明代码含义，`#` 后的内容不执行 |
| `.` | 成员访问：`f.read()`、`app.get` | 调用对象的属性与方法 |

### B.4 常用内置函数与文件方法

| 名称 | 规范用法 | 能处理什么问题 |
|------|---------|---------------|
| `open()` | `open("index.html", "r", encoding="utf-8")` | 打开文件，通常配合 `with ... as` 使用 |
| `f.read()` | `f.read()` | 一次性读取文件全部内容 |
| `print()` | `print("中间件1 start")` | 把内容输出到控制台，用于调试观察 |
| `str()` / `int()` / `float()` / `bool()` | `int("5")`、`str(3)` | 强制类型转换 |
| `len()` | `len("abc")`、`len([1, 2, 3])` | 获取字符串/容器长度 |
| `range()` | `for i in range(10):`（拓展） | 生成整数序列，配合 `for` 遍历固定次数 |

### B.5 SQLAlchemy 常用参数与方法

| 关键字 | 规范用法 | 能处理什么问题 |
|--------|---------|---------------|
| `create_async_engine` | `create_async_engine(URL, echo=True, pool_size=10, max_overflow=20)` | 创建异步数据库引擎，统一管理连接 |
| `echo` | `echo=True` | 控制台打印 SQL 日志，方便调试 |
| `pool_size` | `pool_size=10` | 设置连接池常驻连接数，避免频繁建连 |
| `max_overflow` | `max_overflow=20` | 高峰期连接池外最多可临时创建的连接数 |
| `async_sessionmaker` | `async_sessionmaker(bind=..., class_=AsyncSession, expire_on_commit=False)` | 创建会话工厂，统一生成异步会话 |
| `bind` | `bind=async_engine` | 将会话工厂/会话绑定到指定引擎 |
| `class_` | `class_=AsyncSession` | 指定会话类为异步会话 |
| `expire_on_commit` | `expire_on_commit=False` | 提交事务后仍可读取对象字段 |
| `Mapped` | `Mapped[int]`、`Mapped[str]` | 声明字段的 Python 类型，供类型检查与映射 |
| `mapped_column` | `mapped_column(String(255), comment="书名")` | 把模型属性映射为数据库字段，配置类型与约束 |
| `primary_key` | `primary_key=True` | 将字段设为主键 |
| `comment` | `comment="书名"` | 为字段添加注释，便于查看表结构 |
| `default` | `default=func.now()` | 设置 ORM 层字段默认值 |
| `insert_default` | `insert_default=func.now()` | 插入数据时由数据库写入默认值 |
| `onupdate` | `onupdate=func.now()` | 更新数据时自动刷新字段值 |
| `func.now()` | `mapped_column(DateTime, default=func.now())` | 取数据库当前时间，时间由数据库统一生成 |
| `String` / `Integer` / `Float` / `DateTime` | `mapped_column(String(255))` | 指定字段对应的数据库类型 |
| `__tablename__` | `__tablename__ = "book"` | 指定模型对应的数据表名 |
| `yield` | `yield session`（生成器依赖函数中） | 在接口前后分别执行准备与清理逻辑（配合 commit/rollback/close） |
| `select` | `select(Book).where(...)` | 构建查询语句 |
| `.where()` | `.where(Book.id >= 2)`、`.where(Book.id == book_id)` | 为查询添加过滤条件（常量或路径参数） |
| `.like()` | `.where(Book.author.like("曹%"))` | 模糊匹配，`%` 匹配任意多个字符 |
| `.offset()` / `.limit()` | `.offset(skip).limit(page_size)` | 分页：跳过与限制条数 |
| `.scalars()` | `result.scalars().all()` | 把结果按模型对象逐行提取 |
| `.scalar()` | `result.scalar()` | 取单个标量值（如聚合结果） |
| `.scalar_one_or_none()` | `result.scalar_one_or_none()` | 取至多一条结果，无则返回 `None` |
| `db.get()` | `await db.get(Book, 1)` | 按主键直接查询 |
| `db.add()` | `db.add(book_obj)` | 把对象加入会话，用于新增记录 |
| `db.delete()` | `await db.delete(db_book)` | 删除对象对应的记录 |
| `.commit()` / `.rollback()` / `.close()` | `await session.commit()` | 提交 / 回滚 / 关闭会话 |
| `create_all` | `Base.metadata.create_all` | 按模型定义创建缺失的数据表 |
| `run_sync` | `await conn.run_sync(Base.metadata.create_all)` | 在异步连接中执行同步操作 |
| `@app.on_event("startup")` | `@app.on_event("startup")` | 注册应用启动时执行的回调 |

---

## 附录 C：关键字分类总览（按功能角色）

> 附录 B 从"技术来源"逐类详解关键字，本附录换一个视角：按关键字在**一次 HTTP 请求从进入应用到返回响应的流程中所承担的角色**分类，方便"想做什么 → 直接找到对应关键字"。
>
> 流程主线：**应用搭建 → 请求接收与校验 → 业务处理（依赖 / 数据库）→ 异常处理 → 返回响应**。表中"所属天"指该关键字在正文第几天的代码中出现，详细用法见附录 B 对应小节。

### C.1 应用构建与路由（搭建应用、注册接口）

| 关键字 / 用法 | 一句话功能 | 所属天 |
|------|------|------|
| `from 包 import 组件` / `import 模块` | 导入所需组件 | 第 1 天 |
| `app = FastAPI()` | 创建应用对象 | 第 1 天 |
| `@app.get()` / `@app.post()` / `@app.put()` / `@app.delete()` | 注册路由接口 | 第 1 天 |
| `async def 接口()` | 定义异步接口函数 | 第 1 天 |
| `@app.middleware("http")` | 注册请求中间件 | 第 2 天 |
| `@app.on_event("startup")` | 注册应用启动时执行的回调 | 第 3 天 |

### C.2 请求数据接收与校验（声明结构、校验参数、默认值）

| 关键字 / 用法 | 一句话功能 | 所属天 |
|------|------|------|
| `参数: str` / `int` / `float` / `bool` | 类型标注，自动校验与转换 | 第 1 天 |
| `class 模型(BaseModel)` | 定义请求/响应数据模型 | 第 1 天 |
| `Field(默认值, 规则...)` | 配置模型字段 | 第 1 天 |
| `Path(...)` / `Query(...)` | 路径/查询参数校验组件 | 第 1 天 |
| `ge` / `gt` / `le` / `lt` | 数值范围校验 | 第 1 天 |
| `min_length` / `max_length` | 字符串长度校验 | 第 1 天 |
| `default` | 未传参时使用的默认值 | 第 1/3 天 |
| `...`（Ellipsis） | 必填参数标记 | 第 1 天 |
| `Mapped[类型]` | ORM 字段的 Python 类型标注 | 第 3 天 |
| `mapped_column(类型, 规则...)` | ORM 字段映射为数据库列 | 第 3 天 |
| `primary_key` / `comment` | 设主键 / 加字段注释 | 第 3 天 |
| `insert_default` / `onupdate` | 插入默认值 / 更新时自动刷新 | 第 3 天 |

### C.3 依赖注入与复用（公共逻辑抽出复用）

| 关键字 / 用法 | 一句话功能 | 所属天 |
|------|------|------|
| `参数 = Depends(依赖函数)` | 把依赖函数返回值注入接口 | 第 2 天 |
| `async def 依赖(): ... yield ...` | 生成器依赖（前后准备与清理，如数据库会话） | 第 3 天 |

### C.4 业务逻辑与流程控制（判断、循环、异步）

| 关键字 / 用法 | 一句话功能 | 所属天 |
|------|------|------|
| `if` / `elif` / `else` | 条件分支 | 第 2 天 |
| `in` / `not in` | 判断值是否在容器中 | 第 2 天 |
| `and` / `or` / `not` | 逻辑运算 | — |
| `for` / `while` / `break` / `continue` | 循环与循环跳转 | — |
| `await` | 等待异步操作完成 | 第 2/3 天 |

### C.5 响应与输出（把结果交回客户端）

| 关键字 / 用法 | 一句话功能 | 所属天 |
|------|------|------|
| `return 数据` | 返回结果（自动序列化为 JSON） | 第 1 天 |
| `response_model=模型` | 按模型过滤响应字段 | 第 2 天 |
| `response_class=HTMLResponse` | 返回网页 HTML | 第 2 天 |
| `response_class=FileResponse` / `FileResponse(路径)` | 返回本地静态文件 | 第 2 天 |
| `f"文本{变量}"` | 字符串格式化插入变量 | 第 1 天 |
| `print()` | 控制台输出（调试观察） | 第 2 天 |

### C.6 异常与错误处理（失败时的标准处理）

| 关键字 / 用法 | 一句话功能 | 所属天 |
|------|------|------|
| `raise HTTPException(status_code=, detail=)` | 主动抛出 HTTP 错误响应 | 第 2 天 |
| `try` / `except` / `finally` | 捕获异常、出错回滚、最终清理 | 第 3 天 |

### C.7 资源与上下文管理（用完自动释放）

| 关键字 / 用法 | 一句话功能 | 所属天 |
|------|------|------|
| `with 资源 as 变量:` | 代码块结束自动释放资源 | 第 2 天 |
| `async with 资源 as 变量:` | 异步资源自动释放（连接、会话） | 第 3 天 |
| `open(路径, "r", encoding="utf-8")` | 打开文件 | 第 2 天 |
| `f.read()` | 读取文件内容 | 第 2 天 |

### C.8 数据库 ORM（SQLAlchemy 异步操作）

| 关键字 / 用法 | 一句话功能 | 所属天 |
|------|------|------|
| `create_async_engine(URL, echo=, pool_size=, max_overflow=)` | 创建异步数据库引擎 | 第 3 天 |
| `class Base(DeclarativeBase)` | 定义模型公共基类 | 第 3 天 |
| `__tablename__ = "表名"` | 指定数据表名 | 第 3 天 |
| `DateTime` / `String(n)` / `Integer` / `Float` | 字段对应的数据库类型 | 第 3 天 |
| `async_sessionmaker(bind=, class_=, expire_on_commit=)` | 创建会话工厂 | 第 3 天 |
| `select(模型)` | 构建查询语句 | 第 3 天 |
| `.where(条件)` | 条件过滤 | 第 3 天 |
| `.like("xx%")` | 模糊匹配 | 第 3 天 |
| `.offset(n)` / `.limit(m)` | 分页跳过 / 限制条数 | 第 3 天 |
| `db.get(模型, 主键)` | 按主键查询 | 第 3 天 |
| `func.count/max/sum/avg(字段)` | 聚合计算 | 第 3 天 |
| `.scalars().all()` / `.scalar()` / `.scalar_one_or_none()` | 提取查询结果 | 第 3 天 |
| `await session.commit()` / `rollback()` / `close()` | 提交 / 回滚 / 关闭会话 | 第 3 天 |
| `Base.metadata.create_all` / `run_sync(...)` | 按模型建表 | 第 3 天 |
| `func.now()` | 取数据库当前时间 | 第 3 天 |
| `db.add(对象)` + `await db.commit()` | 新增记录 | 第 3 天 |
| 修改对象属性 + `await db.commit()` | 更新记录 | 第 3 天 |
| `db.delete(对象)` + `await db.commit()` | 删除记录 | 第 3 天 |
| `model_dump()` | 模型转字典 | 第 3 天 |

### C.9 运算符与符号（基础语法）

| 关键字 / 用法 | 一句话功能 | 所属天 |
|------|------|------|
| `=` / `==` / `!=` | 赋值 / 相等 / 不等判断 | — |
| `>` `<` `>=` `<=` | 大小比较 | — |
| `+` | 数值相加 / 字符串拼接 | — |
| `{}` | 路径参数 / 字典 / f-string | 第 1 天 |
| `:` | 类型标注 / 字典 / 代码块 | 第 1 天 |
| `f` | 格式化字符串前缀 | 第 1 天 |
| `?` / `&` | URL 查询参数分隔 | 第 1 天 |
| `#` | 单行注释 | — |
| `.` | 成员（属性/方法）访问 | — |

---

> 后续学习内容（如第 4 天认证鉴权、JWT 等）完成后，再继续补充到本文件。
