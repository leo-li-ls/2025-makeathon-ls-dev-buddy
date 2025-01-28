import argparse
from pathlib import Path

# Vector store and embeddings
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Replace OpenAI with Ollama
from langchain_ollama import OllamaLLM

# Prompt template
from langchain.prompts import ChatPromptTemplate


# ------------------------------------------------------------------------------
# Build absolute paths relative to THIS script file
# ------------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
CHROMA_PATH = SCRIPT_DIR.parent / "chroma"

PROMPT_TEMPLATE = """
Introduction: Answer the question at the end based only on the following context, and only output the answer as response, no need to output your thinking process. PS: Give the most detailed answer, use more than one phrase to answer if possible.

Context:

```text
{context}
```

Question: "{question}"
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # Use local embeddings for the DB search
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

    # Build context from matches
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # Prepare the prompt
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # debug usage
    # print(prompt)

    # Use Ollama as the local LLM
    # (Adjust base_url or model name depending on your Ollama config)
    llm = OllamaLLM(model="deepseek-r1:8b")
    response_text = llm.predict(prompt)

    # Show sources (file metadata)
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)

if __name__ == "__main__":
    main()
