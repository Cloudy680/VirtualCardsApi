import enum

from datetime import date
from pydantic import BaseModel

from sqlalchemy import ForeignKey, String
from sqlalchemy import select, exists
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import async_session_factory, Base


class Payment_system(enum.Enum):
    mastercard = "MASTERCARD"
    visa = "VISA"
    belcard = "BELCARD"

class CardORM(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(16), nullable=False)
    carrier_name : Mapped[str] = mapped_column(nullable=False)
    expires_date : Mapped[date] = mapped_column(nullable=False)
    payment_system : Mapped[Payment_system] = mapped_column(nullable=False)
    cvv : Mapped[str] = mapped_column(String(3), nullable=False)
    carrier_id : Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))
    frozen : Mapped[bool] = mapped_column(nullable=False, default=False)



class Card(BaseModel):
    id : int |  None = None
    number : str = None
    carrier_name : str = None
    expires_date : date = None
    payment_system : Payment_system = None
    frozen : bool = False

    carrier_id: int = None


    @staticmethod
    async def check_if_card_exists(number : str, carrier_id : int) -> bool:
        async with async_session_factory() as session:
            stmt = select(exists().where(CardORM.number == number, CardORM.carrier_id == carrier_id))
            result = await session.execute(stmt)
            return result.scalar()

    @staticmethod
    async def check_if_card_is_frozen(id : int, carrier_id : int) -> bool:
        async with async_session_factory() as session:
            stmt = select(exists().where(CardORM.id == id, CardORM.carrier_id == carrier_id,
                                         CardORM.frozen == True))
            result = await session.execute(stmt)
            return result.scalar()

    class Config:
        from_attributes = True

class Card_In_DB(Card):
    cvv : str


Card_check_functions = Card()