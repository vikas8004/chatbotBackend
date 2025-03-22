import bcrypt

def hash_str(data:str)->str:
    salt=bcrypt.gensalt(10)
    return bcrypt.hashpw(data.encode(),salt=salt).decode()

def verify(password:str,hash_pass:str)->bool:
    return bcrypt.checkpw(password.encode(),hash_pass.encode())