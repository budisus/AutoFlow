# AutoFlow

**Automation workflow engine for building, scheduling, and executing complex task pipelines.**

```
pip install autoflow
```

## Features

- 🔗 **Node-based workflow builder** — Connect tasks as directed graphs
- ⏰ **Flexible schedulers** — Cron, interval, or event-driven triggers
- 🔀 **Parallel & sequential execution** — Optimized worker pool
- 📊 **Execution logging & metrics** — Track task performance
- 🔌 **Extensible node system** — Plug in custom nodes
- 🐳 **Container-ready** — Deploy anywhere with Docker

## Quick Start

```python
from autoflow import Workflow, Schedule, run

# Define a workflow
wf = Workflow(name="data-pipeline")
wf.add_node("fetch", fetch_data)
wf.add_node("transform", transform_data)
wf.add_node("store", save_data)
wf.connect("fetch", "transform")
wf.connect("transform", "store")

# Run it
run(wf)
```

## Documentation

Full docs at [https://autoflow.dev/docs](https://autoflow.dev/docs)

## License

MIT © 2026