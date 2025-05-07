# from connectors.vector_db_connector import ChromaDB

# def ingest_documents(pdf_path, pdf_collection_name):
#     client = ChromaDB()
#     print(f"Ingesting {client.pdf_path}")
#     client.ingest_documents(pdf_path=pdf_path, collection_name=pdf_collection_name)

# if __name__ == "__main__":
#     pdf_path='data/ventilation_doc.pdf'
#     ingest_documents(pdf_path=pdf_path, pdf_collection_name="pdf_collection")
from langchain_community.document_loaders import ConfluenceLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from uuid import uuid4
from milvus_utils import get_vector_store
import os

loader = ConfluenceLoader(
    url=os.getenv("confluenceURL"),
    username=os.getenv("confluenceUSERNAME"),
    api_key=os.getenv("confluence_APIKEY"),
    space_key=os.getenv("confluence_SPACEKEY"),
    include_attachments=True,
    limit=50
)
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=200)
texts = text_splitter.split_documents(documents)
uuids = [str(uuid4()) for _ in texts]

vector_store = get_vector_store(drop_old=True)
vector_store.add_documents(documents=texts, ids=uuids)
print("✅ Documents successfully added")