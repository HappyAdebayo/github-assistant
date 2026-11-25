
import hashlib

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


class ChromaDefaultEmbeddings(Embeddings):
    def __init__(self):
        self.embedding_function = DefaultEmbeddingFunction()

    def embed_documents(self, texts):
        embeddings = self.embedding_function(texts)
        return [embedding.tolist() for embedding in embeddings]

    def embed_query(self, text):
        embedding = self.embedding_function([text])[0]
        return embedding.tolist()


def create_vector_store():
    embedding_function = ChromaDefaultEmbeddings()

    vector_store = Chroma(
        collection_name="github_repository",
        embedding_function=embedding_function,
        persist_directory="./chroma_db"
    )

    return vector_store


def store_chunks(vector_store, chunks):
    documents = []
    ids = []

    for chunk in chunks:
        file_path = chunk.metadata["file_path"]
        start_index = chunk.metadata["start_index"]

        chunk_id = hashlib.sha256(
            f"{chunk.metadata['repository']}:{file_path}:{start_index}".encode()
        ).hexdigest()

        documents.append(chunk)
        ids.append(chunk_id)

    vector_store.add_documents(
        documents=documents,
        ids=ids
    )

    return len(documents)
