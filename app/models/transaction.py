import enum

from pydantic import BaseModel
from datetime import date, time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

class Status(enum.Enum):
    approved = "APPROVED"
    declined = "DECLINED"
    processing = "PROCESSING"


class TransactionORM(Base):

    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount_of_money: Mapped[float] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=True)
    transaction_date: Mapped[date] = mapped_column(nullable=True)
    transaction_time: Mapped[time] = mapped_column(nullable=True)
    status: Mapped[Status] = mapped_column(nullable=True)

    card_id: Mapped[str] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"))


class Transaction(BaseModel):
    amount_of_money: float
    name: str
    transaction_date: date
    transaction_time: time
    status: Status

    card_id: int

    class Config:
        from_attributes = True

