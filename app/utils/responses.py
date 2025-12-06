from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def success(message, data=None, status_code=200):
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({
            "status": "success",
            "message": message,
            "data": data or {}
        })
    )

def fail(message, error=None, status_code=400):
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({
            "status": "fail",
            "message": message,
            "error": error or {}
        })
    )

