[CmdletBinding()]
param(
    [switch]$CheckOnly
)

$ErrorActionPreference = 'Stop'

function Get-RedactedHost([string]$Url) {
    if ([string]::IsNullOrWhiteSpace($Url)) { return $null }
    try {
        $uri = [Uri]$Url
        return ($uri.Scheme + '://' + $uri.Host + $uri.AbsolutePath.TrimEnd('/'))
    } catch {
        return '<invalid-url>'
    }
}

$profiles = @(
    @{ Name = 'primary'; Url = $env:ANCIENT_BOOK_PRIMARY_API_URL; Model = $env:ANCIENT_BOOK_PRIMARY_MODEL; Key = $env:ANCIENT_BOOK_PRIMARY_API_KEY },
    @{ Name = 'secondary'; Url = $env:ANCIENT_BOOK_SECONDARY_API_URL; Model = $env:ANCIENT_BOOK_SECONDARY_MODEL; Key = $env:ANCIENT_BOOK_SECONDARY_API_KEY }
)

# Backward-compatible aliases for existing BibiLab helpers. Values never
# appear in output and are used only to determine whether configuration exists.
if (-not $profiles[0].Url) { $profiles[0].Url = $env:BIBI_API_URL }
if (-not $profiles[0].Model) { $profiles[0].Model = $env:BIBI_MODEL }
if (-not $profiles[0].Key) { $profiles[0].Key = $env:BIBI_API_KEY }

$results = foreach ($profile in $profiles) {
    $missing = @()
    if ([string]::IsNullOrWhiteSpace($profile.Url)) { $missing += 'url' }
    if ([string]::IsNullOrWhiteSpace($profile.Model)) { $missing += 'model' }
    if ([string]::IsNullOrWhiteSpace($profile.Key)) { $missing += 'api_key' }
    $status = if ($missing.Count -gt 0) { 'configuration_missing' } else { 'configured' }
    [ordered]@{
        profile = $profile.Name
        provider = Get-RedactedHost $profile.Url
        model = if ($profile.Model) { $profile.Model } else { $null }
        status = $status
        missing = $missing
    }
}

$payload = [ordered]@{
    profiles = @($results)
    secrets_written = $false
    network_used = $false
    next_step = 'Run a harmless connectivity probe through the host runtime before sending page images.'
}
$payload | ConvertTo-Json -Depth 5

if (($results | Where-Object { $_.status -eq 'configuration_missing' }).Count -gt 0) {
    exit 2
}
exit 0
