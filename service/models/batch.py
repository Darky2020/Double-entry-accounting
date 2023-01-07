from .base import Base, NativeDatetimeField
from tortoise.functions import Sum
from tortoise import fields
import math

class Batch(Base):
    created = NativeDatetimeField()

    journals: fields.ReverseRelation["Journal"]

    @property
    async def verify(self):
        await self.fetch_related("journals")

        amount_list = await self.journals.all().annotate(
            amount_sum=Sum("postings__amount")
        ).values("amount_sum")

        amount = sum(item['amount_sum'] for item in amount_list)

        return math.isclose(amount, 0)

    @property
    async def journal_count(self):
        await self.fetch_related("journals")

        return len(self.journals)
    
    class Meta:
        table = "service_batches"
