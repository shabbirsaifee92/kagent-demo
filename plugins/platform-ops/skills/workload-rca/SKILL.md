---
name: workload-rca
description: >-
  Find the root cause of a failing Kubernetes workload that is managed by ArgoCD and
  deployed from a Helm chart. Use when a workload is CrashLoopBackOff, not becoming
  ready, OOMKilled, or an Argo Application has gone Degraded after a sync. Produces a
  causal chain backed by evidence, not a restatement of the alert. Read-only: this
  skill never mutates cluster state.
compatibility: >-
  Requires read access to the target namespace (pods, events, deployments, replicasets,
  pods/log) and read access to the GitOps repository.
---

# Workload root-cause analysis

The alert already told you *what* broke. Your job is *why*. Do not restate the symptom.

**Read-only — enforced throughout.** Never patch, delete, scale, restart, or annotate any
resource. Never merge anything. Your only outputs are findings.

## Core rule — the error message is a symptom, not a cause

A stack trace tells you where the process gave up, not why it was configured that way.
Always trace from the failing process outward to the thing a human changed. Stop only
when you reach a change in Git, or when you have exhausted the evidence available.

## Phase 1 — Establish the failure

Collect, in this order:

- Pod status and `restartCount`; the terminated container's `reason` and `exitCode`
- Recent `Events` in the namespace, oldest first
- Container logs, including `--previous` for a crashlooping pod

Record the precise failure signature. Do not proceed on a guess about what it means.

## Phase 2 — Compare against what was intended

- Read the rendered workload spec actually running in the cluster
- Identify every environment variable, mount, probe, and resource limit the container received
- Flag any value that is empty, absent, or obviously a default when it should not be

An empty value is a finding. Something upstream failed to supply it.

## Phase 3 — Trace the value back to its source

For each suspicious value, walk the chain backwards:

1. Which chart template emitted it?
2. Which values key does that template read?
3. Is that key defined in the chart's own `values.yaml` defaults?
4. Is it overridden in the GitOps environment values?

**The most common root cause is a key that a chart template reads but no `values.yaml`
defines** — the template renders empty and the failure surfaces far away from the mistake.

## Phase 4 — Find the change

Identify the commit that introduced the failure. Check both:

- The **GitOps repository** — was an image tag or chart version promoted?
- The **application repository** — what shipped in that version?

A tag promotion is usually the *trigger*. The *defect* usually shipped earlier, in the
version being promoted to. Name both, and keep them distinct.

## Phase 5 — Report

Produce a causal chain, each link backed by evidence you actually observed:

```
symptom -> observed value -> template -> missing default -> commit -> promotion
```

Then state:

- **Root cause** — one sentence
- **Trigger** — what made it surface now
- **Confidence** — high / medium / low
- **Not ruled out** — alternative explanations, and what access you lacked to eliminate them

Never claim certainty you have not earned. A named uncertainty is more useful to the
on-call engineer than false confidence.

## Handoff

If a fix is warranted, do not apply it. Hand the causal chain to `argo-promotion` for
mitigation and `app-fix-pr` for remediation.
