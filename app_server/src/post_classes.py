from pydantic import BaseModel, Field
from typing import List
from typing import Union

utc_date_time_rgx = "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z"

date_time_rgx = "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:(\d{2}|\d{2}.\d{3})"
time_range_rgx = date_time_rgx + "_" + date_time_rgx


class ProductInfo(BaseModel):
    product_id: str = Field(min_length=1)
    brand_id: str = Field(min_length=1)
    category_id: str = Field(min_length=1)
    price: int = Field(ge=0, lt=1e9)


class UserTags(BaseModel):
    time: str = Field(regex="^(" + utc_date_time_rgx + ")$")
    cookie: str = Field(min_length=1)
    country: str = Field(min_length=1)
    device: str = Field(regex="^(PC|MOBILE|TV)$")
    action: str = Field(regex="^(VIEW|BUY)$")
    origin: str = Field(min_length=1)
    product_info: ProductInfo


class AggregateQuery(BaseModel):
    time_range: str = Field(regex="^(" + time_range_rgx + ")$")
    action: str = Field(regex="^(VIEW|BUY)$")
    origin: Union[str, None] = Field(default=None)
    brand_id: Union[str, None] = Field(default=None)
    category_id: Union[str, None] = Field(default=None)
    aggregates: List[str] = Field(default=None)