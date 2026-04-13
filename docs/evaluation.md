# Evaluation

Initial metrics:

- HitRate@K
- MRR
- average latency in milliseconds

The benchmark is deterministic:

- query succeeds when expected terms, files, or chunk ids are found in top-K
- required queries are the minimum gate
- optional queries guide future improvements but do not block the first baseline
