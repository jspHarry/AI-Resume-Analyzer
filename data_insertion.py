# from mongodb_connect import get_mongo_connection

# def insert_user_data_mongo(resume_data, resume_score, timestamp, reco_field, cand_level, recommended_skills, rec_course):
#     db = get_mongo_connection()
#     collection = db['user_data']  # Collection name

#     data = {
#         "name": resume_data['name'],
#         "email": resume_data['email'],
#         "resume_score": resume_score,
#         "timestamp": timestamp,
#         "total_pages": resume_data['no_of_pages'],
#         "predicted_field": reco_field,
#         "user_level": cand_level,
#         "actual_skills": resume_data['skills'],
#         "recommended_skills": recommended_skills,
#         "recommended_courses": rec_course
#     }
#     collection.insert_one(data)


# def fetch_all_users():
#     db = get_mongo_connection()
#     collection = db['user_data']
#     return list(collection.find({}, {'_id': 0}))  # Exclude _id if not needed


from mongodb_connect import get_mongo_connection

# Function to insert user data
def insert_user_data_mongo(resume_data, resume_score, timestamp, reco_field, cand_level, recommended_skills, rec_course):
    db = get_mongo_connection()
    
    if db is None:
        print("❌ MongoDB connection failed. Data not inserted.")
        return

    collection = db['user_data']  # Collection name

    data = {
        "name": resume_data.get('name'),
        "email": resume_data.get('email'),
        "resume_score": resume_score,
        "timestamp": timestamp,
        "total_pages": resume_data.get('no_of_pages'),
        "predicted_field": reco_field,
        "user_level": cand_level,
        "actual_skills": resume_data.get('skills', []),
        "recommended_skills": recommended_skills,
        "recommended_courses": rec_course
    }

    try:
        collection.insert_one(data)
        print("✅ Data inserted successfully!")
    except Exception as e:
        print("❌ Error inserting data:", e)


# Function to fetch all users
def fetch_all_users():
    db = get_mongo_connection()
    
    if db is None:
        print("❌ MongoDB connection failed. Cannot fetch data.")
        return []

    collection = db['user_data']
    
    try:
        users = list(collection.find({}, {'_id': 0}))  # Exclude _id if not needed
        print(f"✅ {len(users)} user(s) fetched successfully!")
        return users
    except Exception as e:
        print("❌ Error fetching users:", e)
        return []

