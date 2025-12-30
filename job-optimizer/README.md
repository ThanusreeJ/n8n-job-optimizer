# Job Optimizer - 4 Day Progress Demo

## Overview
This is a simplified version showing 4 days of development progress on the Multi-Agent Production Job Optimizer.

## What's Included (Days 1-4)

### Day 1: Setup
- Project structure
- Data models
- API connection

### Day 2: Baseline Scheduler
- FIFO (First-In-First-Out) scheduler
- Basic web interface
- CSV upload

### Day 3: Batching Agent
- AI logic to group similar jobs
- Minimize setup changes
- Rush order priority

### Day 4: Bottleneck Agent
- Identify overloaded machines
- Balance workload distribution

## Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment:**
   ```bash
   copy .env.template .env
   # Add your GROQ_API_KEY in .env
   ```

3. **Run the App:**
   ```bash
   streamlit run ui/app.py
   ```

## What's NOT Included Yet

- Constraint validation agent
- Full multi-agent orchestration
- Advanced comparison features
- Complete documentation

These are planned for Days 5+.
