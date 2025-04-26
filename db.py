from pymongo import MongoClient

def get_mongodb_client():
    """Create and return MongoDB client connection"""
    client = MongoClient('mongodb://localhost:27018/')
    return client

def fetch_all_jobs():
    """Fetch all jobs from the jobs collection in db-jobgeniem"""
    client = get_mongodb_client()
    db = client['jobs_db']
    collection = db['jobs']
    
    jobs = list(collection.find({}))
    
    client.close()
    
    return jobs

def fetch_single_job_details(job_id:str):
    client=get_mongodb_client()
    db = client['jobs_db']
    collection = db['jobs']

    job=collection.find_one({
        "id":job_id

    })

    client.close()

    return job


def fetch_resume_data(user_email: str) -> dict:
    client = get_mongodb_client()
    db = client['jobs_db']
    collection = db['resumes']
    
    resume = collection.find_one({"user_email": user_email})
    
    client.close()

    return resume

if __name__ == '__main__':
    jobs = fetch_all_jobs()
    resume = fetch_resume_data('demouser17@gmail.com')
    print(f"Found {len(jobs)} jobs")
    print(f"Found {resume} resume")