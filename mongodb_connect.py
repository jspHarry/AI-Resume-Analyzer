from pymongo import MongoClient

def get_mongo_connection():
    # Replace this URL with your MongoDB URI
    client = MongoClient("mongodb+srv://jaspinder0029:harry2299@cluster0.r18ki.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # or your cloud MongoDB URI
    db = client['resume_analysis']  # Database name
    return db
