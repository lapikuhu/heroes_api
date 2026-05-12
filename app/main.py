from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from web.routes import users, heroes, missions
from db import create_db_and_tables

"""Lifespans handlers in FastAPI allow you to define 
setup and teardown logic for your application."""
@asynccontextmanager
# async context manager for lifespan allows us to run async code during startup and shutdown
async def lifespan(app: FastAPI):
    await create_db_and_tables() # setup: seed startup data after Alembic migrations
    
    print("Database setup complete. [OK]")

    yield # execution pauses here and the app starts accepting requests

    print("Shutting down application... [OK]")

app = FastAPI(title="Heroes Fast API app", lifespan=lifespan, tags=["app"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the routers
app.include_router(users.router)
app.include_router(heroes.router)
app.include_router(missions.router)
