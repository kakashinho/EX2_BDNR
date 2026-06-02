import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("USER")
password = os.getenv("PASSWORD")
uri = f'mongodb+srv://{user}:{password}@cluster0.zs9maic.mongodb.net/?retryWrites=true&w=majority'

client = MongoClient(uri, server_api=ServerApi('1'))

db = client.mercadolivre