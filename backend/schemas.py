from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator
class Input(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
class BookInput(Input):
    title: str = Field(min_length=1,max_length=160)
    author: str = Field(min_length=1,max_length=120)
    category: Literal['Roman','Edebiyat','Bilim','Çocuk','Diğer']
    kind: Literal['Bağış','Takas','Satış']
    price: int = Field(default=0,ge=0,le=100000)
    condition: Literal['İyi','Çok iyi','Yeni gibi']
    location: str = Field(min_length=1,max_length=100)
    description: str = Field(default='',max_length=2000)
    isbn: str = Field(default='',pattern=r'^(\d{10}|\d{13})?$')
    image_url: str = Field(default='',max_length=1000)
    @model_validator(mode='after')
    def price_rule(self):
        if self.kind == 'Satış' and self.price <= 0: raise ValueError('Satış fiyatı pozitif olmalı')
        if self.kind != 'Satış': self.price=0
        return self
class ProfileInput(Input):
    display_name: str = Field(min_length=2,max_length=80)
    city: str = Field(min_length=1,max_length=100)
    bio: str = Field(default='',max_length=500)
class RequestInput(Input):
    offered_book_id: int | None = Field(default=None,gt=0)
    message: str = Field(default='',max_length=1000)
    delivery_method: Literal['campus','hand','cargo'] = 'campus'
    shipping_payer: Literal['sender','recipient'] = 'recipient'
class RequestAction(Input):
    action: Literal['accept','reject','cancel']
class DeliveryInput(Input):
    carrier: str = Field(default='',max_length=80)
    tracking_number: str = Field(default='',max_length=100)
    meeting_point: str = Field(default='',max_length=200)
    cost_cents: int = Field(default=0,ge=0,le=10000000)
class ComplaintInput(Input):
    book_id: int | None = Field(default=None,gt=0)
    transaction_id: int | None = Field(default=None,gt=0)
    reason: str = Field(min_length=10,max_length=1000)
    @model_validator(mode='after')
    def target(self):
        if (self.book_id is None) == (self.transaction_id is None): raise ValueError('Bir kitap veya bir işlem seç')
        return self
class ResolutionInput(Input):
    resolution: str = Field(min_length=10,max_length=1000)
    outcome: Literal['dismiss','resolved','cancel_transaction'] = 'resolved'
class SupportInput(Input):
    organization: str = Field(min_length=2,max_length=160)
    document_url: str = Field(default='',max_length=1000)
    note: str = Field(min_length=5,max_length=1000)
class ModerateInput(Input):
    hidden: bool
    reason: str = Field(min_length=5,max_length=500)
class UserStateInput(Input):
    disabled: bool
    reason: str = Field(min_length=5,max_length=500)
