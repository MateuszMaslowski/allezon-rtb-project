from pydantic import BaseModel, Field


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
    origin: str = Field(default=None)
    brand_id: str = Field(default=None)
    category_id: str = Field(default=None)
    aggregates: List[str] = Field(default=None)