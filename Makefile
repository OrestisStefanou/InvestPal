run_investpal:
	uv run fastapi run main.py

run_investpal_dev:
	uv run fastapi dev main.py

run_investpal_mcp:
	uv run python3 -m apps.mcp_api.app

backfill_embeddings:
	uv run python3 -m scripts.backfill_note_embeddings

# YES=1 skips the interactive confirmation, FORCE=1 lets first-pull replace a
# local database that has rows in it. Both arrive as environment variables from
# whatever ran make, so `make turso_first_pull FORCE=1` works from here and from
# the ecosystem root alike.
TURSO_YES   := $(if $(filter 1 y yes true,$(YES)),--yes)
TURSO_FORCE := $(if $(filter 1 y yes true,$(FORCE)),--force)

turso_status:
	uv run python3 -m scripts.turso_sync status

turso_first_push:
	uv run python3 -m scripts.turso_sync first-push $(TURSO_YES)

turso_first_pull:
	uv run python3 -m scripts.turso_sync first-pull $(TURSO_FORCE) $(TURSO_YES)

turso_push:
	uv run python3 -m scripts.turso_sync push

turso_pull:
	uv run python3 -m scripts.turso_sync pull $(TURSO_YES)

turso_verify:
	uv run python3 -m scripts.turso_sync verify