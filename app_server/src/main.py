from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import Union

app = FastAPI()


class Dupa(BaseModel):
    cipa : str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/user_tags/view")
async def add_view_tag(body: Dupa, response: Response):
    response.status_code = 204
    print("View", body)
    return


@app.post("/user_tags/buy")
async def add_buy_tag(body, response: Response):
    response.status_code = 204
    print("Buy", body)
    return
