# Evaluation Artifacts

This directory stores small, reviewable evidence files:

~~~text
environment.remote.json
evaluation.json
evaluation.csv
interrupt_evaluation.json
baseline_interrupt_evaluation.json
perturbation_evaluation.json
benchmark.json
summary.md
SHA256SUMS
~~~

Large videos, datasets, and checkpoints must be hosted outside the Git repository.

The final evaluation.json must validate against evaluation.schema.json. `evaluate.py`
automatically writes JSON, flattened CSV, and a Markdown summary while hashing the actual
checkpoint tree. Tables in the technical report must be generated from these immutable results.
