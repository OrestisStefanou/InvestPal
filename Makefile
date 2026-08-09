run_investpal:
	uv run fastapi run main.py

run_investpal_dev:
	uv run fastapi dev main.py

run_investpal_mcp:
	uv run python3 -m apps.mcp_api.app

backfill_embeddings:
	uv run python3 -m scripts.backfill_note_embeddings

turso_status:
	uv run python3 -m scripts.turso_sync status

turso_first_push:
	uv run python3 -m scripts.turso_sync first-push

turso_first_pull:
	uv run python3 -m scripts.turso_sync first-pull

turso_push:
	uv run python3 -m scripts.turso_sync push

turso_pull:
	uv run python3 -m scripts.turso_sync pull

turso_verify:
	uv run python3 -m scripts.turso_sync verify