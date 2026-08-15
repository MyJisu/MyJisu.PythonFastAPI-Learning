# 使用 bcrypt 算法实现密码加密与校验：加密明文密码生成哈希存入数据库，登录时对比明文与库中哈希值
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 密码加密功能
def get_hash_password(password: str):
    return pwd_context.hash(password)


# 验证密码：verify返回值为布尔型
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
