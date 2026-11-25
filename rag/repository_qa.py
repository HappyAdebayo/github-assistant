from rag.vector_store import create_vector_store
from rag.retrieval import semantic_search, reciprocal_rank_fusion
from rag.bm25_search import BM25Search
from rag.reranking import CrossEncoderReranker
from langchain_core.documents import Document

def retrieve_repository_context(owner, repo, question, k=10):
    repository = f"{owner}/{repo}"

    vector_store = create_vector_store()

    # 1. Retrieve repository chunks for BM25
    chunks = get_repository_chunks(
        vector_store,
        repository
    )

    # 2. Semantic search
    semantic_results = vector_store.similarity_search_with_score(
        question,
        k=k,
        filter={"repository": repository}
    )

    # 3. BM25 search
    bm25 = BM25Search(chunks)
    bm25_results = bm25.search(question, k=k)

    # 4. Combine search results using RRF
    fused_results = reciprocal_rank_fusion(
        [semantic_results, bm25_results]
    )

    # 5. Rerank candidates
    reranker = CrossEncoderReranker()

    reranked_results = reranker.rerank(
        query=question,
        documents=fused_results,
        top_n=5
    )

    return reranked_results

def get_repository_chunks(vector_store, repository):
    result = vector_store.get(
        where={"repository": repository},
        include=["documents", "metadatas"]
    )

    return [
        Document(
            page_content=content,
            metadata=metadata
        )
        for content, metadata in zip(
            result["documents"],
            result["metadatas"]
        )
    ]


def build_repository_context(results):
    context = []

    for index, (document, score) in enumerate(results, start=1):
        file_path = document.metadata["file_path"]
        start_line = document.metadata["start_line"]
        end_line = document.metadata["end_line"]

        context.append(
            f"""
                Source {index}
                File: {file_path}
                Lines: {start_line}-{end_line}

                Code:
                {document.page_content}
                """
                        )

    return "\n\n".join(context)


def ask_repository(owner, repo, question):
    try:
        results = retrieve_repository_context(
            owner=owner,
            repo=repo,
            question=question
        )

        if not results:
            return {
                "success": False,
                "message": "No relevant code or documentation was found."
            }

        context = build_repository_context(results)

        return {
            "success": True,
            "repository": f"{owner}/{repo}",
            "question": question,
            "context": context
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        return {
            "success": False,
            "message": f"Repository search failed: {str(e)}"
        }