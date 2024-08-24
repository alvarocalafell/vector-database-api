from fastapi import Request

def get_vector_db(request: Request):
    return request.app.state.vector_db