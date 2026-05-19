$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath ".env.local")) {
    throw ".env.local is required."
}

$tokenLine = Get-Content -LiteralPath ".env.local" | Where-Object { $_ -like "GITHUB_TOKEN=*" } | Select-Object -First 1
if (-not $tokenLine) {
    throw "GITHUB_TOKEN missing in .env.local."
}

$owner = (Get-Content -LiteralPath ".env.local" | Where-Object { $_ -like "GITHUB_OWNER=*" } | Select-Object -First 1) -replace "^GITHUB_OWNER=", ""
$repo = (Get-Content -LiteralPath ".env.local" | Where-Object { $_ -like "GITHUB_REPO=*" } | Select-Object -First 1) -replace "^GITHUB_REPO=", ""
$fullName = "$owner/$repo"

$env:GH_TOKEN = $tokenLine.Substring("GITHUB_TOKEN=".Length)

Write-Host "Repository:"
gh repo view $fullName --json nameWithOwner,url,visibility,defaultBranchRef

Write-Host "Recent workflow runs:"
gh run list --repo $fullName --limit 5
