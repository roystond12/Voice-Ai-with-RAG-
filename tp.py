import chromadb

# Initialize the client (Persistent or Ephemeral)
client = chromadb.PersistentClient(path="./chroma_db")

# Get your collection
collection = client.get_collection(name="vectorDB")

# Count the records
record_count = collection.count()
print(f"Total records in collection: {record_count}")