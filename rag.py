import os
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None
_index = None
_chunks = []


def get_model():
    global _model

    if _model is None:
        print("Loading RAG embedding model...")
        _model = SentenceTransformer(MODEL_NAME)
        print("RAG embedding model loaded.")

    return _model


def load_documents():
    documents = []

    if not KNOWLEDGE_DIR.exists():
        return documents

    for file_path in KNOWLEDGE_DIR.glob("*.txt"):
        try:
            text = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            if text.strip():
                documents.append({
                    "source": file_path.name,
                    "text": text
                })

        except Exception as exc:
            print(f"Could not read {file_path}: {exc}")

    return documents


def chunk_text(text, chunk_size=700, overlap=100):
    words = text.split()

    chunks = []

    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk.strip())

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def build_knowledge_base():
    global _index
    global _chunks

    documents = load_documents()

    if not documents:
        print("No RAG documents found.")
        return False

    all_chunks = []

    for document in documents:
        document_chunks = chunk_text(document["text"])

        for chunk in document_chunks:
            all_chunks.append({
                "source": document["source"],
                "text": chunk
            })

    if not all_chunks:
        print("No chunks were created.")
        return False

    model = get_model()

    texts = [item["text"] for item in all_chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    _index = index
    _chunks = all_chunks

    print("\n========================================")
    print("RAG KNOWLEDGE BASE READY")
    print("========================================")
    print("Documents:", len(documents))
    print("Chunks:", len(_chunks))
    print("Embedding dimension:", dimension)
    print("========================================\n")

    return True


def retrieve(query, top_k=4):
    global _index
    global _chunks

    if _index is None or not _chunks:
        build_knowledge_base()

    if _index is None or not _chunks:
        return []

    model = get_model()

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    scores, indices = _index.search(
        query_embedding,
        min(top_k, len(_chunks))
    )

    results = []

    for score, index in zip(scores[0], indices[0]):

        if index < 0:
            continue

        chunk = _chunks[index]

        results.append({
            "source": chunk["source"],
            "text": chunk["text"],
            "score": float(score)
        })

    return results


def format_context(results):
    if not results:
        return "No relevant knowledge was retrieved."

    context_parts = []

    for i, result in enumerate(results, start=1):
        context_parts.append(
            f"[Source {i}: {result['source']}]\n"
            f"{result['text']}"
        )

    return "\n\n".join(context_parts)


if __name__ == "__main__":
    print("Testing RAG...")

    build_knowledge_base()

    query = "What is RAG and how does it work?"

    results = retrieve(query, top_k=3)

    print("\nQUERY:")
    print(query)

    print("\nRETRIEVED INFORMATION:")

    for result in results:
        print("\n--------------------------------")
        print("Source:", result["source"])
        print("Score:", round(result["score"], 4))
        print(result["text"])