import argparse
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import openai
import os


# ------------------------------------------------------------------------------
# Build absolute paths relative to THIS script file
# ------------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent

# If your top-level folder has "chroma/" at the same level as "src/", do:
CHROMA_PATH = SCRIPT_DIR.parent / "chroma"

# Load environment variables if still using OpenAI for chat
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # If you want local embeddings for the DB search:
    embedding_function = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = Chroma(
        persist_directory=str(CHROMA_PATH),
        embedding_function=embedding_function
    )

    # Search the DB
    results = db.similarity_search_with_relevance_scores(query_text, k=5)

    # Threshold check
    if len(results) == 0 or results[0][1] < 0.5:
        print("Unable to find matching results.")
        return

    # Build the context text from the top matches
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # Prepare the prompt
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    print(prompt)

    # Use OpenAI for chat (can be replaced with a local LLM if desired)
    model = ChatOpenAI()
    response_text = model.predict(prompt)

    # Show sources (file metadata)
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)

if __name__ == "__main__":
    main()
