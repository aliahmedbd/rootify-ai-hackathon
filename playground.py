import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from uuid import uuid4
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_milvus import Milvus



def createEmbeddings():
    
    outputPath = os.environ["outputDir"]

    loader = DirectoryLoader(outputPath, glob="./*.md")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    uuids = [str(uuid4()) for _ in range(len(texts))]
    embeddings = HuggingFaceEmbeddings(model_name=os.environ["emModel"])
    db_file = os.environ["dbLocation"] + os.environ["dbFileName"]
    print(f"The vector database will be saved to {db_file}")

    # Construct the correct gRPC URI (ensure it's a string, not a tuple)
    uri = f"https://{os.environ['grpcHost']}:{os.environ['grpcPort']}"
    user = os.environ['user']  # Watsonx user (likely "root" or "ibmlhapikey")
    password = os.environ['password']  # Watsonx API key

    # Now initialize the vector store with LangChain Milvus
    vector_store = Milvus(
        collection_name="ATT",    
        embedding_function=embeddings,
        connection_args={
            "uri": uri,
            "user": user,  # Ensure "user" is used instead of "username"
            "password": password,
            "secure": True  # Set to True if Watsonx requires TLS
        },
        index_params={"index_type": "FLAT", "metric_type": "L2"},
        consistency_level="Strong",
        drop_old=True
    )

    print("Milvus vector store initialized successfully!")

    print("Adding documents to Milvus instance.")
    vector_store.add_documents(documents=texts, ids=uuids)
    print("Documents successfully added")