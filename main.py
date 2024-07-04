from fastapi import FastAPI
from routes import database_router, item_router, user_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World "}

app.include_router(item_router)
app.include_router(user_router)
app.include_router(database_router)