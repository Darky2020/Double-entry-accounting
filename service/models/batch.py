from .base import Base, NativeDatetimeField
from tortoise import fields

class Batch(Base):
    created = NativeDatetimeField()

    journals: fields.ReverseRelation["Journal"]

    @property
    async def verify(self):
        await self.fetch_related("journals")

        async for journal in self.journals:
            if not await journal.verify:
                return False

        return True

    class Meta:
        table = "service_batches"
