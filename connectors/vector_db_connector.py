from langchain_milvus import Milvus
from langchain_ibm.embeddings import WatsonxEmbeddings
import os


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

    def get_embedding_model(self):
        return WatsonxEmbeddings(
            model_id=self.em_model,
            url=os.environ['WATSONX_URL'],
            project_id=os.environ["WATSONX_PROJECT_ID"],
            apikey=os.environ['WATSONX_APIKEY']
        )

    def get_vector_store(self, collection_name="DevOpsAssist", drop_old=False):
        embeddings = self.get_embedding_model()
        self.milvus = Milvus(
            collection_name=collection_name,
            embedding_function=embeddings,
            connection_args={
                "uri": self.milvus_uri,
                "user": self.milvus_user,
                "password": self.milvus_password,
                "secure": True
            },
            index_params=self.milvus_index_params,
            consistency_level="Strong",
            drop_old=drop_old
        )
        return self.milvus
    
    def similarity_search(self, query, k=3):
        """
        Conduct a similarity search on the vector store for the selected collection.
        """
        if self.milvus is None:
            vector_store = self.get_vector_store()
        else:
            vector_store = self.milvus
            
        # Perform the similarity search
        results = vector_store.similarity_search(query=query, k=k)
        return results
