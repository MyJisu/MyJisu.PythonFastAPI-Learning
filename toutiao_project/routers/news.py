# 路由模块
from fastapi import APIRouter, Depends, Response, Query, HTTPException
from crud import news
from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession

# 创建APIRouter实例, prefix:前缀名, tags:分组名
router = APIRouter(prefix="/api/news", tags=["news"])


# 获取新闻分类列表接口
# 接口的实现流程
# 1.模块化路由-->API接口规范文档
# 2.定义模型类-->数据库表(数据库设计文档)
# 3.在crud文件夹创建文件,封装操作数据库的方法
# 4.在路由处理函数里面调用crud封装好的方法,响应结果

# 获取新闻分类列表接口
@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    categories = await news.get_categories(db, skip, limit)
    return {
        "code": 200,
        "msg": "获取分类成功",
        "data": categories
    }


# 获取新闻列表
@router.get("/list")
async def get_news_list(
        category_id: int = Query(..., alias="categoryId"),
        # category_id：后端变量名 Query()：fastapi内置类，专门用来定义URL查询参数，...表示必填项，alias表示别名
        page: int = 1,    # 页码参数，默认为1
        page_size: int = Query(10, alias="pageSize", le=100),    # 默认每页10行 le=less equal表示最大长度
        db: AsyncSession = Depends(get_db)    # Depends注入数据库会话依赖
):
    # 思路: 处理分页规则-->查询新闻列表-->计算总量-->计算是否还有更多
    offset = (page - 1) * page_size    # 定义分页逻辑
    news_list = await news.get_news_list(db, category_id, offset, page_size)    # 调用获取新闻列表方法，查询当前页数据
    total = await news.get_news_count(db, category_id)    # 查询分类全部新闻数量
    # 判断是否存在更多
    has_more = (offset + len(news_list)) <= total    # 是否还有下页逻辑
    return {    # 返回json结构
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": has_more
        }
    }


# 获取新闻详情
@router.get("/detail")
async def get_news_detail(news_id: int = Query(..., alias="id"), db: AsyncSession = Depends(get_db)):
    # 获取新闻详情 + 浏览+1 + 相关新闻
    news_detail = await news.get_news_detail(db, news_id)    # 调用获取新闻详情方法，如果查询不到，返回null
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")    # 如果news_detail返回null，抛出404异常
    views_res = await news.increase_news_views(db, news_detail.id)    # 如果不为null，调用浏览量+1方法，
    if not views_res:    # 浏览量更新成功后views_res为1
        raise HTTPException(status_code=404, detail="新闻不存在")    # 浏览量更新失败时，抛出异常
    related_news = await news.get_related_news(db, news_detail.id, news_detail.category_id)    # 如果更新成功，执行获取相关新闻方法
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news
        }
    }
