# cloudflow Constitution

cloudflow is the workflow engine of the Cloud Sandbox: it starts compute nodes,
runs the models on them, and makes the plots of their output. It was the
`cloudflow/` directory of Cloud-Sandbox, packaged here as an installable Python
project. This constitution says what every specification, plan and change in
this repository is held to. "The operator" is the person who owns this
repository and directs the work. "An agent" is any coding agent working in it.

## Core Principles

### I. The Original's Behaviour, Packaged

- What cloudflow does is what the original's `cloudflow/` did (Cloud-Sandbox
  at the unit's baseline, and the original repository's later commits as they
  are synced). The package changes how it is installed and imported, not what
  it does, unless a spec says otherwise.
- A difference from the original is deliberate and written down: the nine
  corrections made in the copy (described in Cloud-Sandbox's
  `exportit/MAP.md`, "Corrections made in the copy"), which are commits in
  this repository's history, and since its originals were deleted from
  Cloud-Sandbox (2026-11-18), each change made here, in a commit that says
  what it corrects (principle S3). Never a quiet edit.
- Defects found in the original and left as they are are recorded, with the
  reason, and are not fixed in passing.

**Why:** the sandbox runs on the original; a package that behaves otherwise
cannot stand in for it.

### II. It Stands Alone

- The installed package reaches nothing outside itself: no path into
  Cloud-Sandbox, no sibling unit's files. Every outward reference the code
  makes is in `tests/outward_references.json`, and a new one fails the tests
  until it is reviewed and recorded.
- The wheel is built and installed into an empty environment by
  `just full-test`, and imports there.

**Why:** a package that works only beside its old repository is not a
package.

### III. New Code Meets the Full Rules; Copied Code Meets the Floor

- Files written for the package are held to the whole lint and type-check
  rule set.
- Copied code is held to the floor: no syntax errors and no undefined names.
  Raising a copied file to the full rules is a change made here, with a spec
  of its own, because it makes every later sync from the original harder to
  merge.

**Why:** the copied code is the original's, and later changes to the original
are merged into it; restyling it in passing would turn every such merge into a
conflict.

<!-- csis-shared: begin, version 2.0.1. Written by Cloud-Sandbox's `just constitution` from exportit/tools/constitution/shared.md; do not edit here. -->

### S1. Acceptance Tests Run Through the Justfile

This repository's acceptance tests are two `Justfile` targets, `just test` and
`just full-test`. A change is accepted when they pass, and not before.

- Every check is run through the `Justfile`, never by calling the tool under
  it directly. A check the `Justfile` lacks is added to it.
- `just test` passes after every change: what this repository's `Justfile`
  puts in it (lint, a type-check with 0 errors where there is code to check,
  and the fast tests).
- `just full-test` passes before a spec is called done and before any release:
  everything in `just test`, and the slow tests this repository has.
- New behaviour comes with tests at the level that proves it.
- What the documentation promises is held by a test where it can be.
- A failure caused by an expired credential or an unreachable service is
  reported as environmental, apart from a failure of the code.

**Why:** acceptance tests that are named targets stay the same between runs
and between people.

### S2. The Operator Decides

- A choice that is the operator's to make is asked of the operator before work
  depends on it, and the answer is recorded in the spec. An agent does not pick
  for them, and follows the answer given even when it is none of the options
  offered.
- An agent commits locally. Merging into `develop`, pushing a branch or a tag,
  and cutting a release each happen only on the operator's word, and one
  approval does not carry over to the next.
- No secret is ever in the repository or on a command line. Keys and tokens are
  read from the environment or from a repository secret.
- When work finds a defect in a released version, it is fixed here, and the
  operator is asked whether to release it as a patch version.

**Why:** the operator reviews each plan and owns each decision before work is
spent on it; and a push or a release cannot be taken back.

### S3. A Copied File: Changed in Cloud-Sandbox, Then Owned Here

This repository was made on 2026-11-17 from a unit of
`infrastructurebuilder/Cloud-Sandbox`, where it is kept as a git submodule
under `exportit/`. Many of its files are copies of files of the original
repository, and Cloud-Sandbox's mapping file for this unit
(`exportit/<unit>.map`) says which. What may change them depends on whether
Cloud-Sandbox still holds their originals:

- **While it does** (the mapping file does not say `owned`), a copied file is
  never edited here. It changes when its original changes, or by a patch in
  Cloud-Sandbox (`exportit/<unit>.patches/`); Cloud-Sandbox's `just export
  <unit>` writes the result into this repository, and its `just test` fails
  on any copied file that differs from the original at the unit's baseline
  plus its patches. Only a file the mapping file calls `new` is this
  repository's own to change here, and a spec that needs a copied file
  changed puts the patch among its tasks, made in Cloud-Sandbox.
- **Once Cloud-Sandbox has deleted this unit's originals** (its stage 22; the
  mapping file says `owned`), this repository owns its copied files and
  changes them here like any other. A later change to the original repository
  arrives by sync: Cloud-Sandbox's `just export-sync` merges the original's
  new commits onto a feature branch here, with their authors, and a conflict
  with this repository's own changes stops the sync for the operator to
  settle. Cloud-Sandbox's `just export-lineage` holds this repository's
  history to the original's, which is what a sync depends on.

**Why:** while both exist, the copies are held to their originals file for
file, so that every difference is written down where both can be seen; once
the originals are gone, the unit is the only place its files live.

### S4. Nothing Goes Toward `ioos`

- No push, no pull request, no remote and no fork toward `ioos/Cloud-Sandbox`
  or anything else under `ioos`, from this repository or for it.
- Every remote of this repository is on `infrastructurebuilder`.

**Why:** the original project belongs to IOOS, and this work is not offered to
it. If any of it is to reach IOOS, that is the operator's to arrange, outside
this work.

## Development Workflow

This repository uses Spec Kit, and nothing else, to plan and track its own
work.

- **Every change larger than a small fix has a spec** under
  `specs/<number>-<short-name>/`: `spec.md` (what and why), `plan.md` (how),
  `tasks.md` (the steps, ticked as they are done). They are made with
  `/speckit-specify`, `/speckit-plan` and `/speckit-tasks`, and carried out
  with `/speckit-implement`.
- **Work that spans units is planned in Cloud-Sandbox**, as a spec under its
  `specs/`, because Cloud-Sandbox is the one place where every unit is checked
  out beside the others. A spec here covers work within this repository; a
  spec there may give rise to one.
- **Open questions are settled before planning**, with `/speckit-clarify` or
  by asking the operator, and recorded in the spec under Clarifications
  (principle S2).
- **`plan.md` checks the plan against this constitution** before any work, and
  again after the design. A plan that breaks a principle says so and why under
  Complexity Tracking, or is changed.
- **There is no `PLAN.md`** in this repository, and none is created. A rule
  elsewhere that says plans go in `PLAN.md` is met here by a spec.
- **Branches:** one git-flow feature branch per spec, `feature/<short-name>`,
  from `develop`. It is finished with a squash-merge into `develop` and kept,
  never deleted. After a finish, `git diff develop feature/<short-name>` is
  empty. Spec Kit's own numbered branches are not used: a spec's directory
  name and its branch's name are independent.
- **After a finish here,** Cloud-Sandbox records this repository's new
  `develop` commit (`git add exportit/<unit>` there), and is pushed after this
  repository, never before.
- **A spec is done** when its tasks are ticked, `just full-test` passes, and
  its `spec.md` says so in its Status line.

## Governance

- This constitution is above every other practice in this repository. Where a
  spec, a plan, a template or a habit disagrees with it, this document is
  right, or it is amended.
- **It has two parts.** The shared part, between the two `csis-shared`
  markers, is the same in every unit's repository. It is kept in
  Cloud-Sandbox (`exportit/tools/constitution/shared.md`), written into each
  unit by `just constitution` there, and held to that source by Cloud-Sandbox's
  `just test`. It is never edited here. The rest is this repository's own.
- **Amending it:** only the operator amends it, or an agent on the operator's
  instruction. This repository's own part is amended here with
  `/speckit-constitution`; the shared part is amended in Cloud-Sandbox, and
  written out to every unit. An amendment says what changed and why, and
  changes whatever in the open specs it makes untrue.
- **Versions** follow semantic versioning, one for the shared part (on its
  marker) and one for the whole (at the end): MAJOR when a principle is
  removed or redefined so that earlier work would break it; MINOR when a
  principle or section is added or materially widened; PATCH for wording.
- **Compliance:** every `plan.md` carries a Constitution Check. A review of a
  change checks it against the principles. `/speckit-analyze` is run when a
  spec, its plan and its tasks may have drifted apart.
- **Guidance for a session** is in `CLAUDE.md` at the root, which points here
  and adds nothing of its own.

<!-- csis-shared: end -->

## Technical Constraints

Python, built with `uv` and `hatchling`; version 1.6.0b0 at the first tag; the
wheel holds `src/cloudflow` only, and the source distribution leaves out
`.specify/`, `.claude/`, `specs/` and `CLAUDE.md`. AWS access only through what
the original uses (boto3); no test reaches AWS.

**Version**: 2.0.1 | **Ratified**: 2026-11-18 | **Last Amended**: 2026-11-19
