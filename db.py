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

if __name__ == '__main__':
    jobs = fetch_all_jobs()
    print(f"Found {len(jobs)} jobs")