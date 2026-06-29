from datetime import datetime, timedelta, timezone

import jwt

from config import settings

# 用于访问的：JWT令牌的有效时间
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES  # 30 minutes
#  JWT令牌的有效时间: 较长
# REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
# 加密算法
ALGORITHM = settings.ALGORITHM
# 密钥
JWT_SECRET_KEY = settings.JWT_SECRET_KEY


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    创建访问令牌
    :param data: 包含用户信息的字典
    :param expires_delta: 过期时间偏移量
    :return: 访问令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


    
