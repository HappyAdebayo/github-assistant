
from rag.vector_store import create_vector_store
from rag.retrieval import semantic_search

vector_store = create_vector_store()

query = "const pool = new Pool connectionString process.env.DATABASE_URL"

results = semantic_search(vector_store, query)

for index, (document, score) in enumerate(results, start=1):
    print(f"\nResult {index}")
    print(f"File: {document.metadata['file_path']}")
    print(f"Distance: {score}")
    print(f"Content:\n{document.page_content}")
