# pydantic就是定义一个一个模型类，用类来说明数据应该长什么样子，每段字段该遵守什么规则
# 数据模型模块 新闻模块模型类：用面向对象的方式描述数据库表，实现代码与数据库映射，复用公共代码、统一数据表规范，简化增删改查操作
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Column, Integer, String, Index, Text, ForeignKey

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# 创建基类
class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(  # Mapped：类型注解工具，专门给数据表字段做类型标记
        DateTime,
        default=datetime.now,    # 默认值为当前时间
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间"
    )


# 新闻分类模型类
class Category(Base):
    __tablename__ = 'news_category'  # ORM 映射核心标识，类对应 MySQL 里名为news_category的表
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,    # 主键，一张表必须有且仅有一个主键
        autoincrement=True,    # 自增主键，新增分类时不用手动给 id 赋值，数据库会自动生成
        comment="分类的ID"    # 数据库字段注释
    )
    name: Mapped[str] = mapped_column(
        String(50),    # 最大50字符
        unique=True,    # 唯一约束：整张表不能出现重复的分类名
        nullable=False,    # 非空约束
        comment="分类名称"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,    # 默认值
        nullable=False,
        comment="排序"
    )

    def __repr__(self):    # Python魔法方法，控制打印对象时输出的内容
        return f"<Category(id={self.id}, name={self.name}, sort_order={self.sort_order})>"


# news模型类
class News(Base):
    __tablename__ = "news"
    # 创建索引：提升查询速度
    __table_args__ = (
        Index('fk_news_category_idx', 'category_id'),
        Index('idx_publish_time', 'publish_time'),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")
    description: Mapped[Optional[str]] = mapped_column(String(500), comment="新闻简介")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
    image: Mapped[Optional[str]] = mapped_column(String(255), comment="封面图片URL")
    author: Mapped[Optional[str]] = mapped_column(String(50), comment="作者")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('news_category.id'), nullable=False)
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="浏览量")
    publish_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="发布时间")

    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title}', views={self.views})>"
