from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select

# Local imports
from web.routes import users, heroes, missions
from db import create_db_and_tables

"""Lifespans handlers are a powerful feature in FastAPI that allow you to define 
setup and teardown logic for your application."""
@asynccontextmanager
# async context manager for lifespan allows us to run async code during startup and shutdown
async def lifespan(app: FastAPI):
    create_db_and_tables() # setup: create database and tables
    
    print("Database setup complete. [OK]")

    yield # execution pauses here and the app starts accepting requests

    print("Shutting down application... [OK]")

app = FastAPI(title="Heroes Fast API app", lifespan=lifespan, tags=["app"])

# Register the routers
app.include_router(users.router)
app.include_router(heroes.router)
app.include_router(missions.router)