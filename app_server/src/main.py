from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from typing import Union

import operator

app = FastAPI()


class ProductInfo(BaseModel):

    def __init__(self, product_id, brand_id, category_id, price: int):
        self.product_id = product_id
        self.brand_id = brand_id
        self.category_id = category_id
        self.price = price

    def not_empty(self, i, name):
        if not i: HTTPException(status_code=442, detail=name + " cannot be empty")
        return

    product_id = property(operator.attrgetter('_product_id'))

    @product_id.setter
    def product_id_setter(self, pi):
        self.not_empty(pi, 'product_id')
        self._product_id = pi

    brand_id = property(operator.attrgetter('_brand_id'))

    @brand_id.setter
    def brand_id_setter(self, bi):
        self.not_empty(bi, 'brand_id')
        self._brand_id = bi

    category_id = property(operator.attrgetter('_category_id'))

    @category_id.setter
    def category_id_setter(self, ci):
        self.not_empty(ci, 'category_id')
        self._category_id = ci

    price = property(operator.attrgetter('_price'))

    @price.setter
    def price_setter(self, p):
        if p < 0 or p > 1e9:
            raise HTTPException(status_code=442, detail="price in wrong value range")
        self._price = p


class UserTags(BaseModel):

    def __init__(self, time, cookie, country, device, action, origin, product_info):
        self.time = time
        self.cookie = cookie
        self.country = country
        self.device = device
        self.action = action
        self.origin = origin
        self.productInfo = product_info

    def not_empty(self, i, name):
        if not i: HTTPException(status_code=442, detail=name + " cannot be empty")
        return

    time = property(operator.attrgetter('_time'))

    @time.setter
    def time_setter(self, t):
        self.not_empty(t, 'time')  # TODO: verify time better
        self._time = t

    cookie = property(operator.attrgetter('_cookie'))

    @cookie.setter
    def cookie_setter(self, c):
        self.not_empty(c, 'cookie')
        self._cookie = c

    country = property(operator.attrgetter('_property'))

    @country.setter
    def country_setter(self, c):
        self.not_empty(c, 'country')
        self._country = c

    device = property(operator.attrgetter('_device'))

    @device.setter
    def device_setter(self, d):
        if not d in ["PC", "MOBILE", "TV"]: raise HTTPException(status_code=442, detail="invalid device type")
        self._device = d

    action = property(operator.attrgetter('_action'))

    @action.setter
    def action_setter(self, a):
        if not a in ["VIEW", "BUY"]: raise HTTPException(status_code=442, detail="invalid action type")
        self._action = a

    origin = property(operator.attrgetter('_origin'))

    @origin.setter
    def origin_setter(self, o):
        self.not_empty(o, 'origin')
        self._orgin = o

    product_info = property(operator.attrgetter('_product_info'))

    @product_info.setter
    def product_info_setter(self, pi):
        self._product_info = pi


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/user_tags/view")
async def add_view_tag(view: UserTags, response: Response):
    if view.action != "VIEW":
        raise HTTPException(status_code=442, detail="user_tag posted in /user_tags/view is required to have param action: view")

    response.status_code = 204
    print("View", view)
    return


@app.post("/user_tags/buy")
async def add_buy_tag(buy : UserTags, response: Response):
    if buy != "BUY":
        raise HTTPException(status_code=442, detail="user_tag posted in /user_tags/buy is required to have param action: buy")
    response.status_code = 204
    print("Buy", buy)
    return


class Dupa(BaseModel):
    cipa: str


@app.post("/user_tags/cipa")
async def cipa(body: Dupa, response: Response):
    response.status_code = 204
    print("View", body)
