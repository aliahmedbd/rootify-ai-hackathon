from milvus_utils import get_vector_store

query = "What technologies are supported for containerized deployment of FCC application?"
vector_store = get_vector_store()

results = vector_store.similarity_search(query=query, k=3)

print("\n🔍 Search Results:")
for i, res in enumerate(results, 1):
    print(f"\nResult {i}:\n{res.page_content}\n")

