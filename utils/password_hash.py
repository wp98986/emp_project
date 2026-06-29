from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()  # 推荐的密码哈希算法

DUMMY_HASH = password_hash.hash("dummypassword")  # 随机密码哈希值，用于测试和调试


def get_password_hash(password: str) -> str:
    """
    获取密码哈希值
    :param password: 密码
    :return: 密码哈希值
    """
    return password_hash.hash(password)  # 密码单向哈希 加密存储，无法解密恢复原始密码


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    :param plain_password: 明文密码
    :param hashed_password: 哈希后的密码
    :return: 是否验证成功
    """
    return password_hash.verify(plain_password, hashed_password)
