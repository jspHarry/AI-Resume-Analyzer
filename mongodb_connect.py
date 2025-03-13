# from pymongo import MongoClient

# def get_mongo_connection():
#     # Replace this URL with your MongoDB URI
#     client = MongoClient("mongodb+srv://jaspinder0029:harry2299@cluster0.r18ki.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # or your cloud MongoDB URI
#     db = client['resume_analysis']  # Database name
#     return db

from pymongo import MongoClient
import certifi

def get_mongo_connection():
    """
    Establish connection to MongoDB Atlas with SSL certificate validation.
    Returns the 'resume_analysis' database instance.
    """
    try:
        client = MongoClient(
            "mongodb+srv://jaspinder0029:harry2299@cluster0.r18ki.mongodb.net/?retryWrites=true&w=majority&tls=true&appName=Cluster0",
            tlsCAFile=certifi.where(),  # Ensure proper SSL cert is used
            serverSelectionTimeoutMS=5000  # 5-second timeout for connection
        )
        db = client['resume_analysis']
        
        # Test connection (optional but recommended)
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")

        return db

    except Exception as e:
        print("❌ Error connecting to MongoDB:", e)
        return None  # or handle appropriately

