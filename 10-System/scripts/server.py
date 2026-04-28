"""FastAPI backend for the Knowledge Base search API.

Provides semantic search, topic existence checking, and index rebuild
over the ChromaDB vector store.

Run:
    uvicorn server:app --host 127.0.0.1 --port 28790
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import indexer


@asynccontextmanager
async def lifespan(app: FastAPI):
    indexer.get_embedding_fn()
    print("Knowledge Base Search API ready on port 28790")
    yield


app = FastAPI(title="Knowledge Base Search API", lifespan=lifespan)


# --- Pydantic models ---

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class CheckRequest(BaseModel):
    topic: str

class SearchResult(BaseModel):
    title: str
    file: str
    score: float
    snippet: str

class CheckResponse(BaseModel):
    exists: bool
    note: str | None = None
    score: float | None = None

class RebuildResponse(BaseModel):
    notes_indexed: int
    chunks_created: int


# --- Endpoints ---

@app.post("/search", response_model=list[SearchResult])
def search(req: SearchRequest):
    collection = indexer.get_collection()
    if collection is None:
        return JSONResponse(
            status_code=503,
            content={"error": "Index not built. Run 'python indexer.py build' first."},
        )

    results = collection.query(
        query_texts=[req.query],
        n_results=req.top_k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]
        hits.append(
            SearchResult(
                title=results["metadatas"][0][i]["title"],
                file=results["metadatas"][0][i]["file_path"],
                score=round(1 - distance, 4),
                snippet=results["documents"][0][i][:200],
            )
        )
    return hits


@app.post("/check", response_model=CheckResponse)
def check(req: CheckRequest):
    collection = indexer.get_collection()
    if collection is None:
        return JSONResponse(
            status_code=503,
            content={"error": "Index not built. Run 'python indexer.py build' first."},
        )

    results = collection.query(
        query_texts=[req.topic],
        n_results=10,
        include=["metadatas", "distances"],
    )

    # Aggregate by note (file_path), keep best score per note
    best_by_note: dict[str, dict] = {}
    for i in range(len(results["ids"][0])):
        meta = results["metadatas"][0][i]
        fp = meta["file_path"]
        score = 1 - results["distances"][0][i]
        if fp not in best_by_note or score > best_by_note[fp]["score"]:
            best_by_note[fp] = {"title": meta["title"], "score": score}

    if not best_by_note:
        return CheckResponse(exists=False)

    best = max(best_by_note.values(), key=lambda x: x["score"])
    return CheckResponse(
        exists=best["score"] >= 0.60,
        note=best["title"],
        score=round(best["score"], 4),
    )


@app.post("/index/rebuild", response_model=RebuildResponse)
def rebuild():
    notes, chunks = indexer.build_index()
    return RebuildResponse(notes_indexed=notes, chunks_created=chunks)
