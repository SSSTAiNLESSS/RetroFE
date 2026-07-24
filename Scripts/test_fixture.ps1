<#
.SYNOPSIS
    Snapshot / restore the RetroFE test fixture at K:\RetroFE-Testies.

.DESCRIPTION
    Layout hot-reload testing writes to the fixture: playlists get updated,
    meta.db gets rebuilt, layouts get edited, exes get dropped into core\.
    This gives a known-good baseline to reset to between tests.

    Only the VOLATILE part of the tree is snapshotted. emulators\ (1.9 GB,
    51k files), core 1.4\ and RetroFE\ never change during a test, so they are
    excluded -- that takes a snapshot from ~2.6 GB to ~450 MB. Excluded
    directories are also protected from the mirror's purge, so a Restore can
    never delete them.

.EXAMPLE
    .\Scripts\test_fixture.ps1 -Action Snapshot
    .\Scripts\test_fixture.ps1 -Action Status
    .\Scripts\test_fixture.ps1 -Action Restore -Force
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Snapshot', 'Restore', 'Status')]
    [string]$Action,

    # Restore is destructive (it mirrors, so it deletes drift). Require an
    # explicit flag rather than an interactive prompt -- Read-Host does not work
    # from an agent shell, where stdin is the null device.
    [switch]$Force,

    # Overridable so the mechanism can be exercised against a throwaway tree
    # before it is ever pointed at the real fixture.
    [string]$Fixture  = 'K:\RetroFE-Testies',
    [string]$Baseline = 'K:\RetroFE-Testies.baseline'
)

$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------- config ----

# Bulky and static: never touched by a test run.
$ExcludeDirs  = @('emulators', 'core 1.4', 'RetroFE')

# Regenerated every run; a clean test should start without it.
$ExcludeFiles = @('log.txt')
# ----------------------------------------------------------------------------

function Invoke-Mirror {
    param(
        [string]$Source,
        [string]$Dest,
        [switch]$ListOnly
    )

    # Exclusions must name the path on BOTH sides. /MIR purges the DESTINATION,
    # and on a Restore the source is the baseline -- which deliberately has no
    # emulators\ etc. A source-only /XD therefore matches nothing on the way
    # back, and the mirror happily deletes 1.9 GB of emulators from the fixture.
    $excludePaths = $ExcludeDirs | ForEach-Object {
        (Join-Path $Source $_), (Join-Path $Dest $_)
    }

    # NB: not $args -- that is an automatic variable inside a function.
    $roboArgs = @(
        $Source, $Dest,
        '/MIR',           # mirror: copy new/changed, purge what the source lost
        '/XD'
    ) + $excludePaths + @(
        '/XF'
    ) + $ExcludeFiles + @(
        '/R:1', '/W:1',   # do not stall for minutes on a locked file
        '/NP',
        '/NJH'
    )
    if ($ListOnly) {
        # Status exists to SHOW the drift, so keep the file list here. Suppress
        # it only for the copying actions, where it is just noise.
        $roboArgs += '/L'
    }
    else {
        $roboArgs += @('/NDL', '/NFL')
    }

    # Capture rather than let it flow down the pipeline, so callers can discard
    # the return value without also discarding the listing.
    $output = & robocopy.exe @roboArgs
    $code   = $LASTEXITCODE

    if ($ListOnly -or $code -ge 8) {
        $output | Write-Host
    }

    # Robocopy: 0-7 success (bit 0 = files copied, bit 1 = extras found/purged),
    # 8+ is a real failure.
    if ($code -ge 8) {
        throw "robocopy failed with exit code $code (see output above)"
    }
    return $code
}

if (-not (Test-Path $Fixture)) {
    throw "Fixture not found: $Fixture"
}

switch ($Action) {

    'Snapshot' {
        Write-Host "Snapshotting $Fixture" -ForegroundColor Cyan
        Write-Host "          -> $Baseline"
        Write-Host "  excluding: $($ExcludeDirs -join ', ') (static) and $($ExcludeFiles -join ', ')"
        Write-Host ''

        Invoke-Mirror -Source $Fixture -Dest $Baseline | Out-Null

        $m = Get-ChildItem $Baseline -Recurse -File -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum
        Write-Host ''
        Write-Host ("Baseline saved: {0} files, {1:N1} MiB" -f $m.Count, ($m.Sum / 1MB)) -ForegroundColor Green
        Write-Host "Reset to it any time with:  .\Scripts\test_fixture.ps1 -Action Restore -Force"
    }

    'Status' {
        if (-not (Test-Path $Baseline)) {
            throw "No baseline yet. Run: .\Scripts\test_fixture.ps1 -Action Snapshot"
        }
        Write-Host "Drift in $Fixture since the baseline was taken:" -ForegroundColor Cyan
        Write-Host '(list-only, nothing is changed)'
        Write-Host ''

        # Compare baseline -> fixture so "New File" means the test ADDED it and
        # "EXTRA" means the test DELETED it.
        Invoke-Mirror -Source $Baseline -Dest $Fixture -ListOnly | Out-Null
    }

    'Restore' {
        if (-not (Test-Path $Baseline)) {
            throw "No baseline to restore from. Run -Action Snapshot first."
        }
        if (-not $Force) {
            Write-Host "Restore is destructive: it mirrors the baseline back over" -ForegroundColor Yellow
            Write-Host "$Fixture, deleting anything the test added." -ForegroundColor Yellow
            Write-Host ''
            Write-Host "Protected (never touched): $($ExcludeDirs -join ', ')"
            Write-Host ''
            Write-Host "Re-run with -Force to go ahead, or -Action Status to see the drift first."
            return
        }

        Write-Host "Restoring $Fixture from baseline..." -ForegroundColor Cyan
        Invoke-Mirror -Source $Baseline -Dest $Fixture | Out-Null

        # log.txt is excluded from the mirror, so clear it explicitly -- every
        # test should start with an empty log.
        $log = Join-Path $Fixture 'log.txt'
        if (Test-Path $log) { Remove-Item $log -Force }

        Write-Host ''
        Write-Host "Fixture reset. log.txt cleared." -ForegroundColor Green
    }
}

# Robocopy signals "files were copied" with exit code 1, which would otherwise
# surface as a script failure. We already threw on anything >= 8.
exit 0
