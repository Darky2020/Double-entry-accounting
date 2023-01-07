from service.models import Account, AssetType, Batch
from service.accounting import Accounting
from tortoise import Tortoise
import asyncio
import config

async def init_db():
    if not (account := await Account.filter(username="CashBook").first()):
        account = await Account.create(**{
            "username": "CashBook"
        })

    if not (user1 := await Account.filter(username="User1").first()):
        user1 = await Account.create(**{
            "username": "User1"
        })

    if not (user2 := await Account.filter(username="User2").first()):
        user2 = await Account.create(**{
            "username": "User2"
        })

    if not (user3 := await Account.filter(username="User3").first()):
        user3 = await Account.create(**{
            "username": "User3"
        })

    if not (asset_type := await AssetType.filter(name="USD").first()):
        asset_type = await AssetType.create(**{
            "name": "USD"
        })

async def main():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    await init_db()


    await Accounting.deposit("User2", "USD", 16.3)
    await Accounting.deposit("User1", "USD", 4.5)

    await Accounting.withdraw("User2", "USD", 2.14)
    await Accounting.transfer("User1", "User3", "USD", 3.0)


    print("User 1:", await Accounting.get_balance("User1", "USD"))
    print("User 2:", await Accounting.get_balance("User2", "USD"))
    print("User 3:", await Accounting.get_balance("User3", "USD"))


if __name__ == "__main__":
    asyncio.run(main())
