from connectors.vector_db_connector import ChromaDB

def ingest_documents(pdf_path, pdf_collection_name):
    client = ChromaDB()
    print(f"Ingesting {client.pdf_path}")
    client.ingest_documents(pdf_path=pdf_path, collection_name=pdf_collection_name)

if __name__ == "__main__":
    pdf_path='data/ventilation_doc.pdf'
    ingest_documents(pdf_path=pdf_path, pdf_collection_name="pdf_collection")
