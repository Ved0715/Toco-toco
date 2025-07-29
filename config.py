
import os 
import dotenv

dotenv.load_dotenv()



class Config:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.embedding_dimension = int(os.getenv('EMBEDDING_DIMENSIONS', '3072'))
        self.embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-large')
      