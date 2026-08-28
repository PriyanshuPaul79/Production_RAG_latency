import chromadb
from rank_bm25 import BM25Okapi
import numpy as np

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="my_docs"
)

def hybrid_ret(question:str, file_id:str, top_k:int):
    """
    Perform Hybrid search here BM25 + semantic search
    """

    print(f"Hybrid Search for {question} in file {file_id} started")

    result = collection.get(
        where={"file_id":file_id},
        include=['documents','metadatas']
    )

    if not result['documents']:
        return []

    documents = result['documents']
    metadatas = result['metadatas']
    ids = result['ids']


    # semantic search 
    sem_result = collection.query(
        query_text=[question],
        n_result=top_k*2,
        where={"file_id":file_id}
    )
    sem_id = sem_result['ids'][0] if sem_result['ids'] else []

    token_docs = [doc.lower()]

