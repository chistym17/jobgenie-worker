import requests
import time
from datetime import datetime

def test_recommendation_performance():
    # API endpoints
    base_url = "http://localhost:8000"
    recommendations_url = f"{base_url}/recommendations"
    status_url = f"{base_url}/recommendations/{{task_id}}"
    
    # Test data
    test_email = "demouser17@gmail.com"
    
    # Start timing
    start_time = time.time()
    print(f"Starting test at: {datetime.now().isoformat()}")
    
    # Make initial request
    print("Making initial request...")
    response = requests.post(
        recommendations_url,
        json={"email": test_email}
    )
    
    if response.status_code != 200:
        print(f"Error in initial request: {response.text}")
        return
    
    task_id = response.json().get("task_id")
    print(f"Task ID received: {task_id}")
    
    # Poll for results
    max_attempts = 60  # 5 minutes maximum
    attempt = 0
    
    while attempt < max_attempts:
        status_response = requests.get(status_url.format(task_id=task_id))
        
        if status_response.status_code != 200:
            print(f"Error checking status: {status_response.text}")
            break
            
        status_data = status_response.json()
        
        if status_data.get("status") == "completed":
            end_time = time.time()
            total_time = end_time - start_time
            print(f"\nTest completed!")
            print(f"Total time taken: {total_time:.2f} seconds")
            print(f"Number of attempts: {attempt + 1}")
            return
            
        print(f"Attempt {attempt + 1}: Status - {status_data.get('status')}")
        time.sleep(5)  # Wait 5 seconds between attempts
        attempt += 1
    
    print("Test timed out after maximum attempts")

if __name__ == "__main__":
    test_recommendation_performance() 