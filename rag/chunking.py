from pathlib import Path

from langchain_text_splitters import (Language, RecursiveCharacterTextSplitter)

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

LANGUAGE_MAP = {
    ".js": Language.JS,
    ".jsx": Language.JS,
    ".ts": Language.TS,
    ".tsx": Language.TS,
    ".py": Language.PYTHON,
    ".md": Language.MARKDOWN,
    ".mdx": Language.MARKDOWN,
    ".html": Language.HTML,
}

def get_splitter(file_path):
    extension = Path(file_path).suffix.lower()

    language = LANGUAGE_MAP.get(extension)

    if language:
        return RecursiveCharacterTextSplitter.from_language(
            language=language,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            add_start_index=True
        )

    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True
    )


def chunk_documents(documents, repository):
    chunks = []

    for document in documents:
        splitter = get_splitter(document["path"])

        metadata = {
            "file_path": document["path"],
            "repository": repository,
            "sha": document["sha"]
        }

        split_docs = splitter.create_documents(
            texts=[document["content"]],
            metadatas=[metadata]
        )

        for chunk in split_docs:
            start_index = chunk.metadata["start_index"]

            end_index = start_index + len(chunk.page_content)

            source_content = document["content"]

            start_line = source_content[:start_index].count("\n") + 1

            end_line = source_content[:end_index].count("\n")

            if end_index == 0 or source_content[end_index - 1] != "\n":
                end_line += 1

            chunk.metadata["start_line"] = start_line
            chunk.metadata["end_line"] = max(start_line, end_line)

        chunks.extend(split_docs)

    return chunks
