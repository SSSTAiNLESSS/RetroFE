<#
.SYNOPSIS
    Mechanically checks whether the current branch is finished, per the
    "Definition of done" in docs/RetroFE/Git-Operating-Procedure.md section 2a.

.DESCRIPTION
    Exists because a prose checklist was not enough: on 2026-07-28 a feature was
    declared finished with a CHANGELOG.md still advertising a different branch's
    feature, and STAiNLESS had to catch it. Anything checkable by a machine
    belongs here rather than in a document someone has to remember to read.

    Reports PASS / WARN / FAIL per check and exits non-zero on any FAIL.
    WARN means "look at this and decide" -- not every case is a defect.

.PARAMETER Base
    Branch to diff against when working out what this branch changed.
    Defaults to the CORE baseline.

.EXAMPLE
    .\Scripts\check_branch_ready.ps1
    .\Scripts\check_branch_ready.ps1 -Base feature/layout-hot-reload
#>
[CmdletBinding()]
param(
    [string]$Base = "feature/data-modernization"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

$script:fails = 0
$script:warns = 0

function Report {
    param([string]$Status, [string]$Name, [string]$Detail)
    $colour = "Green"
    if ($Status -eq "FAIL") { $colour = "Red";    $script:fails++ }
    if ($Status -eq "WARN") { $colour = "Yellow"; $script:warns++ }
    Write-Host ("  [{0}] {1}" -f $Status.PadRight(4), $Name) -ForegroundColor $colour
    if ($Detail) { Write-Host ("         {0}" -f $Detail) -ForegroundColor DarkGray }
}

$branch = (git rev-parse --abbrev-ref HEAD).Trim()
Write-Host ""
Write-Host "Branch readiness: $branch" -ForegroundColor Cyan
Write-Host ("Base for diff:    $Base") -ForegroundColor DarkGray
Write-Host ""

# --- 1. Working tree -------------------------------------------------------
$dirty = git status --porcelain
if ([string]::IsNullOrWhiteSpace($dirty)) {
    Report "PASS" "Working tree is clean"
} else {
    Report "FAIL" "Working tree has uncommitted changes" (($dirty -split "`n" | Select-Object -First 5) -join "; ")
}

# --- 2. Pushed to origin ---------------------------------------------------
$upstream = git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>$null
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($upstream)) {
    Report "FAIL" "No upstream set" "git push -u origin $branch"
} else {
    $counts = (git rev-list --left-right --count "$upstream...HEAD").Trim() -split "\s+"
    if ($counts[1] -ne "0") {
        Report "FAIL" "Not pushed" "$($counts[1]) commit(s) ahead of $upstream"
    } elseif ($counts[0] -ne "0") {
        Report "WARN" "Behind upstream" "$($counts[0]) commit(s) behind $upstream -- see procedure section 3 before pulling"
    } else {
        Report "PASS" "Pushed and in sync with $upstream"
    }
}

# --- 3. CHANGELOG.md describes THIS branch ---------------------------------
# A new branch inherits its parent's changelog. Leaving it means the branch
# advertises somebody else's feature on GitHub.
if (-not (Test-Path "CHANGELOG.md")) {
    Report "WARN" "No CHANGELOG.md" "feature/vlc-replacement uses CHANGELOG_VLC.md; otherwise add one"
} else {
    $header = (Get-Content "CHANGELOG.md" -TotalCount 1).Trim()
    # "feature/settings-reboot-restore" -> "Feature/Settings-Reboot-Restore"
    $expected = ($branch -split "[/-]" | ForEach-Object {
        if ($_.Length -gt 0) { $_.Substring(0,1).ToUpper() + $_.Substring(1) }
    }) -join "-"
    $expected = $expected -replace "^([A-Za-z]+)-", '$1/'
    if ($header -match [regex]::Escape($expected)) {
        Report "PASS" "CHANGELOG.md describes this branch"
    } else {
        Report "FAIL" "CHANGELOG.md is not this branch's" "found '$header' -- expected '# Changelog: $expected'"
    }
}

# --- 4. New settings keys reach the shipped template -----------------------
$template = "Package/Environment/Common/settings.conf"
$added = git diff "$Base...HEAD" -- "RetroFE/Source/*.cpp" "RetroFE/Source/*.h" |
         Select-String -Pattern '^\+.*getProperty\(\s*"([A-Za-z0-9_.]+)"' -AllMatches
$keys = @()
foreach ($m in $added) { foreach ($g in $m.Matches) { $keys += $g.Groups[1].Value } }
$keys = $keys | Sort-Object -Unique
if ($keys.Count -eq 0) {
    Report "PASS" "No new config keys read by this branch"
} else {
    $templateText = ""
    if (Test-Path $template) { $templateText = Get-Content $template -Raw }
    $missing = @($keys | Where-Object { $templateText -notmatch [regex]::Escape($_) })
    if ($missing.Count -eq 0) {
        Report "PASS" "Config keys documented in the shipped template"
    } else {
        Report "WARN" "Config keys not in $template" (($missing) -join ", ")
        Write-Host "         (internal/state keys are fine to skip -- user-facing settings are not)" -ForegroundColor DarkGray
    }
}

# --- 5. New docs/RetroFE docs are in the tracked-docs list -----------------
# docs/ is only partially tracked; a doc missing from the .gitignore comment
# block is one nobody knows is meant to be tracked.
$newDocs = git diff --name-only --diff-filter=A "$Base...HEAD" -- "docs/RetroFE/*.md"
if (-not $newDocs) {
    Report "PASS" "No new docs to register"
} else {
    $ignoreText = Get-Content ".gitignore" -Raw
    $unlisted = @($newDocs | Where-Object { $ignoreText -notmatch [regex]::Escape($_) })
    if ($unlisted.Count -eq 0) {
        Report "PASS" "New docs listed in .gitignore tracked-docs block"
    } else {
        Report "FAIL" "New docs missing from .gitignore tracked-docs list" ($unlisted -join ", ")
    }
}

# --- 6. HANDOVER.md refreshed ---------------------------------------------
$handover = git diff --name-only "$Base...HEAD" -- "HANDOVER.md"
if ($handover) {
    Report "PASS" "HANDOVER.md updated on this branch"
} else {
    Report "WARN" "HANDOVER.md untouched" "refresh it before stopping work"
}

# --- 7. Procedure doc current on the baseline ------------------------------
# Every new branch inherits the baseline's copy, so a stale one there is how
# the checklist goes missing from the next branch.
$baseDoc = git show "${Base}:docs/RetroFE/Git-Operating-Procedure.md" 2>$null
if ($LASTEXITCODE -ne 0) {
    Report "WARN" "Procedure doc absent from $Base" "new branches would inherit nothing"
} elseif ($baseDoc -match "Definition of done") {
    Report "PASS" "Procedure doc on $Base carries the checklist"
} else {
    Report "FAIL" "Procedure doc on $Base is stale" "new branches would inherit a version without the checklist"
}

# --- Summary ---------------------------------------------------------------
Write-Host ""
if ($script:fails -gt 0) {
    Write-Host "NOT READY - $($script:fails) failure(s), $($script:warns) warning(s)" -ForegroundColor Red
} elseif ($script:warns -gt 0) {
    Write-Host "READY, with $($script:warns) warning(s) to eyeball" -ForegroundColor Yellow
} else {
    Write-Host "READY - all mechanical checks pass" -ForegroundColor Green
}
Write-Host ""
Write-Host "Still needs a human: clean Release build with no warnings, and the" -ForegroundColor DarkGray
Write-Host "feature actually verified by running it -- neither is checkable here." -ForegroundColor DarkGray
Write-Host ""

if ($script:fails -gt 0) { exit 1 }
exit 0
