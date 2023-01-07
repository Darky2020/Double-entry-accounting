from tortoise import fields
from .base import Base

class Account(Base):
    username = fields.CharField(max_length=64, unique=True)

    postings: fields.ReverseRelation["Posting"]

    class Meta:
        table = "service_accounts"
