import jwt
from config import setting
from datetime import timedelta, datetime, timezone
from fastapi import HTTPException, status

class JWTAuthentication:
    def __init__(self):
        self.secret_key = setting.SECRET_KEY
        self.jwt_algo = setting.ALGORITHM
        self.token_expire_time = setting.ASCESS_TOKEN_EXPIRE_MINUTES
    
    def generate_token(self, data: dict, expires_time: timedelta | None = None):
        data_to_encode = data.copy()
        if expires_time:
            expires_time = datetime.now(timezone.utc) + expires_time
        else:
            expires_time = datetime.now(timezone.utc) + timedelta(minutes= self.token_expire_time)
        data_to_encode.update({"exp": expires_time})
        encoded_jwt = jwt.encode(data_to_encode, self.secret_key, self.jwt_algo)
        return encoded_jwt
    
    def verify_token(self, token: str):
        try:
            payload: dict = jwt.decode(token, self.secret_key, algorithms= [self.jwt_algo])
            email: str = payload.get("email") 
            if email is None:
                raise HTTPException(status_code= status.HTTP_502_BAD_GATEWAY, detail= "Token Missmatched!")
            return payload
        except Exception as e:
            print(e)
            return None