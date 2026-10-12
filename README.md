This module is part of the molecular symmetry project developed in the context of the graduate course PGF5261 – Group Theory Applied to Solids and Molecules.

This codebase is live and can be accessed at the following link:
https://quantum-materials-simulation-research.github.io/simetria-molecular

## Asynchronous PDF Jobs

`POST /api/pdf` accepts `{"tex": "..."}` and returns HTTP 202 with
`{"ok": true, "job_id": "...", "status": "queued"}`. It stores the TeX in a
private S3 bucket and invokes the PDF Lambda asynchronously. The HTTP request
does not wait for Tectonic compilation.

`GET /api/pdf/{job_id}` returns `queued`, `processing`, `completed`, or `failed`.
A completed job includes a `download_url` signed for five minutes.
`GET /api/pdf/{job_id}?download=1` obtains a fresh signed URL and redirects to
the PDF. Job IDs are unguessable capabilities: treat them as private links.
This is not an authenticated multi-user job service.

The worker has a 300-second Lambda limit, with a shorter subprocess deadline
to leave time for persisting errors. Pending jobs expire after 15 minutes;
S3 lifecycle cleanup removes job inputs, state and PDFs after at least one day.
The API limits TeX input to 2 MB. Failed jobs must be submitted again.
Changing the molecule or analysis in the browser stops local tracking, not
an already running worker.

### Deployment Order

1. In `backend/infra`, run `terraform init`, review `terraform plan`, and apply
	the reviewed plan. This creates the private bucket, IAM permissions, GET
	route, worker environment variables and longer Lambda timeout.
2. Publish the backend PDF Lambda code through the existing commit/push `u`
	workflow. Do not deploy Lambda code manually.
3. Publish the frontend through its existing workflow. It supports both the
	old synchronous response and the new asynchronous job response during rollout.

The new Lambda code requires `PDF_JOB_BUCKET`; publishing it before Terraform
is applied returns HTTP 503. Terraform alone does not publish Lambda code,
because code changes are ignored by the Lambda Terraform lifecycle.

### Tests

Install `boto3`, `numpy` and `pydantic` in your test environment, then run:

```sh
python -m unittest discover -s tests -v
```

Tests use simulated storage and invocation; they do not call AWS.
