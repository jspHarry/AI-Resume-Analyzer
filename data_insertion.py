from mongodb_connect import get_mongo_connection

def insert_user_data_mongo(resume_data, resume_score, timestamp, reco_field, cand_level, recommended_skills, rec_course):
    db = get_mongo_connection()
    collection = db['user_data']  # Collection name

    data = {
        "name": resume_data['name'],
        "email": resume_data['email'],
        "resume_score": resume_score,
        "timestamp": timestamp,
        "total_pages": resume_data['no_of_pages'],
        "predicted_field": reco_field,
        "user_level": cand_level,
        "actual_skills": resume_data['skills'],
        "recommended_skills": recommended_skills,
        "recommended_courses": rec_course
    }
    collection.insert_one(data)


def fetch_all_users():
    db = get_mongo_connection()
    collection = db['user_data']
    return list(collection.find({}, {'_id': 0}))  # Exclude _id if not needed
