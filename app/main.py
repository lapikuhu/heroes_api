from contextlib import asynccontextmanager
from fastapi import FastAPI
import gradio as gr

# Local imports
from web.routes import users, heroes, missions
from db import create_db_and_tables
from web.gradio_landing import build_landing_page

"""Lifespans handlers in FastAPI allow you to define 
setup and teardown logic for your application."""
@asynccontextmanager
# async context manager for lifespan allows us to run async code during startup and shutdown
async def lifespan(app: FastAPI):
    await create_db_and_tables() # setup: create database and tables
    
    print("Database setup complete. [OK]")

    yield # execution pauses here and the app starts accepting requests

    print("Shutting down application... [OK]")

app = FastAPI(title="Heroes Fast API app", lifespan=lifespan, tags=["app"])

# Register the routers
app.include_router(users.router)
app.include_router(heroes.router)
app.include_router(missions.router)

# Build the Gradio landing page and mount it at the root path

landing_page = build_landing_page(app)

# Mount the Gradio app at the root path ("/") of the FastAPI application
# Preserved docs
# Mindful of the app variable re-assignment.
app = gr.mount_gradio_app(app, landing_page, path="/")

