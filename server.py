from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fast_api.fast_api import auth
import uvicorn
import colorama
from fastapi.staticfiles import StaticFiles

colorama.init()
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:9999",
    "http://localhost:5173"

]

app = FastAPI(docs_url="/api/docs", openapi_url="/api")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth, prefix="/api")

if __name__ == "__main__": uvicorn.run("server:app", host="localhost", reload=True, port=9998)