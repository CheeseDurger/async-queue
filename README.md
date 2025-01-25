# Overview
This repo is a demo for processing a queue of llm tasks asynchronously. It relies on 2 mechanisms:
1. A robust llm client: an llm with rate limit management, fallbacks, retries, timeout
2. A robust queue processing: error handling, max concurrency

# How to run
- Install with `pipenv install`
- Run with `pipenv run python main.py`