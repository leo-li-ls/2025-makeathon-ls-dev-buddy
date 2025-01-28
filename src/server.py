import argparse
from pathlib import Path

from flask import Flask, request, jsonify
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
import os

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

---

What you should respond is the answer text itself, don't included "Answer: " as the beginning of your response.
"""

app = Flask(__name__)

# Initialize embeddings and Chroma DB once
embedding_function = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
db = Chroma(
    persist_directory=str(CHROMA_PATH),
    embedding_function=embedding_function
)

# Initialize Ollama LLM
llm = OllamaLLM(model="deepseek-r1:8b")


@app.route("/ask", methods=["POST"])
def ask():
    """
    Expects a JSON payload with {"question": "<user query>"}
    Returns a JSON response with {"answer": "<LLM response>"}
    """
    data = request.get_json(silent=True)
    if not data or "question" not in data:
        return jsonify({"error": "No 'question' provided"}), 400

    query_text = data["question"]
    results = db.similarity_search_with_relevance_scores(query_text, k=5)

    if len(results) == 0 or results[0][1] < 0.5:
        return jsonify({"answer": "No matching results found"}), 200

    context_text = "\n\n---\n\n".join([doc.page_content for doc, score in results])

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    response_text = llm.predict(prompt)

    # Clean up the response by removing <think> blocks
    if '</think>' in response_text:
        # Split on closing tag and take everything after it
        cleaned_response = response_text.split('</think>', 1)[1]
        # Remove leading/trailing whitespace and newlines
        cleaned_response = cleaned_response.lstrip('\n').strip()
    else:
        cleaned_response = response_text.strip()

    return jsonify({"answer": cleaned_response})


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=True)
