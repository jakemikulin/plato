from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
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

# 🔹 Chat memory for conversation history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# 🔹 Define custom prompt template
prompt_template = """You are an AI assistant specializing in mental health resources.

Previous conversation history:
{chat_history}

Retrieved documents:
{context}

User question: {question}

If the documents do not fully answer the question, provide the best possible answer using general knowledge.
Keep responses factual and concise.
"""

prompt = PromptTemplate(
    template=prompt_template, 
    input_variables=["chat_history", "context", "question"]
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
        return "⚠️ Error: Ollama is not running. Please start Ollama and try again."

    llm = OllamaLLM(
        model="phi4-mini",
        system_prompt="You are an assistant specializing in mental health resources."
    )
    retriever = get_retriever()

    # ✅ FIX: Correctly retrieve documents
    start_retrieval = time.time()
    docs = retriever.invoke(query)  
    retrieval_time = time.time() - start_retrieval
    print(f"\n⏳ Retrieval Time: {retrieval_time:.2f} seconds")

    # If relevant documents are found, format them for context
    if docs:
        context = "\n\n".join([f"Document {i+1}: {doc.page_content}" for i, doc in enumerate(docs[:3])])
        print("\n🔍 Retrieved Context for LLM:\n")
        print(context[:500])  # Print first 500 characters for debugging
    else:
        print("❌ No relevant documents found. Using general model response.")
        context = "No relevant documents found."

    # ✅ FIX: Create question-answering chain separately
    qa_chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)

    # ✅ FIX: Ensure correct input format for ConversationalRetrievalChain
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )

    # ✅ FIX: Invoke with chat history (WITHOUT `input_documents`)
    chat_history = memory.load_memory_variables({}).get("chat_history", "")

    start_llm = time.time()
    response = rag_chain.invoke({
        "question": query,
        "chat_history": chat_history  # ✅ Fix: No `input_documents`
    })
    llm_time = time.time() - start_llm
    print(f"\n⏳ LLM Processing Time: {llm_time:.2f} seconds")

    return response["answer"]  # ✅ Fix: Correct output key
