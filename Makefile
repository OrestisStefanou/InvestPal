run_investpal:
	uv run fastapi run main.py

run_investpal_dev:
	uv run fastapi dev main.py

run_investpal_mcp:
	uv run python3 -m apps.mcp_api.app

backfill_embeddings:
	uv run python3 -m scripts.backfill_note_embeddings