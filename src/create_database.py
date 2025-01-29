from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
import shutil

# ------------------------------------------------------------------------------
# Build absolute paths relative to THIS script file
# ------------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
CHROMA_PATH = SCRIPT_DIR.parent / "chroma"
DATA_PATH = SCRIPT_DIR.parent / "data"


def main():
    generate_data_store()

def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)

def load_documents():
    # Use '**/*.md' with recursive=True
    loader = DirectoryLoader(
        str(DATA_PATH),
        glob="**/*.md",
        recursive=True
    )
    documents = loader.load()
    return documents

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    # debug usage
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # debug usage
    # Only print chunk 10 if it exists
    if len(chunks) > 10:
        document = chunks[10]
        print(document.page_content)
        print(document.metadata)

    return chunks

def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Use local embeddings
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma.from_documents(
        chunks,
        embedding_model,
        persist_directory=str(CHROMA_PATH)
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

if __name__ == "__main__":
    main()
