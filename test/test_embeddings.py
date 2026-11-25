
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

embedding_function = DefaultEmbeddingFunction()

text = "This function connects to a PostgreSQL database."

embedding = embedding_function([text])

print("Embedding dimensions:", len(embedding[0]))
print("First 10 values:", embedding[0][:10])

