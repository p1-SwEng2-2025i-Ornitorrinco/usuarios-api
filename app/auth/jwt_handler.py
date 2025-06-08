from datetime import datetime, timedelta,timezone
from jose import jwt

SECRET_KEY = "secreto-seguro"
ALGORITHM = "HS256"

def signJWT(email: str):
    payload = {
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token}
