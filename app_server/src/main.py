from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel, Field
from typing import Union

import operator

app = FastAPI()


class ProductInfo(BaseModel):
    product_id: str = Field(min_length=1)
    brand_id: str = Field(min_length=1)
    category_id: str = Field(min_length=1)
    price: int = Field(ge=0, lt=1e9)


class UserTags(BaseModel):
    time: str = Field(regex="^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)$")
    cookie: str = Field(min_length=1)
    country: str = Field(min_length=1)
    device: str = Field(regex="^(PC|MOBILE|TV)$")
    action: str = Field(regex="^(VIEW|BUY)$")
    origin: str = Field(min_length=1)
    product: ProductInfo


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/user_tags/view")
async def add_view_tag(view: UserTags, response: Response):
    if view.action != "VIEW":
        raise HTTPException(status_code=442,
                            detail="user_tag posted in /user_tags/view is required to have param action: view")

    response.status_code = 204
    print("View", view)
    return


@app.post("/user_tags/buy")
async def add_buy_tag(buy: UserTags, response: Response):
    if buy != "BUY":
        raise HTTPException(status_code=442,
                            detail="user_tag posted in /user_tags/buy is required to have param action: buy")
    response.status_code = 204
    print("Buy", buy)
    return


class Dupa(BaseModel):
    cipa: str


@app.post("/user_tags/cipa")
async def cipa(body: Dupa, response: Response):
    response.status_code = 204
    print("View", body)

# curl -X POST -H "Content-Type: application/json" -d '{"time": "czas", "cookie": "kuki", "country": "PL", "device": "PC", "action": "VIEW", "origin": "US", "product_info": {"product_id": "2137", "brand_id": "balenciaga", "category_id": "566", "price": 33}}' st135vm101.rtb-lab.pl:8000/user_tags/view
