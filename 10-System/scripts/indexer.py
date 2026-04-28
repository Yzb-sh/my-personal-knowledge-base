"""ChromaDB Indexing Engine for Personal Knowledge Base.

Indexes Markdown notes by splitting on ## headings into chunks,
embedding with a multilingual sentence-transformers model, and
storing in a persistent ChromaDB collection with cosine similarity.

Usage:
    python indexer.py build   # full rebuild
    python indexer.py update  # incremental update (hash-based)
"""

import hashlib
import json
import re
import sys
from pathlib import Path

import chromadb
import frontmatter
from chromadb.utils import embedding_functions

VAULT_ROOT = Path(__file__).resolve().parent.parent.parent
CHROMA_DIR = VAULT_ROOT / "10-System" / "scripts" / "chroma_data"
HASH_FILE = CHROMA_DIR / "file_hashes.json"
INDEX_DIRS = ["03-Zettel", "02-Source", "01-Atlas"]
COLLECTION_NAME = "kb_notes"
BATCH_SIZE = 100

# Local model path (downloaded via modelscope to avoid HuggingFace SSL issues).
# Falls back to the HuggingFace model name if the local path doesn't exist.
_LOCAL_MODEL = (
    "C:/Users/yzb/.cache/modelscope"
    "/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
EMBEDDING_MODEL = _LOCAL_MODEL if Path(_LOCAL_MODEL).exists() else "paraphrase-multilingual-MiniLM-L12-v2"

_embedding_fn = None


def get_embedding_fn():
    """Lazy singleton for the sentence-transformers embedding function."""
    global _embedding_fn
    if _embedding_fn is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        print("Embedding model loaded.")
    return _embedding_fn


def _load_hashes() -> dict:
    if HASH_FILE.exists():
        return json.loads(HASH_FILE.read_text(encoding="utf-8"))
    return {}


def _save_hashes(hashes: dict):
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    HASH_FILE.write_text(
        json.dumps(hashes, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _file_hash(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _scan_files() -> list[Path]:
    files = []
    for dir_name in INDEX_DIRS:
        d = VAULT_ROOT / dir_name
        if d.exists():
            files.extend(d.rglob("*.md"))
    return sorted(files)


def parse_note(filepath: Path) -> dict | None:
    """Parse a Markdown note into frontmatter metadata and ##-delimited chunks."""
    post = frontmatter.load(str(filepath))
    tags = post.metadata.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    # Extract domain from tags (e.g. "domain/sql" -> "sql")
    domain = ""
    for tag in tags:
        if isinstance(tag, str) and tag.startswith("domain/"):
            domain = tag[len("domain/"):]
            break

    rel_path = filepath.relative_to(VAULT_ROOT).as_posix()

    # Split body by ## headings
    content = post.content
    if not content or not content.strip():
        return None

    parts = re.split(r"^## ", content, flags=re.MULTILINE)
    # First part is before any ## heading (title line + blank lines) -- skip it

    chunks = []
    idx = 0
    for part in parts[1:]:
        part = part.strip()
        if not part:
            continue
        lines = part.split("\n", 1)
        heading = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        if not body:
            continue
        chunks.append({
            "chunk_type": heading,
            "content": f"{heading}\n{body}",
            "chunk_index": idx,
        })
        idx += 1

    if not chunks:
        return None

    return {
        "file_path": rel_path,
        "title": post.metadata.get("title", filepath.stem),
        "tags": ",".join(str(t) for t in tags),
        "domain": domain,
        "chunks": chunks,
    }


def build_index() -> tuple[int, int]:
    """Full rebuild: delete collection, re-create, index all notes.

    Returns (notes_indexed, chunks_created).
    """
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Delete existing collection for a clean slate
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    ef = get_embedding_fn()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        embedding_function=ef,
    )

    files = _scan_files()
    hashes = {}
    total_chunks = 0

    for fp in files:
        parsed = parse_note(fp)
        if parsed is None:
            continue

        hashes[parsed["file_path"]] = _file_hash(fp)
        ids = []
        documents = []
        metadatas = []

        for chunk in parsed["chunks"]:
            ids.append(f"{parsed['file_path']}::{chunk['chunk_index']}")
            documents.append(chunk["content"])
            metadatas.append({
                "file_path": parsed["file_path"],
                "title": parsed["title"],
                "tags": parsed["tags"],
                "domain": parsed["domain"],
                "chunk_type": chunk["chunk_type"],
            })
            total_chunks += 1

        # Batch add
        for i in range(0, len(ids), BATCH_SIZE):
            collection.add(
                ids=ids[i : i + BATCH_SIZE],
                documents=documents[i : i + BATCH_SIZE],
                metadatas=metadatas[i : i + BATCH_SIZE],
            )

    _save_hashes(hashes)
    notes_count = len(hashes)
    print(f"Index built: {notes_count} notes, {total_chunks} chunks")
    return notes_count, total_chunks


def update_index():
    """Incremental update: compare file hashes, update changed/new/deleted."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = get_embedding_fn()

    try:
        collection = client.get_collection(
            name=COLLECTION_NAME, embedding_function=ef
        )
    except ValueError:
        print("No existing collection found. Running full build...")
        build_index()
        return

    old_hashes = _load_hashes()
    files = _scan_files()

    current_hashes = {}
    for fp in files:
        rel = fp.relative_to(VAULT_ROOT).as_posix()
        current_hashes[rel] = _file_hash(fp)

    current_paths = set(current_hashes.keys())
    old_paths = set(old_hashes.keys())

    new_files = current_paths - old_paths
    deleted_files = old_paths - current_paths
    changed_files = {
        p for p in current_paths & old_paths
        if current_hashes[p] != old_hashes[p]
    }

    if not new_files and not deleted_files and not changed_files:
        print("Index is up to date.")
        return

    # Delete chunks for changed and deleted files
    for rel in changed_files | deleted_files:
        try:
            collection.delete(where={"file_path": rel})
        except Exception:
            pass

    # Re-index new and changed files
    total_new_chunks = 0
    for rel in new_files | changed_files:
        fp = VAULT_ROOT / rel
        parsed = parse_note(fp)
        if parsed is None:
            continue

        ids = []
        documents = []
        metadatas = []
        for chunk in parsed["chunks"]:
            ids.append(f"{parsed['file_path']}::{chunk['chunk_index']}")
            documents.append(chunk["content"])
            metadatas.append({
                "file_path": parsed["file_path"],
                "title": parsed["title"],
                "tags": parsed["tags"],
                "domain": parsed["domain"],
                "chunk_type": chunk["chunk_type"],
            })
            total_new_chunks += 1

        if ids:
            collection.add(ids=ids, documents=documents, metadatas=metadatas)

    # Update hashes
    new_hashes = dict(old_hashes)
    for rel in new_files | changed_files:
        new_hashes[rel] = current_hashes[rel]
    for rel in deleted_files:
        new_hashes.pop(rel, None)
    _save_hashes(new_hashes)

    print(
        f"Updated: {len(new_files)} added, {len(changed_files)} changed, "
        f"{len(deleted_files)} deleted, {total_new_chunks} new chunks"
    )


def get_collection():
    """Return the existing ChromaDB collection, or None if not built yet."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = get_embedding_fn()
    try:
        return client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
    except ValueError:
        return None


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("build", "update"):
        print("Usage: python indexer.py [build|update]")
        sys.exit(1)

    if sys.argv[1] == "build":
        build_index()
    else:
        update_index()
