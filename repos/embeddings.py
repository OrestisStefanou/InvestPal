"""Local text embeddings for semantic search over conversation notes.

Runs a quantised ONNX model on the CPU via fastembed, so no note text ever
leaves the machine. The model is ~67MB and is downloaded from HuggingFace on
first use, then served from `settings.EMBEDDING_CACHE_DIR`. Set
`HF_HUB_OFFLINE=1` once the download has happened, otherwise huggingface_hub
makes a metadata call on every init and a network-less start has to wait for
that to time out.
"""

import json
import logging
import os
import threading

from config import settings


logger = logging.getLogger(__name__)


# Not a Settings field: schema.sql declares the embedding column as
# F32_BLOB(384), so the dimension count is a property of the schema and the
# model together, not something an operator can retune from .env.
EMBEDDING_DIMENSIONS = 384
EMBEDDING_BLOB_BYTES = EMBEDDING_DIMENSIONS * 4


def to_vector_json(vector: list[float]) -> str:
    """Render a vector in the JSON-array form that Turso's `vector32()` parses."""
    return json.dumps(vector)


class FastEmbedEmbedder:
    """Blocking embedder. Callers on the event loop must use `asyncio.to_thread`.

    Every public method fully materialises its result before returning:
    fastembed's `embed`/`query_embed` are generators, so handing one back would
    push the ONNX forward pass onto whichever thread happens to iterate it.
    """

    def __init__(
        self,
        model_name: str = settings.EMBEDDING_MODEL_NAME,
        cache_dir: str = settings.EMBEDDING_CACHE_DIR,
    ):
        self._model_name = model_name
        self._cache_dir = os.path.expanduser(cache_dir)
        self._model = None
        # A threading lock, not an asyncio one: initialisation happens inside an
        # asyncio.to_thread worker, where an asyncio lock would protect nothing.
        self._lock = threading.Lock()

    @property
    def model_name(self) -> str:
        """Identifier persisted alongside each vector, so stale rows can be found."""
        return self._model_name

    def _get_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    # Imported lazily: pulling in onnxruntime costs about a
                    # second, and processes that never embed shouldn't pay it.
                    from fastembed import TextEmbedding

                    os.makedirs(self._cache_dir, exist_ok=True)
                    logger.info(
                        "Loading embedding model %s from %s",
                        self._model_name,
                        self._cache_dir,
                    )
                    self._model = TextEmbedding(
                        model_name=self._model_name,
                        cache_dir=self._cache_dir,
                        # One thread per process: the FastAPI app and the MCP
                        # server each hold their own model, and at batch size 1
                        # onnxruntime's core-count default is oversubscription.
                        threads=1,
                    )
        return self._model

    def warm_up(self) -> None:
        """Force the model load so the first real call doesn't pay for it."""
        self._get_model()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self._get_model()
        return [vector.tolist() for vector in model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        """Embed a search query.

        Uses `query_embed` rather than `embed` so bge's retrieval instruction
        prefix is applied, which is what makes query and document vectors
        comparable for this model family.
        """
        model = self._get_model()
        return next(iter(model.query_embed(text))).tolist()


_embedder: FastEmbedEmbedder | None = None
_embedder_lock = threading.Lock()


def get_embedder() -> FastEmbedEmbedder | None:
    """Return the process-wide embedder, or None when embeddings are disabled.

    Must be used by the DI factories rather than constructing an embedder per
    request: both `dependencies.py` and `apps/mcp_api/app.py` rebuild their
    services on every call.
    """
    if not settings.EMBEDDING_ENABLED:
        return None

    global _embedder
    if _embedder is None:
        with _embedder_lock:
            if _embedder is None:
                _embedder = FastEmbedEmbedder()
    return _embedder
