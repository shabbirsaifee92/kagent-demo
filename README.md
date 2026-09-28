# kagent-demo

Synthetic demo environment for a kagent proof of concept: an **unattended** agent that
performs root-cause analysis on a broken deployment and proposes fixes as pull requests.

Nothing here is real. The structure mirrors a two-repo GitOps setup in a single repository.

## Layout

| Path | Stands in for |
|---|---|
| `app/` | the application repo — source, Dockerfile, and the base Helm chart |
| `argo-control/` | the GitOps repo — per-environment values and the Argo `Application` |
| `plugins/platform-ops/` | an Agent Plugins package of skills the agent loads |
| `kagent/` | the agent, its model config, and its read-only RBAC |

## The scripted failure

`v1.5.0` adds a cache backend. The chart templates `CACHE_URL` from `.Values.cache.url`,
but the chart's own `values.yaml` never defines a default for it — so the variable renders
empty and the container exits at startup.

The image tag is pinned in `argo-control`, so nothing breaks until the tag is promoted.
Promoting `1.4.0 -> 1.5.0` triggers the outage.

```
symptom      ValueError: unsupported cache backend: ''
observed     CACHE_URL="" in the running pod
template     deployment.yaml renders .Values.cache.url
defect       app/chart/values.yaml defines cache.enabled but not cache.url
shipped in   v1.5.0
triggered by the argo-control tag promotion
```

The agent is expected to produce that chain, then open two PRs:

- **revert** in `argo-control` — mitigation, ready to merge
- **fix** in `app/` — remediation, draft, verified with `helm template` before opening

## Design constraints

- The agent has **read-only** RBAC. It never mutates the cluster.
- Its only writes are pull requests. ArgoCD remains the sole thing that changes the cluster.
- Neither PR is merged or auto-merged by the agent.
