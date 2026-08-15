# 增删改查
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News


# 获取全部新闻分类
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):  # 传入异步数据库会话，skip，limit分别代表跳过的页数和一页的数量
    stml = select(Category).offset(skip).limit(limit)  # select(Category)：等价数据库查询语句，offset(skip).limit(limit)等价数据库分页操作行为
    result = await db.execute(stml)  # db.execute(stml)代表将stml包含的语句发送给数据库并执行
    return result.scalars().all()  # .scalars()代表只提取Category对象 .all()表示取出所有的查询结果并以list[Category]列表形式返回


# 根据分类ID查询指定新闻列表
async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0,
                        limit: int = 10):  # category_id: int指定要查询的主键ID
    stml = select(News).where(News.category_id == category_id).offset(skip).limit(
        limit)  # where等价SQL：WHERE news.category_id = 传入的分类ID
    result = await db.execute(stml)  # 同上
    return result.scalars().all()  # 同上


# 查询指定分类下的新闻数量
async def get_news_count(db: AsyncSession, category_id: int):  # category_id: int指定要查询的主键ID
    stml = select(func.count(News.id)).where(
        News.category_id == category_id)  # func：SQLAlchemy内置SQL函数工具，封装数据库原生函数 count(News.id)等价SQL：COUNT(news.id)，获取数据行数
    result = await db.execute(stml)  # 同上
    return result.scalar_one()  # scalar_one()：专门用于查询结果只有一行、只有一列的场景（本场景只返回一个数字）


# 查找新闻详情
async def get_news_detail(db: AsyncSession, news_id: int):  # news_id: int 要查询的新闻主键 ID
    stml = select(News).where(News.id == news_id)  # 同上
    result = await db.execute(stml)  # 同上
    return result.scalar_one_or_none()  # scalar_one_or_none() 查到新闻：返回News ORM 实体对象，不存在该 news_id：返回None，不会抛出异常


# 增加浏览量
async def increase_news_views(db: AsyncSession, news_id: int):  # news_id: int 要查询的新闻主键 ID
    stml = update(News).where(News.id == news_id).values(
        views=News.views + 1)  # update(News)表示更新数据  .values(views=News.views + 1)设置要更新的字段
    result = await db.execute(stml)  # 同上
    await db.commit()  # 提交事务，修改才永久保存到库中，查询操作不需要提交
    return result.rowcount > 0  # result.rowcount数字，代表这条 UPDATE 语句匹配并修改了多少行数据，若新闻存在，其等于1，弱不存在，等于0


# 获取相关新闻
async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    # news_id：当前打开的新闻 ID，查询时要排除本条新闻 category_id：当前新闻所属分类 ID，只查同分类新闻  limit: int = 5：最多返回几条相关新闻，默认 5 条
    stml = select(News).where(
        News.category_id == category_id,    # 条件1：查询同一分类
        News.id != news_id,    # 条件2：查询不同id
    ).order_by(    # SQLAlchemy ORM的排序函数
        News.views.desc(),    # 第一优先级：根据浏览量降序排序
        News.publish_time.desc()    # 第二优先级：根据发布时间倒叙排序
    ).limit(limit)    # 默认获取5条数据
    result = await db.execute(stml)    # 同上
    related_news = result.scalars().all()    # 取出全部匹配的新闻ORM对象，得到list[News]列表
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
    } for news_detail in related_news]    # # 循环遍历：依次取出related_news列表里的每一条新闻对象，临时命名为news_detail
