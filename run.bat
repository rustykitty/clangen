@echo off

uv sync --extra discord || ( pause & exit /b )
uv run main.py || ( pause & exit /b )
