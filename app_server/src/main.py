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
    product_info: ProductInfo


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/user_tags")
async def add_view_tag(view: UserTags, response: Response):
    response.status_code = 204
    print("View", view)
    return


class Dupa(BaseModel):
    cipa: str


@app.post("/user_tags/cipa")
async def cipa(body: Dupa, response: Response):
    response.status_code = 204
    print("View", body)

#
# curl -X POST -H "Content-Type: application/json" -d '{"time": "2022-03-22T12:15:00.000Z", "cookie": "kuki", "country": "PL", "device": "PC", "action": "VIEW", "origin": "US", "product_info": {"product_id": "2137", "brand_id": "balenciaga", "category_id": "566", "price": 33}}' st135vm101.rtb-lab.pl:8000/user_tags/buy
