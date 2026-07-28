---
name: feature-done
description: Run RetroFE's definition-of-done checks before calling any feature, fix or branch finished — verifies the per-branch CHANGELOG.md actually describes this branch, that new settings keys reached the shipped settings.conf template, that new docs/RetroFE docs are registered in .gitignore's partial-tracking list, that HANDOVER.md was refreshed, that the branch is pushed, and that the git procedure doc on the CORE baseline is current. Use PROACTIVELY whenever work is about to be described as done, complete, finished, shipped, ready, or wrapped up, before committing the final change of a piece of work, and before any handoff. Also use when the user says "/feature-done", "is this ready", "did I miss anything", "check the branch", or asks why a convention was missed. NOT a code review and NOT a build — it checks repo conventions, which is the thing that has actually been missed.
---

# feature-done — RetroFE definition of done

STAiNLESS has delegated git and repo conventions to Claude entirely. **Him catching a missed
convention is a failure of that delegation, not a helpful review.** This skill exists because a
prose checklist was not enough: on 2026-07-28 a feature was declared finished with a
`CHANGELOG.md` still advertising a different branch's feature, and he had to catch it.

Run this **before** saying anything is done. It takes seconds.

## 1. Run the mechanical checks

```powershell
.\Scripts\check_branch_ready.ps1
```

Add `-Base <branch>` if this branch was cut from something other than
`feature/data-modernization`.

It reports PASS / WARN / FAIL and exits non-zero on any FAIL:

| Check | Why it exists |
|---|---|
| Working tree clean | — |
| Pushed and in sync with `origin` | Backups are pre-authorised; unpushed work is unbacked-up work |
| `CHANGELOG.md` describes **this** branch | A new branch inherits its parent's changelog. This is the one that was missed. |
| New config keys reach `Package/Environment/Common/settings.conf` | The shipped template is where users discover settings |
| New `docs/RetroFE/*.md` registered in `.gitignore` | `docs/` is only *partially* tracked |
| `HANDOVER.md` refreshed | Next session's only state |
| Procedure doc current on the **baseline** | Every new branch inherits the baseline's copy; a stale one there is how the checklist goes missing again |

**WARN means look and decide**, not "defect". Internal state keys legitimately do not belong in
the user-facing settings template; user-facing settings do.

## 2. Do the two things the script cannot check

- **Clean Release build, no warnings.**
  ```powershell
  cd RetroFE\Build
  cmake --build . --config Release
  ```
- **Verify by running it, and quote the evidence.** A log line, a measured before/after, a
  screenshot the user confirmed. Never "should work". If it was only built and not run, say
  exactly that.

## 3. Judgement calls the script deliberately leaves alone

- **Design doc.** If the feature has non-obvious mechanics — anything a future session would
  otherwise have to re-derive from source — write one in `docs/RetroFE/` and add it to the
  tracked-docs list in `.gitignore`.
- **Launcher properties** go in `Package/Environment/Common/launchers/Main.conf`.
- **`submissions/pull_requests.md`.** A prepared PR guide exists on two origin branches. It is
  stale and inconsistently tracked — see `Git-Operating-Procedure.md` §2b. Consider it, and if
  skipping, say why.

## 4. If a convention was missed anyway

Do not just fix the instance. **Audit, then fix the checker**, or it recurs:

```bash
git diff --name-only upstream/master origin/<branch>     # what a finished branch really contains
```

Then add the finding to `docs/RetroFE/Git-Operating-Procedure.md` §2b, and — if it is
mechanically checkable — to `Scripts/check_branch_ready.ps1`. A convention that exists in the
repo but not in the checker is a bug in the checker.

**Standing rule: derive procedure from the repo, not from the conversation.**

## Reference

- `docs/RetroFE/Git-Operating-Procedure.md` — §1 standing decisions (already answered, do not
  re-interview), §2 intake rule, §2a definition of done, §2b audited conventions, §3 the
  local/remote divergence trap.
- `HANDOVER.md` — live session state.
