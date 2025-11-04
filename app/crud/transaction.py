from sqlalchemy import select

from app.db.database import async_session_factory

from app.models.transaction import TransactionORM ,Transaction


class TransactionCRUD:

    @staticmethod
    async def add_new_transaction(transaction: Transaction, c_id: int):
        async with async_session_factory() as session:
            new_transaction = TransactionORM(amount_of_money=transaction.amount_of_money,
                                             name=transaction.name,
                                             transaction_date=transaction.transaction_date,
                                             transaction_time=transaction.transaction_time,
                                             status=transaction.status,
                                             card_id=c_id
                                             )
            session.add(new_transaction)
            await session.commit()


    @staticmethod
    async def get_all_transactions_by_card_id(card_id : str):
        async with async_session_factory() as session:
            stmt = select(TransactionORM).where(TransactionORM.card_id == card_id)
            result = await session.execute(stmt)
            transactions = result.scalars().all()
            return [Transaction.model_validate(transaction) for transaction in transactions]


    @staticmethod
    async def get_all_transactions():
        async with async_session_factory() as session:
            stmt = select(TransactionORM)
            result = await session.execute(stmt)
            transactions = result.scalars().all()
            return [Transaction.model_validate(transaction) for transaction in transactions]

    @staticmethod
    async def get_transaction_by_id(transaction_id: int):
        async with async_session_factory() as session:
            stmt = select(TransactionORM).where(TransactionORM.id == transaction_id)
            result = await session.execute(stmt)
            transaction = result.scalar_one_or_none()

            return transaction

    @staticmethod
    async def delete_transaction_by_id(transaction_id : int):
        async with async_session_factory() as session:
            stmt = select(TransactionORM).where(TransactionORM.id == transaction_id)
            result = await session.execute(stmt)
            transaction = result.scalar_one_or_none()

            if transaction:
                await session.delete(transaction)
                await session.commit()
                return True
            else:
                return True


transaction_crud = TransactionCRUD()