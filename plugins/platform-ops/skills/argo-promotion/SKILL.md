---
name: argo-promotion
description: >-
  Open a pull request against the argo-control GitOps repository to promote or revert a
  deployed image tag or chart version. Use when a root cause has been established and the
  running version needs to change — most often to revert a bad promotion and restore
  service. Encodes the repository's branch, label, and PR body conventions. Never merges.
compatibility: Requires the gh CLI authenticated against the GitOps repository.
---

# argo-control promotion and revert

This skill is the only sanctioned way to change a deployed version. Do not hand-edit
`values.yaml` outside of it — the conventions here are what the platform team reviews against.

**Mitigation is not remediation.** A revert restores service; it does not fix the defect.
Whenever you open a revert PR, a corresponding fix must also be proposed via `app-fix-pr`.
Say so in the PR body, and link the two.

## Step 1 — Confirm you have a root cause

Do not open a revert PR on a hunch. You need, from `workload-rca`:

- The failing version and the last known-good version
- The commit that promoted the failing version
- A stated confidence level

If confidence is **low**, stop and report instead. A wrong revert is an outage of its own.

## Step 2 — Decide the correct change

| Situation | Correct change |
|---|---|
| A bad version was promoted, prior version was healthy | Revert the tag to the last known-good |
| The defect is in environment values themselves | Correct the value; do not revert the tag |
| Root cause is outside this repository | Open nothing here; report and hand off |

**Do not patch around a chart defect by adding the missing value here.** That hides the
defect from every other consumer of the chart and the next team hits it. Revert, then fix
upstream. If you are tempted to add a value that the chart should have defaulted, that is
the signal — say so explicitly in the PR body.

## Step 3 — Branch

```
revert/<app>-<from-version>-to-<to-version>
```

Branch from the default branch. One app per branch.

## Step 4 — Make the change

Edit only the environment values file for the affected app. Change only the version field.
No formatting changes, no unrelated keys, no reordering. The diff must be reviewable at a
glance during an incident.

## Step 5 — Open the PR

- **Title:** `revert(<app>): <from> -> <to> — <one-line root cause>`
- **Not a draft.** This is mitigation; it is meant to be merged quickly.
- **Labels:** `mitigation`, `automated`

Body must contain, in this order:

1. **Impact** — what is broken right now, and since when
2. **Root cause** — one sentence, from the RCA
3. **Evidence** — the causal chain, each link observed
4. **What this PR does** — the version change, and that it restores the prior state
5. **What this PR does NOT do** — that the defect remains in the newer version, with a
   link to the companion fix PR
6. **Confidence** and anything not ruled out
7. **Rollback** — how to undo this PR if it does not help

## Step 6 — Stop

Never merge. Never enable auto-merge. Report the PR URL and hand off.
