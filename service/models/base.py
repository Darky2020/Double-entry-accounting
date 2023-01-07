from tortoise.models import Model
from datetime import datetime
from tortoise import fields

class Base(Model):
    id = fields.IntField(pk=True)

class NativeDatetimeField(fields.Field[datetime], datetime):
    SQL_TYPE = "TIMESTAMP"
