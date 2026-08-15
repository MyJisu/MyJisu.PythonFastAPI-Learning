# 增删改查
import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql.functions import user

from utils import security
from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest


# 根据用户名查询数据库
async def get_user_by_username(db: AsyncSession, username: str):    # username: str要查询的用户名
    query = select(User).where(User.username == username)
    result = await db.execute(query)    # 将构造好的查询语句提交给数据库执行
    return result.scalar_one_or_none()


# 创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):    # 用户请求类参数，包含用户名和密码
    hashed_password = security.get_hash_password(user_data.password)    # 调用bcrypt加密函数，接收前端的明文密码生成哈希密文
    user = User(username=user_data.username, password=hashed_password)    # 创建ORM实体对象
    db.add(user)    # 将对象加入到数据库会话，放到待执行队列
    await db.commit()    # 提交成功数据入库
    await db.refresh(user)    # 刷新实体
    return user


# 生成/刷新token登录令牌，登录注册时调用
async def create_token(db: AsyncSession, user_id: int):
    token = str(uuid.uuid4())  # 生成随机唯一ID，格式类似 550e8400-e29b-41d4-a716-446655440000
    expire_at = datetime.now() + timedelta(days=7)    # 设置过期时间
    query = select(UserToken).where(UserToken.user_id == user_id)    # 查询用户是否有登录令牌，有-->刷新，没有-->新增
    result = await db.execute(query)    # 将构造好的查询语句提交给数据库执行
    user_token = result.scalar_one_or_none()    # 存在返回ORM 对象，不存在返回none
    if user_token:
        user_token.token = token    # 刷新token
        user_token.expire_at = expire_at    # 刷新过期时间
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expire_at)    # 在内存构建一条新令牌实体
        db.add(user_token)    # 把实体对象放入会话缓冲区
        await db.commit()    # 提交实物
    return token


# 验证用户是否存在
async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:    # 数据库没有该用户名，直接返回none
        return None
    if not security.verify_password(password, user.password):     # 存在用户名，比较密码是否一致
        return None

    return user


# 根据token查询用户：验证token有效性-->查询用户
async def get_user_by_token(db: AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()

    if not db_token or db_token.expires_at < datetime.now():    # 数据库没有传入的token或者有效时间小于当前时间
        return None
    query = select(User).where(User.id == db_token.user_id)    # 通过 user_id 查询真正的用户信息
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 修改用户信息
async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        # values指定需要更新哪些字段以及对应的值
        # model_dump把Pydantic模型UserUpdateRequest转换成普通字典
        # **字典解包
        exclude_unset=True,    # 只保留前端本次请求主动传入赋值的字段；模型默认值、没传的字段全部剔除
        exclude_none=True    # 过滤掉字典中值等于None的键值对
    ))
    result = await db.execute(query)
    await db.commit()
    if result.rowcount == 0:    # 代表这条UPDATE SQL实际影响的数据行数
        raise HTTPException(status_code=404, detail='用户不存在')
    updated_user = await get_user_by_username(db, username)    # 更新数据库执行完成后，重新查询一次数据库，拿到最新的用户信息，赋值给 updated_user
    return updated_user


# 修改密码:验证当前密码-->新密码转密文--->修改当前密码-->响应结果
async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    if not security.verify_password(old_password, user.password):    # 校验旧密码
        return False
    hashed_new_pwd = security.get_hash_password(new_password)    # 对新密码进行hash加密
    user.password = hashed_new_pwd    # 修改密码
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True

