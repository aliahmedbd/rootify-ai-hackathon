from milvus_utils import get_vector_store

query = "What technologies are supported for containerized deployment of FCC application?"
vector_store = get_vector_store()

results = vector_store.similarity_search(query=query, k=3)

print("\n🔍 Search Results:")
for i, res in enumerate(results, 1):
    print(f"\nResult {i}:\n{res.page_content}\n")

# from pymilvus import connections, Collection
# from dotenv import load_dotenv
# import os

# # Load environment variables from .env file
# load_dotenv()

# # Connect to Milvus
# connections.connect(
#     alias="default",
#     uri=f"grpc://{os.environ['grpcHost']}:{os.environ['grpcPort']}",
#     secure=True,
#     user=os.environ['milvusUser'],
#     password=os.environ['milvusPass']
# )
# print("✅ Connected to Milvus!")

# # Name of the existing collection
# collection_name = "DevOpsAssist"

# # Load the collection
# collection = Collection(name=collection_name)
# collection.load()
# print(f"📦 Collection '{collection_name}' loaded.")


# results = collection.query(
#     expr="source != ''",
#     output_fields=["source"],
#     limit=10
# )
# print(results)