import argparse
# from dataclasses import dataclass
from langchain_community.vectorstores import Chroma

# Replace OpenAIEmbeddings import with HuggingFaceEmbeddings
# from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings

# You can keep ChatOpenAI if you still want OpenAI-based LLM generation
from langchain_openai import ChatOpenAI

from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import openai
import os


# Load environment variables if you still use OpenAI for chat
load_dotenv()
# If you're no longer using any OpenAI services, you can remove the below lines
openai.api_key = os.environ.get("OPENAI_API_KEY")

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # Prepare the DB with local embeddings.
    embedding_function = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)

    if len(results) == 0 or results[0][1] < 0.5:
        print("Unable to find matching results.")
        return

    # Build the context text from the top matches
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # Prepare the prompt
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    print(prompt)

    # If you want to keep using OpenAI for chat, you can do so here
    model = ChatOpenAI()
    response_text = model.predict(prompt)

    # Show sources, if available
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)


if __name__ == "__main__":
    main()
