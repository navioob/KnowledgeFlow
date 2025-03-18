from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

def chunker(seq, batch_size):
  return (seq[pos:pos + batch_size] for pos in range(0, len(seq), batch_size))

class PineconeClient:
    def __init__(self, api_key, index_name):
        self.agent = Pinecone(api_key=api_key)
        self.index = self.agent.Index(index_name)

    
    def upload_vectors(self, list_of_chunks, namespace):
        
        try:
            self.index.upsert(vectors=list_of_chunks, namespace = namespace, async_req=True)
        except Exception as error:
            return {"success":False, "message":f"{error}.Unable to upsert data"}
        # for chunk in chunker(list_of_chunks, batch_size=50)
     

        # Wait for and retrieve responses (in case of error)
        # [async_result.result() for async_result in async_results]

    # serverless index does not support delete by metadata
    def delete_vectors(self, user_id, document_id):

        """
        Delete vectors from Pinecone index based on namespace and document ID metadata
        
        Args:
            namespace (str): Pinecone namespace containing the vectors
            document_id (str): Document ID to match in metadata for deletion
        """

        # Get all vector IDs with the document_id prefix
        vector_ids = []

        # List vectors by prefix
        list_response = self.index.list(
            prefix=document_id,
            namespace=user_id,
        )
        
        # Collect vector IDs
        for ids in list_response:
            if isinstance(ids, list):
                vector_ids.extend(ids)
            else:
                vector_ids.append(ids)
        

        if not vector_ids:
            print(f"No vectors found with prefix: {document_id}")
            return

        # Delete in batches of 1000 (Pinecone's maximum)
        for i in range(0, len(vector_ids), 1000):
            batch_ids = vector_ids[i:i+1000]
            self.index.delete(ids=batch_ids, namespace=user_id)
        
        print(f"Deleted {len(vector_ids)} vectors with prefix '{document_id}' in namespace '{user_id}'")

