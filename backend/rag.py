from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import time

# Load embedding model
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")

# Load ChromaDB retriever
def get_retriever():
    db = Chroma(persist_directory="vectorstore/", embedding_function=embedding_model)
    return db.as_retriever()

# Memory for conversation history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def ask_question(query):
    llm = OllamaLLM(
        model="llama3.2",
        system_prompt=(
            "You are an assistant specialising in mental health resources."
        )
    )
    retriever = get_retriever()

    start_retrieval = time.time()
    docs = retriever.invoke(query)  
    retrieval_time = time.time() - start_retrieval

    print(f"\n⏳ Retrieval Time: {retrieval_time:.2f} seconds")
    print("\n🔍 Retrieved Documents:\n")

    if docs:
        # Format retrieved context more clearly
        context = "\n\n".join([f"Document {i+1}: {doc.page_content}" for i, doc in enumerate(docs[:3])])

        print("\n🔹 Retrieved Context for LLM:\n")
        print(context[:500])  # Print only the first 500 chars for debugging

        prompt = f"""Use the following documents to answer the question:

        {context}

        Question: {query}

        If the documents do not fully answer the question, provide the best possible answer based on general knowledge.
        Keep responses factual and concise.
        """
    else:
        print("❌ No relevant documents found. Using general model response.")
        prompt = f"Answer the following question using general knowledge:\n\nQuestion: {query}"

    print("\n🔹 FINAL PROMPT SENT TO LLM:\n")
    print(prompt)  # Print first 500 chars for debugging

    start_llm = time.time()
    response = llm.invoke(prompt)  
    llm_time = time.time() - start_llm

    print(f"\n⏳ LLM Processing Time: {llm_time:.2f} seconds")

    return response