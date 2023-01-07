from .base import Base, NativeDatetimeField
from tortoise import fields
import math

class Journal(Base):
    created = NativeDatetimeField()

    postings = fields.ReverseRelation["Posting"]

    type = fields.CharField(max_length=16, index=True)

    batch: fields.ForeignKeyRelation["Batch"] = fields.ForeignKeyField(
        "models.Batch", related_name="journals", null=True
    )

    @property
    async def verify(self):
        sum = 0

        await self.fetch_related("postings")

        for posting in self.postings:
            sum += posting.amount

        return math.isclose(sum, 0)

    class Meta:
        table = "service_journals"
