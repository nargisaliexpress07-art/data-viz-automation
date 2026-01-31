#!/usr/bin/env python3
"""
Queue Manager - Creates render jobs and pushes to GitHub
"""

import json
import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import sys

# Add parent directory to path to import other scripts
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_scraper import DataScraper
from generate_analysis import generate_analysis

load_dotenv()

class QueueManager:
    def __init__(self):
        self.repo_path = os.path.expanduser('~/data-viz-automation')
        self.queue_path = os.path.join(self.repo_path, 'data/render_queue')
    
    def create_render_job(self, data_point, analysis):
        """Create a JSON config file for video rendering"""
        
        video_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        config = {
            'id': video_id,
            'chart_type': data_point.get('chart_type', 'line'),
            'title': data_point['title'],
            'data': data_point['data'],
            'source': data_point['source'],
            'analysis': analysis,
            'created_at': datetime.now().isoformat()
        }
        
        # Save to queue
        config_file = os.path.join(self.queue_path, f'video_{video_id}.json')
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Created render job: {video_id}")
        return video_id
    
    def push_to_github(self):
        """Push queued jobs to GitHub (triggers Actions)"""
        
        os.chdir(self.repo_path)
        
        # Git add
        subprocess.run(['git', 'add', 'data/render_queue/'], check=True)
        
        # Git commit
        commit_msg = f"Queue render jobs - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        try:
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        except subprocess.CalledProcessError:
            print("No new jobs to commit")
            return False
        
        # Git push (this triggers GitHub Actions)
        subprocess.run(['git', 'push'], check=True)
        print("✅ Pushed to GitHub - Actions will start rendering")
        return True
    
    def process_daily_topics(self):
        """Main function: scrape data, generate analysis, queue renders"""
        
        scraper = DataScraper()
        topics = scraper.get_daily_topics()
        
        jobs_created = 0
        
        for topic in topics:
            print(f"\n📊 Processing: {topic['title']}")
            
            # Generate analysis with GPT
            analysis = generate_analysis(topic)
            print(f"💭 Analysis: {analysis}")
            
            # Create render job
            self.create_render_job(topic, analysis)
            jobs_created += 1
        
        if jobs_created > 0:
            # Push all jobs to GitHub at once
            self.push_to_github()
        
        print(f"\n✅ Queued {jobs_created} videos for rendering")

if __name__ == "__main__":
    manager = QueueManager()
    manager.process_daily_topics()
