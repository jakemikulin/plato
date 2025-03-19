from langchain_ollama import OllamaLLM
from langchain_chroma import Chroma  # ✅ FIXED IMPORT
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
import time
import requests

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
Keep responses factual and concise under 500 characters.

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

# 🔹 Function to handle questions
def ask_question(query):
    if not is_ollama_running():
        yield "Error: Ollama is not running. Please start Ollama and try again."
        return

    llm = OllamaLLM(
        model="plato",
        streaming=True
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

    # ✅ Stream the response
    full_response = ""  
    for chunk in llm.stream(final_prompt):
        cleaned_chunk = chunk.replace(" ,", ",").replace(" .", ".").replace(" ?", "?").replace(" !", "!")  # ✅ Remove bad spacing
        cleaned_chunk = " ".join(cleaned_chunk.split())  # ✅ Normalize spaces
        full_response += cleaned_chunk + " "  
        yield cleaned_chunk + " "
    