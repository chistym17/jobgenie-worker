import time
import json
from datetime import datetime
from job_crawler import JobCrawler
from llm_processor import JobLLMProcessor
from db import fetch_all_jobs
import asyncio
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

REQUESTS_PER_MINUTE = 10
MINUTE = 60
RATE_LIMIT_DELAY = MINUTE / REQUESTS_PER_MINUTE

class JobProcessor:
    def __init__(self):
        """Initialize the job processing pipeline"""
        self.crawler = JobCrawler()
        self.llm_processor = JobLLMProcessor()
        self.processed_jobs = []
        self.failed_jobs = []
        self.start_time = None
        self.end_time = None

    def _log(self, message: str):
        """Helper method to log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    async def process_job(self, job: Dict) -> None:
        """Process a single job with rate limiting"""
        job_id = job.get('_id')
        job_title = job.get('title', 'Unknown')
        
        self._log(f"Starting to process job: {job_title}")
        
        try:
            self._log(f"Scraping URL: {job['url']}")
            scrape_result = self.crawler.scrape_job_details(job['url'])
            
            if not scrape_result:
                self._log(f"Failed to scrape job: {job_title}")
                self.failed_jobs.append({
                    'id': job_id,
                    'title': job_title,
                    'error': 'Scraping failed'
                })
                return

            self._log(f"Processing with LLM: {job_title}")
            processed_data = self.llm_processor.process_job_posting(scrape_result)
            
            self.processed_jobs.append({
                'id': job_id,
                'title': job_title,
                'data': processed_data,
                'status': 'success'
            })
            
        except Exception as e:
            self._log(f"Error processing job {job_title}: {str(e)}")
            self.failed_jobs.append({
                'id': job_id,
                'title': job_title,
                'error': str(e)
            })
        
        time.sleep(RATE_LIMIT_DELAY)

    async def process_and_upload_jobs(self) -> None:
        """Run the entire job processing pipeline"""
        self.start_time = datetime.now()
        self._log("Starting job processing pipeline...")

        try:
            jobs = fetch_all_jobs()
            self._log(f"Found {len(jobs)} jobs in MongoDB")
            
            jobs_to_process = jobs[:5]
            self._log(f"Processing first {len(jobs_to_process)} jobs for testing")
            
            for job in jobs_to_process:
                await self.process_job(job)

            with open('processed_jobs.txt', 'w') as f:
                for job in self.processed_jobs:
                    f.write("\n" + "="*80 + "\n")
                    f.write(f"Job ID: {job['id']}\n")
                    f.write(f"Title: {job['title']}\n")
                    f.write("\nProcessed Data:\n")
                    for key, value in job['data'].items():
                        f.write(f"- {key}: {value}\n")
                    f.write("\n")
            
            with open('failed_jobs.txt', 'w') as f:
                for job in self.failed_jobs:
                    f.write("\n" + "="*80 + "\n")
                    f.write(f"Job ID: {job['id']}\n")
                    f.write(f"Title: {job['title']}\n")
                    f.write(f"Error: {job['error']}\n")

        except Exception as e:
            self._log(f"Pipeline failed with error: {str(e)}")
        finally:
            self.end_time = datetime.now()
            self._log("\nPipeline Summary:")
            self._log(f"Total jobs processed: {len(self.processed_jobs)}")
            self._log(f"Total jobs failed: {len(self.failed_jobs)}")
            self._log(f"Total time taken: {self.end_time - self.start_time}")

if __name__ == '__main__':
    processor = JobProcessor()
    asyncio.run(processor.process_and_upload_jobs())