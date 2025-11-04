from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_active_user
from app.api.permission import permission_operations

from app.models.user import User
from app.models.transaction import Status, Transaction

from app.crud.card import Card_CRUD
from app.crud.transaction import transaction_crud


router = APIRouter()


@router.post("/Transaction")
async def make_payment(current_user: Annotated[User, Depends(permission_operations.require_permission("transactions", "make_payment"))],
                            card_id : int,
                            money_amount : float,
                            company_name: str = "Free payment"):
    card = await Card_CRUD.get_card_by_id(card_id,current_user.id)
    if card:
        if not card.frozen:
            transaction_data = {"amount_of_money" : money_amount,
                                "name" : company_name,
                                "transaction_date" : date.today(),
                                "transaction_time" : datetime.now().time(),
                                "status" : Status.approved,
                                "card_id" : card_id}
            await transaction_crud.add_new_transaction(Transaction(**transaction_data), card.id)
            return {"message" : "Payment was successfully done"}
        else:
            raise HTTPException(status_code=400, detail="This card is frozen")
    else:
        raise HTTPException(status_code=404, detail="There is no card with this id")

@router.get("/Transactions")
async def show_transactions_for_a_specific_card(current_user: Annotated[User, Depends(permission_operations.require_permission("transactions", "show_for_my_card"))],
                                                card_id : int):
    card = await Card_CRUD.get_card_by_id(card_id, current_user.id)
    if card:
        transactions = await transaction_crud.get_all_transactions_by_card_id(card.id)
        if transactions:
            return transactions
        else:
            raise HTTPException(status_code=404, detail="No transactions for this card")
    else:
        raise HTTPException(status_code=404, detail="There is no card with this id")


@router.get("/Transactions/Show_all")
async def show_all_transactions(current_user: Annotated[User, Depends(permission_operations.require_permission("transactions", "show_all"))]):
    transactions = await transaction_crud.get_all_transactions()
    if transactions:
        return transactions
    else:
        return {"message" : "There is no transactions"}