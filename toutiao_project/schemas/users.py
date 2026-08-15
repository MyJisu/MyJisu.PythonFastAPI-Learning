from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# 用户请求类
class UserRequest(BaseModel):
    username: str
    password: str


# 用户基础信息父类
class UserInfoBase(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


# user_info对应的类，返回给前端的用户信息模型
class UserInfoResponse(UserInfoBase):
    id: int
    username: str
    model_config = ConfigDict(    # 允许使用 SQLAlchemy ORM 对象构造模型
        from_attributes=True
    )


# data数据类型，登录/注册整体响应外层模型
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias='userInfo')
    # 模型类配置
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


# 更新用户信息的模型类
class UserUpdateRequest(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None


# 修改密码模型类
class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., alias='oldPassword', description="旧密码")
    new_password: str = Field(..., min_length=6, alias='newPassword', description="新密码")
