from datetime import datetime, timedelta
import jwt

async def create_access_token(
    data: dict, 
    private_key: str,
    algorithm: str,
    expires_delta: timedelta = timedelta(days=14),
):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded_jwt