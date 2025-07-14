from langchain_ibm.embeddings import WatsonxEmbeddings
import os
from pymilvus import connections
from pymilvus import Collection

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings


class MilvusConnector:
    def __init__(self):
        """
        Initialize the Milvus Connector class.
        Establishes a connection to the PostgreSQL database.
        """
        self.milvus_uri = f"grpc://{os.environ['grpcHost']}:{os.environ['grpcPort']}"
        self.milvus_user = os.environ['milvusUser']
        self.milvus_password = os.environ['milvusPass']
        self.milvus_index_params={"index_type": "FLAT", "metric_type": "L2"}
        self.em_model = "ibm/slate-125m-english-rtrvr"

        self.milvus = None

        try:
            conn = connections.connect(
                alias="default",
                uri=f"grpc://{os.environ['grpcHost']}:{os.environ['grpcPort']}",
                user=os.environ['milvusUser'],
                password=os.environ['milvusPass'],
                secure=True
            )
            print("Connected to Milvus successfully.")
            return conn
        
        except Exception as e:
            import traceback
            print("Milvus connection failed.")
            print(traceback.format_exc())


    def get_embedding_model(self):
        return WatsonxEmbeddings(
            model_id=self.em_model,
            url=os.environ['WATSONX_URL'],
            project_id=os.environ["WATSONX_PROJECT_ID"],
            apikey=os.environ['WATSONX_APIKEY']
        )
    

    def search_milvus(self, query_text: str, top_k: int = 3, collection_name: str="DevOpsAssist"):
        # Embed the query text
        embedding_model = self.get_embedding_model()
        query_vector = embedding_model.embed_query(query_text)

        # Load the collection
        collection = Collection(name=collection_name)
        collection.load()

        # Perform search
        search_params = {
            "metric_type": "L2",      # or "IP" or "COSINE" depending on how your index was built
            "params": {"nprobe": 10}  # tune for accuracy/speed
        }

        results = collection.search(
            data=[query_vector],              # query vectors
            anns_field="vector",           # name of the vector field
            param=search_params,
            limit=top_k,
            output_fields=["text"]            # optional: fields to return
        )

        return results



class ChromaDB():

    def __init__(self):
        """
        The ChromaDB pipeline!
        """
        self.embedding_model = "ibm-granite/granite-embedding-30m-english"
        self.persist_directory = "./chroma_db"
        self.embedding_function = HuggingFaceEmbeddings(model_name="ibm-granite/granite-embedding-30m-english")
        self.pdf_path = "data/ventilation_doc.pdf"
    
    def ingest_documents(self, pdf_path, collection_name="pdf_collection", chunk_size=500, chunk_overlap=50):
        # Load the PDF document
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs = text_splitter.split_documents(documents)

        # Create the Chroma vector store
        vectordb = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory
        )

        # Add documents to the vector store
        vectordb.add_documents(docs)

        print(f"Successfully ingested {len(docs)} chunks into Chroma at '{self.persist_directory}'.")

    def search(self, query, collection='pdf_collection'):
        vectordb = Chroma(
        collection_name=collection,
        persist_directory=self.persist_directory,
        embedding_function=self.embedding_function
        )

        return vectordb.similarity_search(query, k=3)
