from contextlib import asynccontextmanager

from datetime import datetime

from typing import Annotated

from fastapi import FastAPI, Depends

from app.core.scheduler import scheduler_manager
from app.core.db_core import create_tables

from app.api.endpoints import auth, cards, transactions, account, admin
from app.api.dependencies import get_current_active_user

from app.models.user import User

from app.api.permission import permission_operations

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    await scheduler_manager.start_scheduler()
    await permission_operations.create_first_admin()
    yield
    # Shutdown
    await scheduler_manager.shutdown_scheduler()

app = FastAPI(title="Virtual cards api", version="1.0.0", lifespan=lifespan)



app.include_router(auth.router, prefix = "/authentication", tags=["Authentication"])
app.include_router(cards.router, prefix = "/Cards", tags = ["Cards"])
app.include_router(transactions.router, prefix = "/Transaction", tags = ["Transactions"])
app.include_router(account.router, prefix = "/Account", tags = ["Account"])
app.include_router(admin.router, prefix="/admin", tags=["Admin operations"])


@app.get("/Root", tags = ["Root"])
async def root():
    return {
        "message": "Card Service API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health", tags = ["Check"])
async def health_check(current_user: Annotated[User, Depends(permission_operations.require_permission("check", "health_check"))]):
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "user" : current_user
    }

@app.get("/User check", tags = ["Check"])
async def check(current_user : Annotated[User, Depends(get_current_active_user)] ):
    if current_user.name:
        return {"message": f"Welcome to FastAPI App {current_user.name}!"}
    else:
        return {"message": f"Welcome to FastAPI App {current_user.name}!"}


