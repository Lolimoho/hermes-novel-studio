# Studio development instructions

These instructions apply to every file under `studio/`.

## Repository boundaries

- Treat `../skill/` as a separate maintained product. Do not edit, move, or reformat files under it unless the user explicitly requests Skill work.
- Put all new Novel Studio application code, tests, documentation, plugin code, and infrastructure under `studio/`.
- Do not restore the pre-split root layout or move Studio files back to the repository root.

## Milestone gate

1. Read `docs/project-management/status.md` before starting implementation work.
2. Work only on the milestone marked `IN_PROGRESS`.
3. Do not implement a locked milestone early unless the user explicitly changes scope.
4. A milestone may move to `READY_FOR_ACCEPTANCE` only when its stated deliverables, tests, documentation, and acceptance evidence are complete.
5. Only explicit user approval may move a milestone to `ACCEPTED` and unlock the next milestone.
6. Record every milestone status transition and material scope change in `docs/project-management/status.md`.

While M0 is active, create planning, product, architecture, security, API-contract, and decision documents only. Production application code starts at M1 after M0 acceptance.

## Architecture boundaries

- PostgreSQL is the source of truth for approved novel facts, artifacts, revisions, approvals, and audit history.
- Hindsight is semantic memory, never the source of truth for approved canon.
- Hermes owns model/API configuration, profiles, sessions, skills, tools, and Kanban execution state.
- Novel Studio must not duplicate Hermes API-key or model-provider configuration.
- AI actions must use domain APIs/tools; do not grant agents unrestricted SQL mutation.
- Human approval gates cannot be bypassed by an agent or automation.

## Engineering rules

- Keep secrets out of the repository. Commit examples with placeholders only.
- Prefer explicit contracts, versioned migrations, idempotent jobs, and auditable state transitions.
- Add tests with each behavior change and keep milestone acceptance paths covered end to end.
- Document architectural decisions in `docs/decisions/` using sequential ADR files.
- Preserve recoverability: drafts, approved revisions, task state, and audit data must not depend on a live agent session.

