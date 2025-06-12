import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found! Check your .env file")

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
    SimpleDirectoryReader
)
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

class LlamaIndexAgent:
    def __init__(self, rebuild_index=False):
        # Configure the LLM and embeddings
        Settings.llm = OpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0.1)
        Settings.embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY)
        Settings.chunk_size = 1024
        Settings.chunk_overlap = 20

        self.index_dir = "indexes"
        self.docs_dir = "data/people_docs"

        # Create directories if they don't exist
        os.makedirs(self.index_dir, exist_ok=True)
        os.makedirs(self.docs_dir, exist_ok=True)

        if rebuild_index or not os.path.exists(os.path.join(self.index_dir, "index_store.json")):
            print("[LlamaIndexAgent] Building index from documents...")
            try:
                documents = SimpleDirectoryReader(self.docs_dir).load_data()
                if not documents:
                    print("[LlamaIndexAgent] No documents found, creating empty index")
                    # Create a simple document if none exist
                    from llama_index.core import Document
                    documents = [Document(text="No documents available yet. Please add documents to the data/people_docs directory.")]
                
                self.index = VectorStoreIndex.from_documents(documents)
                self.index.storage_context.persist(persist_dir=self.index_dir)
                print(f"[LlamaIndexAgent] Index created with {len(documents)} documents")
            except Exception as e:
                print(f"[LlamaIndexAgent] Error building index: {e}")
                # Create a fallback empty index
                from llama_index.core import Document
                documents = [Document(text="Error loading documents. Please check your document directory.")]
                self.index = VectorStoreIndex.from_documents(documents)
        else:
            print("[LlamaIndexAgent] Loading existing index...")
            try:
                storage_context = StorageContext.from_defaults(persist_dir=self.index_dir)
                self.index = load_index_from_storage(storage_context)
                print("[LlamaIndexAgent] Index loaded successfully")
            except Exception as e:
                print(f"[LlamaIndexAgent] Error loading index: {e}")
                # Rebuild if loading fails
                self.__init__(rebuild_index=True)
                return

        self.query_engine = self.index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact"
        )

    def query_knowledge(self, question: str) -> str:
        print(f"[LlamaIndexAgent] Question: {question}")
        try:
            response = self.query_engine.query(question)
            answer = str(response)
            print(f"[LlamaIndexAgent] Answer: {answer}")
            return answer
        except Exception as e:
            print(f"[LlamaIndexAgent] Error querying: {e}")
            return f"I encountered an error while searching for information: {str(e)}"

# Example usage (for testing)
if __name__ == "__main__":
    try:
        agent = LlamaIndexAgent(rebuild_index=True)
        response = agent.query_knowledge("What is this company about?")
        print(f"[LlamaIndexAgent] Response: {response}")
    except Exception as e:
        print(f"[LlamaIndexAgent] Test failed: {e}")