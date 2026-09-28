# AGENTS.md

Instructions for any AI agent working in this repository. Humans: see the same
steps, they are the real local development workflow.

## What this is

`demo-app` is a small Python HTTP service with a minimal web UI, deployed to
Kubernetes by ArgoCD via a Helm chart.

```
app/src/app.py       the service
app/tests/           pytest suite
app/chart/           the Helm chart (owned by this repo)
argo-control/        deployment config: image tag and per-env values
Tiltfile             build + deploy in one command
```

## Ground rules

- **Never edit `argo-control/` for feature work.** That directory is deployment
  configuration. Changing an image tag there is a release, not a feature.
- **No comments explaining what code does.** Put the reasoning in the commit message.
- **No ticket IDs anywhere in code or comments.**
- **Never merge your own pull request.** Open it and stop.

## Local development

Everything runs against the cluster you are already in. There is no local docker.

### 1. Branch

```bash
git checkout main && git pull
git checkout -b feat/<short-description>
```

### 2. Test-driven development

Write the failing test first. Always.

```bash
pytest app/tests -q                  # should fail, for the reason you expect
# ...implement...
pytest app/tests -q                  # should pass
pytest app/tests --cov=app/src --cov-report=term-missing
```

New behaviour without a test is not done.

### 3. Deploy and verify in Kubernetes

Unit tests are not proof it runs. Deploy it:

```bash
export TILT_NAMESPACE=dev-<something-unique>
tilt ci
```

`tilt ci` builds the image with buildkit, pushes to the in-cluster registry,
renders the Helm chart, applies it, and waits for the pods to be healthy. It
exits non-zero if anything fails.

Then confirm the behaviour is actually live:

```bash
kubectl run curl-check --rm -i --restart=Never --image=curlimages/curl:latest \
  -n $TILT_NAMESPACE -- -s http://demo-app/api/status
kubectl run curl-check --rm -i --restart=Never --image=curlimages/curl:latest \
  -n $TILT_NAMESPACE -- -s http://demo-app/
```

Keep that output. It goes in the pull request.

### 4. Clean up

```bash
kubectl delete namespace $TILT_NAMESPACE
```

### 5. Pull request

Commit with a message explaining what changed and why, push the branch, and open
a PR containing:

- **What was asked**
- **What changed**
- **TDD** — the failing test you wrote first and its failure output
- **Test coverage** — pytest output, coverage for the lines you touched
- **Verified in Kubernetes** — the `tilt ci` and `curl` output, quoted
- **Assumptions** — anything ambiguous you decided yourself
- **Out of scope** — what you deliberately did not do

## If you get stuck

Open the pull request as a draft anyway. Say exactly where you stopped, what you
tried, and what you think is wrong. A partial PR with honest notes is useful; a
silent failure is not.
