from tortoise import fields
from .base import Base

class Posting(Base):
    amount = fields.DecimalField(
        max_digits=28, decimal_places=8, default=0
    )

    index = fields.IntField(index=True)

    journal: fields.OneToOneRelation["Journal"] = fields.ForeignKeyField(
        "models.Journal", related_name="postings"
    )

    account: fields.OneToOneRelation["Account"] = fields.ForeignKeyField(
        "models.Account", related_name="postings"
    )

    asset_type: fields.OneToOneRelation["AssetType"] = fields.ForeignKeyField(
        "models.AssetType", related_name="postings"
    )

    class Meta:
        table = "service_postings"
