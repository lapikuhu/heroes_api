from __future__ import annotations

from typing import Any

import gradio as gr
import httpx
from fastapi import FastAPI


async def login_against_backend(app: FastAPI, username: str, password: str) -> tuple[bool, str]:
    clean_username = username.strip()
    if not clean_username or not password:
        return False, "Enter both username and password."

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://gradio.local") as client:
        response = await client.post(
            "/users/login",
            data={"username": clean_username, "password": password},
        )

    if response.is_success:
        return True, "Credentials accepted. API login succeeded."

    detail: Any
    try:
        detail = response.json().get("detail")
    except ValueError:
        detail = None

    if isinstance(detail, str) and detail.strip():
        return False, detail

    return False, "Login failed. Check your credentials and try again."


def build_landing_page(app: FastAPI) -> gr.Blocks:
    theme = gr.themes.Soft(
        primary_hue="slate",
        secondary_hue="blue",
        neutral_hue="zinc",
    )

    async def submit_login(username: str, password: str) -> str:
        ok, message = await login_against_backend(app, username, password)
        status = "Success" if ok else "Error"
        return f"### {status}\n{message}"

    with gr.Blocks(
        title="Heroes API Login",
        theme=theme,
        fill_height=True,
        css="""
        .hero-shell {
            max-width: 520px;
            margin: 48px auto;
            padding: 32px;
            border: 1px solid #d4d4d8;
            border-radius: 20px;
            background: linear-gradient(180deg, #fafafa 0%, #f4f4f5 100%);
            box-shadow: 0 24px 80px rgba(15, 23, 42, 0.12);
        }
        .hero-subtitle {
            color: #3f3f46;
            margin-bottom: 20px;
        }
        .hero-status {
            min-height: 92px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.78);
        }
        body {
            background: radial-gradient(circle at top, #e0f2fe 0%, #f8fafc 38%, #e4e4e7 100%);
        }
        """,
    ) as landing_page:
        with gr.Column(elem_classes=["hero-shell"]):
            gr.Markdown("# Heroes API")
            gr.Markdown(
                "Sign in to validate your credentials against the existing API backend.",
                elem_classes=["hero-subtitle"],
            )
            username = gr.Textbox(label="Username", placeholder="Enter your username")
            password = gr.Textbox(
                label="Password",
                placeholder="Enter your password",
                type="password",
            )
            login_button = gr.Button("Log in", variant="primary")
            status = gr.Markdown(
                "### Ready\nEnter credentials to test the API login flow.",
                elem_classes=["hero-status"],
            )

            login_button.click(
                submit_login,
                inputs=[username, password],
                outputs=status,
            )
            password.submit(
                submit_login,
                inputs=[username, password],
                outputs=status,
            )

    return landing_page