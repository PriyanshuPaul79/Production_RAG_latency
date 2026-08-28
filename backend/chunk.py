import os
import chromadb
from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding 


print("loading vector store...")


chroma_client = chromadb.PersistentClient(path="./chroma_db")
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=150)


collection = chroma_client.get_or_create_collection(
    name="my_docs"
)

print("Vector store loaded successfully.")


def ingest_docs(file_id:str, file_path:str, filename:str, file_db:dict):
    """
    Ingests documents into the vector store.
    """
    print(f"--- INGESTION STARTED for file_id: {file_id} ---")
    
    try:
        # Read the documents
        file_db[file_id]["status"]="reading"
        reader = SimpleDirectoryReader(input_files=[file_path])
        documents = reader.load_data()
        #chunking 
        file_db[file_id]["status"]="checking"
        nodes= node_parser.get_nodes_from_documents(documents)
        print("created chunks")


        file_db[file_id]["status"]="embedding"

        chunk_id=[]
        chunk_text=[]
        chunk_metadatas=[]

        for i, node in enumerate(nodes):
            chunk_id.append(f"{file_id}_chunk_{i}")
            chunk_text.append(node.get_content())

            metadata = node.metadata.copy()
            metadata["file_id"]=file_id
            metadata["filename"]=filename
            chunk_metadatas.append(metadata)

        collection.add(
            ids=chunk_id,
            documents=chunk_text,
            metadatas=chunk_metadatas
        )


        file_db[file_id]["status"] = "ready"
        file_db[file_id]["message"] = f"Successfully processed {len(nodes)} chunks."
        print(f"--- INGESTION FINISHED for file_id: {file_id} ---")

    except Exception as e:
        file_db[file_id]["status"] = "failed"
        file_db[file_id]["message"] = f"Error: {str(e)}"
        print(f"--- INGESTION FAILED: {e} ---")
    
       