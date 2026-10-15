## 1. Graph hung in fetch node

Symptom: app.invoke() never returned. 

Cause: trafilatura.fetch_url has no timeout; one dead URL blocked the pipeline.

Fix: Download with requests (timeout), parallelize with a thread pool, skip failures.
