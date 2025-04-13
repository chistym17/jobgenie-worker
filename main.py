from embedder import get_embedding
from qdrant_service import init_collection, insert_document, search_similar

if __name__ == "__main__":
    init_collection()

    text = "Qdrant is a vector database"
    embedding = get_embedding(text)
    print(embedding[:10])
    insert_document(id=1, embedding=embedding, payload={"text": text})

    query = "Database for embeddings"
    query_embedding = get_embedding(query)
    results = search_similar(query_embedding)

    print("Top matches:")
    for hit in results:
        print(f"Score: {hit.score:.4f}, Payload: {hit.payload}")
