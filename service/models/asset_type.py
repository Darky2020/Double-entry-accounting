from tortoise import fields
from .base import Base

class AssetType(Base):
    name = fields.CharField(max_length=64, unique=True)

    transfers: fields.ReverseRelation["Posting"]

    class Meta:
        table = "service_assettypes"
