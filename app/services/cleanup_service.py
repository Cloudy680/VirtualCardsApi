from datetime import date, timedelta

from sqlalchemy import select

from app.db.database import async_session_factory

from app.models.card import CardORM
from app.models.transaction import TransactionORM


class CardCleanupService:
    @staticmethod
    async def freeze_expired_cards():
        async with async_session_factory() as session:
            today = date.today()
            stmt = select(CardORM).where(CardORM.expires_date < today, CardORM.frozen == False)
            result = await session.execute(stmt)
            expires_cards = result.scalars().all()

            frozen_counter = 0

            if expires_cards:
                for card in expires_cards:
                    card.frozen = True
                    frozen_counter += 1

                if frozen_counter > 0:
                    await session.commit()


    @staticmethod
    async def delete_all_old_frozen_cards():
        async with async_session_factory() as session:
            month_ago = date.today() - timedelta(days=30)
            stmt = select(CardORM).where(CardORM.expires_date < month_ago, CardORM.frozen == True)
            result = await session.execute(stmt)
            cards_to_delete = result.scalars().all()

            deleted_counter = 0
            if cards_to_delete:
                for card in cards_to_delete:
                    await session.delete(card)
                    deleted_counter += 1

                if deleted_counter > 0:
                    await session.commit()


    @staticmethod
    async def delete_all_old_transactions():
        async with async_session_factory() as session:
            month_ago = date.today() - timedelta(days=30)
            stmt = select(TransactionORM).where(TransactionORM.transaction_date < month_ago)
            result = await session.execute(stmt)
            old_transactions = result.scalars().all()

            deleted_counter = 0

            if old_transactions:
                for transaction in old_transactions:
                    await session.delete(transaction)
                    deleted_counter += 1

                if deleted_counter > 0:
                    await session.commit()


    @staticmethod
    async def perform_full_cleanup():
        print("CLEANUP START")
        await CardCleanupService.freeze_expired_cards()
        await CardCleanupService.delete_all_old_frozen_cards()
        await CardCleanupService.delete_all_old_transactions()
        print("CLEANUP END")

