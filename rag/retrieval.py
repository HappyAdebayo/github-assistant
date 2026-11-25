
def semantic_search(vector_store, query, k=5):
    results = vector_store.similarity_search_with_score(
        query,
        k=k
    )

    return results

def reciprocal_rank_fusion(search_results, k=60):
    fused_scores = {}
    documents = {}

    for results in search_results:
        for rank, (document, score) in enumerate(results, start=1):
            doc_id = (
                document.metadata["repository"],
                document.metadata["file_path"],
                document.metadata["start_index"]
            )

            if doc_id not in fused_scores:
                fused_scores[doc_id] = 0
                documents[doc_id] = document

            fused_scores[doc_id] += 1 / (k + rank)

    ranked_ids = sorted(
        fused_scores,
        key=fused_scores.get,
        reverse=True
    )

    return [
        (documents[doc_id], fused_scores[doc_id])
        for doc_id in ranked_ids
    ]


def filter_by_metadata(documents, repository=None, file_path=None):
    filtered_documents = []

    for document, score in documents:
        metadata = document.metadata

        if repository and metadata.get("repository") != repository:
            continue

        if file_path and not metadata.get("file_path", "").startswith(file_path):
            continue

        filtered_documents.append((document, score))

    return filtered_documents
