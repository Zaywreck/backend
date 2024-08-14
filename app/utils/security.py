from fastapi import Header, HTTPException, Depends

def verify_api_key(api_key: str = Header(...)):
    if api_key != "7c7f55abb883c3d4b16f69a15e0c29fc":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key