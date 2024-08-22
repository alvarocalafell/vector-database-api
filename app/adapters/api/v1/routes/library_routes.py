from fastapi import APIRouter

router = APIRouter()

@router.get("/libraries")
def get_libraries():
    return {"message": "List of libraries"}
