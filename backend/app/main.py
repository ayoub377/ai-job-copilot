from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "AI JOB copilot backend ready"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
