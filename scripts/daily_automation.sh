#!/bin/bash

# Navigate to project directory
cd ~/data-viz-automation

# Load environment variables
export $(cat .env | xargs)

# Run the queue manager
python3 scripts/queue_manager.py

# Log the run
echo "$(date): Daily automation completed" >> logs/automation.log
