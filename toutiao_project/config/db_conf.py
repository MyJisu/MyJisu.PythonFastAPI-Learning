# 数据库配置：会话工厂必须依托数据库引擎才能创建数据库会话；接口通过注入数据库依赖函数，获取独立会话实例；拿到会话后，即可执行数据库增删改查操作。
import os
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine


# 搭建数据库引擎：连接程序和数据库的通道，会话工厂依靠它生成会话，以此实现数据库交互。
ASYNC_DATABASE_URL = os.getenv(
    "ASYNC_DATABASE_URL",
    "mysql+aiomysql://root:your_password@localhost:3306/news_app?charset=utf8mb4"
)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,  # 数据库连接地址
    echo=True,  # 是否打印SQL日志
    pool_size=10,  # 连接池常驻连接数，程序启动后永久保持 10 个空闲数据库连接
    max_overflow=20,  # 连接池最大溢出连接。当 10 个常驻连接全部被占用，最多额外创建 20 个临时连接；总最大连接数 = 10+20=30
)

# 创建异步会话工厂：异步会话工厂用于统一生成数据库会话，各接口可通过该工厂获取独立会话实例，执行数据库增删改查操作。
AsyncSessionLocal = async_sessionmaker(  # async_sessionmaker是会话生成器，统一规范所有数据库会话的行为，赋值给AsyncSessionLocal
    bind=async_engine,  # 绑定刚才创建的数据库引擎
    class_=AsyncSession,  # 指定生成的会话是异步会话 AsyncSession
    expire_on_commit=False  # 就这样写就行
)


# 数据库依赖函数：通过Depends(get_db)调用，自动获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:  # 调用会话工厂，从数据库连接池中取出一条空闲链接进行连接，创建全新异步会话对象并赋值为session
        try:
            yield session  # 生成器yield的暂停/交出逻辑，函数运行到此处时暂停，把session抛出给接口函数，待进行完接口逻辑后返回下一步
            await session.commit()  # 提交接口里的新增、修改、删除操作并写入数据库
        except Exception:  # 捕获接口内所有异常
            await session.rollback()  # 回滚操作，只要报错，撤销当前会话所有未提交的数据库操作，防止半截脏数据存入数据库
            raise  # 重新抛出原异常
        finally:  # 关键字finally：无论正常还是报错都会执行
            await session.close()  # 关闭会话，将数据库链接归还连接池
