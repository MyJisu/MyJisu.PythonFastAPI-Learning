# 路由模块
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud import users
from config.db_conf import get_db
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from utils.response import success_response
from utils.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 注册逻辑: 验证用户是否存在--> 创建用户-->生成token-->响应结果
    existing_user = await users.get_user_by_username(db, user_data.username)    # 验证用户是否存在
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user = await users.create_user(db, user_data)    # 若不存在，调用创建用户异步方法
    token = await users.create_token(db, user.id)    # 生成token登录令牌
    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    # }
    # 使用 Pydantic 响应模型组装数据，通过 Pydantic 模型规范输出
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)


# 登录接口
@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 登录逻辑：验证用户是否存在 -> 验证密码 -> 生成 Token  → 响应结果
    user = await users.authenticate_user(db, user_data.username, user_data.password)    # 验证用户是否存在
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = await users.create_token(db, user.id)    # 若存在，刷新登录令牌
    # 组装登录/注册接口最终返回给前端的数据；清洗数据库原始用户对象，屏蔽敏感信息，并且适配前后端命名风格
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功啦", data=response_data)


# 获取用户信息：查token-->功能整合成一个工具函数-->路由导入使用(依赖注入)
@router.get("/info")
async def user_info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


# 修改用户信息：验证token-->更新用户输入数据-->请求头参数-->定义pydantic-->响应结果
@router.put("/update")    # 参数：用户输入，验证token，db
async def update_user_info(user_data: UserUpdateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await users.update_user(db, user.username, user_data)
    return success_response(message="更新用户信息成功",data=UserInfoResponse.model_validate(user))


# 修改密码
@router.put("/password")
async def update_password(
        password_data: UserChangePasswordRequest,
        user: User = Depends(get_current_user),    # 把get_current_user鉴权依赖注入进来，实现接口强制登录校验，并直接拿到当前登录用户的ORM对象
        db: AsyncSession = Depends(get_db),
):
    res_change_pwd = await users.change_password(db, user, password_data.old_password, password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败")
    return success_response(message="修改密码成功")

