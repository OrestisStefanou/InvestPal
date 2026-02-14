run_investpal:
	uv run fastapi run main.py

run_investpal_dev:
	uv run fastapi dev main.py

run_investpal_mcp:
	uv run python3 -m mcp_app.app