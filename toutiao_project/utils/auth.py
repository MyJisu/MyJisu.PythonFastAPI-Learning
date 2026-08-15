# 整合根据token查询用户最终返回的功能：通过数据库查询验证 token 是否有效
from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from crud import users

from config.db_conf import get_db
from starlette import status


# 从请求头提取 Bearer 令牌，校验 token 有效性，成功则返回登录用户；令牌非法直接返回 401，实现接口登录鉴权
async def get_current_user(
        authorization: str = Header(..., alias='Authorization'),
        db: AsyncSession = Depends(get_db)
):
    token = authorization.removeprefix('Bearer ').strip()
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='无效令牌')
    return user
