from .base import Base, NativeDatetimeField
from tortoise import fields

class Posting(Base):
    created = NativeDatetimeField()

    amount = fields.DecimalField(
        max_digits=28, decimal_places=8, default=0
    )

    index = fields.IntField(unique=True)

    journal: fields.ForeignKeyRelation["Journal"] = fields.ForeignKeyField(
        "models.Journal", related_name="postings"
    )

    account: fields.ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account", related_name="postings"
    )

    asset_type: fields.ForeignKeyRelation["AssetType"] = fields.ForeignKeyField(
        "models.AssetType", related_name="postings"
    )

    class Meta:
        table = "service_postings"
