from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
if str(APP_DIR) not in sys.path:
	sys.path.insert(0, str(APP_DIR))

from web.gradio_landing import login_against_backend


def test_gradio_login_helper_posts_to_existing_login_route() -> None:
	backend_app = FastAPI()

	@backend_app.post("/users/login")
	async def login() -> dict[str, str]:
		return {"access_token": "secret-token", "token_type": "bearer"}

	ok, message = __import__("asyncio").run(login_against_backend(backend_app, "demo", "pw"))

	assert ok is True
	assert "Credentials accepted" in message


def test_homepage_and_docs_remain_available(monkeypatch) -> None:
	import main

	async def skip_startup_seed() -> None:
		return None

	monkeypatch.setattr(main, "create_db_and_tables", skip_startup_seed)

	with TestClient(main.app) as client:
		home_response = client.get("/")
		docs_response = client.get("/docs")

	assert home_response.status_code == 200
	assert "Heroes API" in home_response.text
	assert docs_response.status_code == 200
