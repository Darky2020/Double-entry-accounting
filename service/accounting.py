from service.models import Account, Journal, Posting, AssetType, Batch
from service.exceptions import InvalidJournal
from datetime import datetime
from service import constants
import math

class Accounting(object):
    @classmethod
    async def new_batch(cls):
        if not (batch := await Batch.filter().order_by("-id").first()):
            batch = await Batch.create(**{
                "created": datetime.utcnow()
            })

            return

        new_batch = await Batch.create(**{
            "created": datetime.utcnow()
        })

        if not await batch.verify:
            # The batch is invalid so we search for the journal causing the problem
            async for journal in batch.journals:
                if not journal.verify:
                    raise InvalidJournal(journal.reference)

        journal = await Journal.create(**{
            "created": datetime.utcnow(),
            "type": constants.MIGRATION,
            "batch": new_batch
        })

        # Move balances from the previous batch into the first journal of the new batch
        async for asset_type in AssetType.filter().all():
            sum = 0

            async for account in Account.exclude(username="CashBook").all():
                amount = await cls.get_balance(account.username, asset_type.name)

                if not math.isclose(amount, 0):
                    await Posting.create(**{
                        "amount": amount,
                        "journal": journal,
                        "account": account,
                        "asset_type": asset_type
                    })

                    sum += amount

            cash_book = await Account.filter(username="CashBook").first()

            await Posting.create(**{
                "amount": -sum,
                "journal": journal,
                "account": cash_book,
                "asset_type": asset_type
            })

    @classmethod
    async def get_balance(cls, username: str, assetname: str) -> float:
        if not (account := await Account.filter(username=username).first()):
            return 0

        if not (asset_type := await AssetType.filter(name=assetname).first()):
            return 0

        if not (batch := await Batch.filter().order_by("-created").first()):
            return 0

        amount = 0

        async for journal in batch.journals:
            postings = await journal.postings.filter(
                account=account,
                asset_type=asset_type
            ).all()

            for posting in postings:
                amount += posting.amount

        return amount

    @classmethod
    async def deposit(cls, username: str, amount: float) -> bool:
        if not (account := await Account.filter(username=username).first()):
            return False
        
        # Unfinished
