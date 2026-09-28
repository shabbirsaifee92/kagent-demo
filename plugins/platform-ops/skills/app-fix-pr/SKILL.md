---
name: app-fix-pr
description: >-
  Open a draft pull request against the application repository that fixes the underlying
  defect found during root-cause analysis, with the fix verified before the PR is opened.
  Use after a root cause is established, alongside (not instead of) a revert. Produces an
  evidence-backed draft for normal review — never merges, never promotes itself.
compatibility: >-
  Requires the gh CLI authenticated against the application repository, and helm for
  render verification.
---

# Application-repository fix PR

The revert stopped the bleeding. This is the actual fix, and it goes through normal review
at normal speed.

## Step 1 — Fix the defect, not the symptom

Work from the causal chain produced by `workload-rca`. The fix belongs at the link in the
chain where the mistake was made, not where it surfaced.

- A chart template reads a key with no default → add the default to the chart's `values.yaml`
- Code assumes configuration that may legitimately be absent → make it degrade, not crash
- Both are usually true. Fix both, and say why in the PR body.

Do not "fix" it by changing the environment values in the GitOps repo. That is a workaround,
and it leaves the defect in place for every other consumer.

## Step 2 — Prefer a safe default over a hard failure

If a missing value can produce a sensible degraded mode, that is almost always better than
a crash at startup. A cache that is unavailable should log a warning and run without a
cache. A startup crash turns a degraded feature into a full outage.

If a hard failure genuinely is correct, then it must fail with a message that names the
missing configuration and where to set it.

## Step 3 — Verify BEFORE opening the PR

Never propose an unverified fix. At minimum:

- `helm lint` the chart
- `helm template` the chart with the **real environment values** from the GitOps repo, and
  confirm the previously-empty value now renders correctly
- Confirm the rendered diff contains only what you intended

Capture this output. It goes in the PR body verbatim. An unverified fix is a guess with
extra steps.

## Step 4 — Branch

```
fix/<short-description>
```

## Step 5 — Open a DRAFT PR

- **Title:** `fix(<component>): <what the defect was>`
- **Draft: yes.** This is remediation, not an emergency.
- **Labels:** `bug`, `automated`
- Assign to the owning team where known.

Body must contain:

1. **What was broken** — the defect, in one sentence
2. **How it surfaced** — the incident, linked to the revert PR
3. **The fix** — what changed and why it belongs here rather than in the GitOps repo
4. **Verification** — the render output proving the value now resolves
5. **Confidence** and anything not ruled out
6. **Follow-ups** — anything deliberately left out of scope

## Step 6 — Stop

Never mark ready for review. Never merge. Report the PR URL.
