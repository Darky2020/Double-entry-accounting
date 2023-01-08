from service.models import Account, Journal, Posting, AssetType, Batch
from service.exceptions import InvalidJournal
from tortoise.functions import Sum
from datetime import datetime
from service import constants
import math

# Max amount of journals per batch
MAX_JOURNALS = 200

class Accounting(object):
    @classmethod
    async def last_batch(cls):
        return await Batch.filter().order_by("-created").first()

    @classmethod
    async def get_cashbook(cls):
        return await Account.filter(username="CashBook").first()

    @classmethod
    async def next_posting_index(cls):
        if (posting := await Posting.filter().order_by("-created").first()):
            return posting.index+1

        return 1

    @classmethod
    async def new_batch(cls):
        if not (batch := await cls.last_batch()):
            batch = await Batch.create(**{
                "created": datetime.utcnow()
            })

            return batch

        if not await batch.verify:
            # The batch is invalid so we search for the journal causing the problem
            async for journal in batch.journals:
                if not await journal.verify:
                    raise InvalidJournal(journal.reference)

        journal = await Journal.create(**{
            "created": datetime.utcnow(),
            "type": constants.MIGRATION,
        })

        # Move balances from the previous batch into the first journal of the new batch
        async for asset_type in AssetType.filter().all():
            sum = 0

            async for account in Account.exclude(username="CashBook").all():
                amount = await cls.get_balance(account.username, asset_type.name)

                if not math.isclose(amount, 0):
                    await Posting.create(**{
                        "created": datetime.utcnow(),
                        "amount": amount,
                        "index": await cls.next_posting_index(),
                        "journal": journal,
                        "account": account,
                        "asset_type": asset_type
                    })

                    sum += amount

            await Posting.create(**{
                "created": datetime.utcnow(),
                "amount": -sum,
                "index": await cls.next_posting_index(),
                "journal": journal,
                "account": await cls.get_cashbook(),
                "asset_type": asset_type
            })

        new_batch = await Batch.create(**{
            "created": datetime.utcnow()
        })

        journal.batch = new_batch
        await journal.save()

        return new_batch

    @classmethod
    async def get_balance(cls, username: str, assetname: str) -> float:
        if not (account := await Account.filter(username=username).first()):
            return 0

        if not (asset_type := await AssetType.filter(name=assetname).first()):
            return 0

        if not (batch := await cls.last_batch()):
            return 0

        amount_list = (
            await batch.journals.filter(
                postings__account=account,
                postings__asset_type=asset_type
            ).all().annotate(
                amount_sum=Sum("postings__amount")
            ).values("amount_sum"))

        amount = sum(item['amount_sum'] for item in amount_list)

        return amount

    @classmethod
    async def deposit(cls, username: str, assetname: str, amount: float) -> bool:
        if not (account := await Account.filter(username=username).first()):
            return False
        
        if not (asset_type := await AssetType.filter(name=assetname).first()):
            return False

        if amount <= 0:
            return False

        if not (batch := await cls.last_batch()):
            batch = await cls.new_batch()

        if await batch.journal_count >= MAX_JOURNALS:
            batch = await cls.new_batch()

        journal = await Journal.create(**{
            "created": datetime.utcnow(),
            "type": constants.DEPOSIT,
            "batch": batch
        })

        await Posting.create(**{
            "created": datetime.utcnow(),
            "amount": amount,
            "index": await cls.next_posting_index(),
            "journal": journal,
            "account": account,
            "asset_type": asset_type
        })

        await Posting.create(**{
            "created": datetime.utcnow(),
            "amount": -amount,
            "index": await cls.next_posting_index(),
            "journal": journal,
            "account": await cls.get_cashbook(),
            "asset_type": asset_type
        })

        if not await journal.verify:
            raise InvalidJournal(journal.reference)

        return True

    @classmethod
    async def withdraw(cls, username: str, assetname: str, amount: float) -> bool:
        if not (account := await Account.filter(username=username).first()):
            return False
        
        if not (asset_type := await AssetType.filter(name=assetname).first()):
            return False

        if amount <= 0:
            return False

        if float(await cls.get_balance(username, assetname)) - amount < 0:
            return False

        if not (batch := await cls.last_batch()):
            batch = await cls.new_batch()

        if await batch.journal_count >= MAX_JOURNALS:
            batch = await cls.new_batch()

        journal = await Journal.create(**{
            "created": datetime.utcnow(),
            "type": constants.WITHDRAWAL,
            "batch": batch
        })

        await Posting.create(**{
            "created": datetime.utcnow(),
            "amount": -amount,
            "index": await cls.next_posting_index(),
            "journal": journal,
            "account": account,
            "asset_type": asset_type
        })

        await Posting.create(**{
            "created": datetime.utcnow(),
            "amount": amount,
            "index": await cls.next_posting_index(),
            "journal": journal,
            "account": await cls.get_cashbook(),
            "asset_type": asset_type
        })

        if not await journal.verify:
            raise InvalidJournal(journal.reference)

        return True

    @classmethod
    async def transfer(cls, sender_name: str, receiver_name: str, assetname: str, amount: float) -> bool:
        if not (sender := await Account.filter(username=sender_name).first()):
            return False

        if not (receiver := await Account.filter(username=receiver_name).first()):
            return False
        
        if not (asset_type := await AssetType.filter(name=assetname).first()):
            return False

        if amount <= 0:
            return False

        if float(await cls.get_balance(sender_name, assetname)) - amount < 0:
            return False

        if not (batch := await cls.last_batch()):
            batch = await cls.new_batch()

        if await batch.journal_count >= MAX_JOURNALS:
            batch = await cls.new_batch()

        journal = await Journal.create(**{
            "created": datetime.utcnow(),
            "type": constants.TRANSFER,
            "batch": batch
        })

        await Posting.create(**{
            "created": datetime.utcnow(),
            "amount": -amount,
            "index": await cls.next_posting_index(),
            "journal": journal,
            "account": sender,
            "asset_type": asset_type
        })

        await Posting.create(**{
            "created": datetime.utcnow(),
            "amount": amount,
            "index": await cls.next_posting_index(),
            "journal": journal,
            "account": receiver,
            "asset_type": asset_type
        })

        if not await journal.verify:
            raise InvalidJournal(journal.reference)

        return True
