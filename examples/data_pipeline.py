"""
Example: Data Pipeline Workflow

This example demonstrates a typical ETL (Extract, Transform, Load) pipeline.
"""

from autoflow import Workflow, run, Scheduler, IntervalScheduler
from autoflow.utils import setup_logging

# Setup logging
setup_logging()


# Define node functions
def fetch_data(context):
    """Simulate fetching data from an API."""
    print("Fetching data...")
    return {"records": [1, 2, 3, 4, 5]}


def clean_data(context):
    """Remove invalid records."""
    records = context.get("fetch_data", {}).get("records", [])
    cleaned = [r for r in records if r is not None]
    print(f"Cleaned {len(records)} -> {len(cleaned)} records")
    return {"records": cleaned, "count": len(cleaned)}


def aggregate_data(context):
    """Compute statistics."""
    records = context.get("clean_data", {}).get("records", [])
    total = sum(records)
    avg = total / len(records) if records else 0
    print(f"Total: {total}, Average: {avg:.2f}")
    return {"total": total, "average": avg, "count": len(records)}


def save_results(context):
    """Save to database (simulated)."""
    stats = context.get("aggregate_data", {})
    print(f"Saving results: {stats}")
    return {"saved": True, "records": stats.get("count", 0)}


def create_data_pipeline():
    """Build the ETL workflow."""
    wf = Workflow(name="data-pipeline")
    wf.add_node("fetch_data", fetch_data)
    wf.add_node("clean_data", clean_data)
    wf.add_node("aggregate_data", aggregate_data)
    wf.add_node("save_results", save_results)
    
    # Define the flow
    wf.connect("fetch_data", "clean_data")
    wf.connect("clean_data", "aggregate_data")
    wf.connect("aggregate_data", "save_results")
    
    return wf


if __name__ == "__main__":
    # Run once
    pipeline = create_data_pipeline()
    result = run(pipeline)
    print(f"\nPipeline completed! Saved {result.get('save_results', {}).get('records')} records.")
    
    # Or run on schedule (every 60 seconds)
    # scheduler = Scheduler(IntervalScheduler(60), create_data_pipeline)
    # scheduler.start()