from langchain_ollama import OllamaLLM
from langchain_chroma import Chroma  # ✅ FIXED IMPORT
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
import time
import requests
import re

# 🔹 Load embedding model
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")

# 🔹 Load ChromaDB retriever
def get_retriever():
    db = Chroma(persist_directory="vectorstore/", embedding_function=embedding_model)
    return db.as_retriever()

# 🔹 Define custom prompt template
prompt_template = """

The following information may be helpful:\n\n
{context}

You do not need to talk about eveything in the helpful information,

User question: {question}

If the context is not relevent provide the best possible answer using what you know.
Keep responses factual.

"""

prompt = PromptTemplate(
    template=prompt_template, 
    input_variables=["context", "question"]
)

# 🔹 Ensure Ollama is running before making requests
def is_ollama_running():
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False
    
    # Function to clean and format text
def clean_text(text):
    """Fix word splits, punctuation, and formatting."""
    # Fix spaces before/after punctuation
    text = re.sub(r"\s+([,.;!?])", r"\1", text)  # Remove space before punctuation
    text = re.sub(r"([(\[])\s+", r"\1", text)  # Fix spaces after opening brackets
    text = re.sub(r"\s+([)\]])", r"\1", text)  # Fix spaces before closing brackets
    text = re.sub(r"(\w)\s*-\s*(\w)", r"\1-\2", text)  # Fix hyphenated words

    # Fix slash formatting issues
    text = re.sub(r"\s*/\s*", r"/", text)  # Remove spaces around slashes

    # Fix single quotes around words (like ' Feeling Good ' → "Feeling Good")
    text = re.sub(r"\s*'\s*(\w.*?)\s*'\s*", r'"\1"', text)

    # Fix email-like splits
    text = re.sub(r"\s*@\s*", "@", text)  # Remove spaces around "@"
    text = re.sub(r"\s*(\.org|\.com|\.net|\.edu)", r"\1", text)  # Fix domain splits

    # Normalize spaces
    text = " ".join(text.split())

    return text

# 🔹 Function to handle questions
def ask_question(query):
    if not is_ollama_running():
        yield "Error: Ollama is not running. Please start Ollama and try again."
        return

    llm = OllamaLLM(
        model="plato",
        streaming=True,
        max_tokens=150
    )
    
    retriever = get_retriever()

    # ✅ Start retrieval (No memory, fresh retrieval per query)
    start_retrieval = time.time()
    docs = retriever.invoke(query)[:3]  # Fetch top 3 relevant documents
    retrieval_time = time.time() - start_retrieval
    print(f"\n⏳ Retrieval Time: {retrieval_time:.2f} seconds")

    if docs:
        context = "\n\n".join([f"{doc.page_content}" for doc in docs])
        print("\n🔍 Retrieved Context for LLM:\n")
        print(context[:500])  # Print first 500 characters for debugging
    else:
        print("No relevant documents found.")
        context = ""

    # ✅ Construct final prompt (NO memory)
    final_prompt = prompt.format(
        context=context,
        question=query
    )

    print("\n🔹 FINAL PROMPT SENT TO LLM:\n")
    print(final_prompt[:500])  # Print first 500 characters for debugging

    # Stream the response
    full_response = ""
    buffer = ""  # ✅ Store incomplete words
    for chunk in llm.stream(final_prompt):
        chunk = chunk.strip()  # ✅ Trim spaces before processing

        # ✅ Merge buffered text with new chunk and split words correctly
        text = buffer + chunk
        words = text.split(" ")  # ✅ Split words properly

        if len(words) > 1:
            buffer = words.pop()  # ✅ Keep last word in buffer if incomplete
        else:
            buffer = ""  # ✅ Clear buffer if all words are complete

        # ✅ Properly format and yield the words
        cleaned_text = " ".join(words)
        cleaned_text = clean_text(cleaned_text)  # Apply formatting fixes

        if cleaned_text:
            yield cleaned_text + " "
            full_response += cleaned_text + " "

    # ✅ Ensure the final buffer is included
    if buffer:
        buffer = clean_text(buffer.strip())  # Final formatting pass
        yield buffer + " "
        full_response += buffer + " "