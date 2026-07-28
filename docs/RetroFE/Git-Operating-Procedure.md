# Git Operating Procedure

**Claude owns git in this repo. STAiNLESS should never have to think about it.**

This is a standing procedure, not session state. It changes only when a standing decision
changes. Live "where are we right now" belongs in `HANDOVER.md`; the branch inventory in
`HANDOVER.md` §5 and the fork history in §7 are the companion reads.

Written 2026-07-28 after an explicit interview with STAiNLESS, who said: *"github completely
confuses the fuck out of me, and i am relying on you 100% with that stuff... you need to be in
charge of that, dont just say you got it, document that shit so next session you got it too."*

That is the contract. Behave accordingly:

- **Never make STAiNLESS choose a branch, a base, or a merge strategy.** Decide it, state the
  decision in one line with the reason, then act.
- **Never present git as an obstacle.** If something is blocked, the answer is "we need to do X
  first, it takes about Y" — not a lecture on refs.
- **Interview once, not every session.** The standing decisions below are already answered. Do
  not re-ask them. Ask only if a genuinely new fork in the road appears.

---

## 1. Standing decisions — answered 2026-07-28, do not re-ask

| Question | Answer | What it means for how you work |
|---|---|---|
| Submit work back to upstream `phulshof/RetroFE`? | **Keep the door open, not actively pushing PRs** | Every feature stays on its own branch so any one of them can be lifted out later. Do not tangle two features into one branch. But do not spend effort shepherding PRs unless asked. |
| Back branches up to GitHub? | **Yes, push everything to `origin`** | Every branch gets pushed with tracking set. Do this as part of `/handoff`, not as a special event. `origin` is STAiNLESS's own fork — pushing there is routine and pre-authorised. |
| One integrated "this is CORE" branch? | **Wanted, deferred** | Build it *after* the settings-reboot-restore feature lands. Do not start it mid-feature. Plan is in §6. |

Pushing to `origin` is **pre-authorised** and needs no confirmation. Pushing to `upstream` is
impossible by design (its push URL is the literal string `DISABLED`) and must stay that way.

---

## 2. The intake rule — when STAiNLESS says "let's make X"

Run these five steps *before* writing any code. It takes under a minute.

### Step 1 — Is something already in flight?

Check `git status` and `HANDOVER.md` §1 "Next single action".

- **Working tree dirty, or a feature half-built?** Say so plainly and give the choice in one
  sentence: *"We're mid-way through the layout watcher. I can park it cleanly and start this, or
  finish the watcher first — about an hour. Which?"* Never silently stack a second feature on an
  unfinished one.
- **Clean tree, nothing queued?** Go straight to step 2.

### Step 2 — Does X depend on unmerged work?

Ask it about the *code*, not the calendar: does X call functions, states, or config keys that
exist only on an unmerged branch?

- **Yes** → the new branch must be cut from that branch.
- **No** → cut from the CORE baseline (step 3).

### Step 3 — Pick the parent

| Situation | Cut from | Why |
|---|---|---|
| X is independent of all unfinished work | `feature/data-modernization` | This is the **CORE baseline** — the branch the live arcade `retrofe.exe` is built from (`HANDOVER.md` §3). Anything cut from `master` loses the libVLC video backend and cannot be tested against the real build. |
| X builds directly on an unmerged feature | that feature's branch | e.g. `refresh = yes` depends on `reapplyTweensFrom()`, so it belongs on `feature/layout-hot-reload`. |
| X is a pure upstream bug fix worth contributing | `upstream/master`, named `pr/<name>` | See §4. Rare. |

**Default is `feature/data-modernization`.** If unsure, that is the answer.

### Step 4 — Name it

`feature/<short-kebab-description>` for new capability, `fix/<short-kebab-description>` for
bugs, `pr/<name>` **only** for clean upstream-contribution branches (§4).

One branch = one logical modification. If you catch yourself wanting to add an unrelated change
to a branch, that is the signal to cut another branch instead.

### Step 5 — State it, then act

One line, then do it. Example of the right tone:

> "Cutting `feature/settings-reboot-restore` off `feature/data-modernization` — it doesn't touch
> the hot-reload code, so it stays independent and can ship on its own. Starting now."

Then `git switch -c <name> <parent>`. No approval loop for the git part; the *feature* still
follows the normal blueprint → go → build → prove it rhythm from `CLAUDE.md`.

### Step 6 — Replace CHANGELOG.md before the feature is done

**This repo carries a per-branch `CHANGELOG.md` at the root, and it is the first thing anyone
sees on GitHub.** It describes *that branch's* modification only — not a running history. A new
branch inherits its parent's changelog, so leaving it untouched means the branch advertises
somebody else's feature.

Format (follow `origin/fix/tween-easing-bugs` — the cleanest example):

```markdown
# Changelog: Feature/Branch-Name

One paragraph: what this branch does and why.

## [feature/branch-name]

### Added / Changed / Fixed
- **Thing**: what and why.
```

**Known debt, spotted 2026-07-28:** `feature/layout-hot-reload` and
`feature/data-modernization` both still carry `# Changelog: Feature/Mixed-Collections`,
inherited and never replaced. Fix when next working on either.

---

## 3. Ground truth of this repo — verified 2026-07-28

### Remotes

```
origin    https://github.com/SSSTAiNLESSS/RetroFE-CORE.git   (fetch + push)  <- ours
upstream  https://github.com/phulshof/RetroFE.git            (fetch only)    <- theirs
```

`upstream`'s push URL is deliberately `DISABLED` so a stray push fails loudly.

### ⚠️ The two-track situation — read this before touching the small branches

Four branch **names** exist in two different versions, and the local and remote copies are
**not** the same commits. This is the single most confusing thing in the repo. Verified by
`git merge-base --is-ancestor` and `rev-list --count`, not assumed:

| Branch name | On `origin` | Locally | Divergence |
|---|---|---|---|
| `fix/tween-easing-bugs` | **clean**, 2 commits off `upstream/master` | junk-carrying, off local `master` | ahead 5, behind 2 |
| `feature/playlist-menu-wheel` | **clean**, 2 commits off `upstream/master` | junk-carrying | ahead 5, behind 2 |
| `feature/reverse-launcher-mapping` | **clean**, 2 commits off `upstream/master` | junk-carrying | ahead 5, behind 2 |
| `feature/sort-and-filter` | **clean**, 3 commits off `upstream/master` | junk-carrying | ahead 6, behind 3 |

"Junk-carrying" means the branch descends from `d11032c` — the 279-binary commit documented in
`HANDOVER.md` §7 that would get a PR closed on sight.

**What happened:** the clean-PR-branch recipe from `HANDOVER.md` §7 was already executed for
these four and pushed — but under the *plain* branch names instead of `pr/*`, so the PR-track
copies now collide with the build-track copies. Same commit messages, different SHAs, different
bases.

**Consequences you must respect:**

- **Do not `git pull` these four branches.** It would merge two divergent histories and create a
  genuine mess. There is nothing to pull; the content is identical.
- **The `origin` copies are the PR-ready ones.** If a PR is ever wanted for one of these four,
  it is already sitting on GitHub — open it from the `origin` branch, base
  `phulshof/RetroFE:master`.
- **The local copies are the build-track ones.** Harmless, but not PR material.
- **Recommended tidy-up, not yet done:** rename the four `origin` branches to `pr/*` so the two
  tracks stop sharing names. This rewrites remote refs, so **ask STAiNLESS before doing it** —
  it is the one remote operation in this document that is not pre-authorised.

### Everything else

| Branch | State |
|---|---|
| `feature/data-modernization` | CORE baseline. **Pushed 2026-07-28** (was local-only — the branch the live arcade exe came from, with no backup). In sync. |
| `feature/layout-hot-reload` | Current feature branch, cut from `data-modernization`. **Pushed 2026-07-28.** In sync. |
| `feature/mixed-collections` | In sync. Carries junk history on both sides — large, not PR-shaped as-is. |
| `feature/vlc-replacement` | In sync. Carries junk history on both sides. |
| `master` | 3 ahead of `origin/master`. **Not** a clean upstream mirror — it carries `d11032c` (junk), `a7fb3da` (a genuine GStreamer fix), `75bdeea` (gitignore). |

All nine local branches now have upstream tracking configured (set 2026-07-28 — before that,
*none* did, which is why `git status` never reported ahead/behind and `HANDOVER.md` §5 carried
"in sync" claims that could not have been checked).

---

## 4. Contributing something upstream — the only recipe

Do **not** rewrite published history. Do **not** try to purge the junk binaries — that was
attempted 2026-07-23, measured, and reverted; the full reasoning is in `HANDOVER.md` §7 and the
short version is that it saves 7.6% and severs `upstream/master` ancestry.

Instead, cut clean and cherry-pick:

```bash
git fetch upstream
git switch -c pr/<name> upstream/master
git cherry-pick <the real commits>
git push -u origin pr/<name>
```

Then open the PR: base `phulshof/RetroFE:master` ← compare
`SSSTAiNLESSS/RetroFE-CORE:pr/<name>`. The junk binaries never enter the picture because the
branch never descends from `d11032c`.

Always name these `pr/*`. That is the rule the four branches in §3 broke.

---

## 5. Routine operations — who decides what

| Operation | Pre-authorised? | Notes |
|---|---|---|
| `git switch -c` a new feature branch | ✅ yes | Decide the parent yourself via §2. State it in one line. |
| Commit on a feature branch | ✅ yes | Never commit on `master`. |
| `git push origin <branch>` | ✅ yes | Own fork. Do it every `/handoff`. |
| `git fetch` (either remote) | ✅ yes | Read-only. |
| Merge one feature branch into another | ❌ ask | Changes what ships. Explain the conflict risk first. |
| Rename or delete a remote branch | ❌ ask | Affects GitHub state. |
| Anything that rewrites history (`rebase`, `filter-repo`, `push --force`) | ❌ ask, and expect the answer to be no | See §4 and `HANDOVER.md` §7. |
| `git add -A` | 🚫 **never** | `RustCore/target/` reaches 2.2 GB and the repo already carries ~360 MiB of committed binaries. Add files by name. |

---

## 6. The integration branch — planned, deferred

**Decision 2026-07-28: wanted, but not until the settings-reboot-restore feature lands.**
Reason: merging five branches and building a new feature at the same time makes a failure
impossible to attribute.

Nothing currently combines all the mods into one shippable build. `feature/data-modernization`
is the biggest branch but does not contain the tween fixes, playlist wheel, launcher mapping, or
sort/filter.

When the time comes:

1. Cut `core-integration` from `feature/data-modernization`.
2. Merge the small branches **local copies** (build-track — the `origin` copies are the clean PR
   variants and have a different base, §3) in ascending order of risk:
   `fix/tween-easing-bugs` → `feature/reverse-launcher-mapping` → `feature/playlist-menu-wheel`
   → `feature/sort-and-filter`.
3. **Expect conflicts between `sort-and-filter` and `data-modernization`** — both touch
   collection and metadata code. This has never been trialled. Budget real time for it.
4. Build, test on `K:\RetroFE-Testies`, then ship to CORE.

### Licensing, when a build is distributed

RetroFE is **GPLv3**. Distributing modified binaries requires offering the corresponding source,
so tag every released build (`git tag -a core-v1.0`) to keep public source matched to the
shipped exe. Third-party assets bundled with CORE (themes, artwork, fonts, DLLs) carry their own
licences and are not covered by RetroFE's GPL.

---

## 7. Plain-English glossary for STAiNLESS

Only here so the words in this file are not opaque. You are not expected to use any of them.

- **branch** — a parallel copy of the project where one change is built, so it can't break the
  others. "One branch per modification" is why your mods stay untangled.
- **origin** — your own copy of the project on GitHub. Backup + your workspace. Safe to push to.
- **upstream** — the original author's project. We can read from it, never write to it.
- **commit** — one saved snapshot with a message explaining the change.
- **push / fetch** — upload your commits to GitHub / download what's there.
- **ahead / behind** — how many commits your PC has that GitHub doesn't, and vice versa.
- **cherry-pick** — copy one specific change onto a different branch, leaving its baggage behind.
- **PR (pull request)** — a formal offer of your change to the original author. Optional; you
  have decided to keep the option open without actively pursuing it.
- **merge conflict** — two branches changed the same lines, so someone must choose. Claude
  handles these; you'll only hear about it if a real decision is needed.
