param(
    [string]$Visibility = "public"
)

$ErrorActionPreference = "Stop"

if ($Visibility -notin @("public", "private")) {
    throw "Visibility must be 'public' or 'private'."
}

if (-not (Test-Path -LiteralPath ".env.local")) {
    throw ".env.local is required and must contain GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO."
}

$tokenLine = Get-Content -LiteralPath ".env.local" | Where-Object { $_ -like "GITHUB_TOKEN=*" } | Select-Object -First 1
if (-not $tokenLine) {
    throw "GITHUB_TOKEN missing in .env.local."
}

$owner = (Get-Content -LiteralPath ".env.local" | Where-Object { $_ -like "GITHUB_OWNER=*" } | Select-Object -First 1) -replace "^GITHUB_OWNER=", ""
$repo = (Get-Content -LiteralPath ".env.local" | Where-Object { $_ -like "GITHUB_REPO=*" } | Select-Object -First 1) -replace "^GITHUB_REPO=", ""
if (-not $owner) { throw "GITHUB_OWNER missing in .env.local." }
if (-not $repo) { $repo = "agent-workbench" }

$token = $tokenLine.Substring("GITHUB_TOKEN=".Length)
$env:GH_TOKEN = $token
$env:GITHUB_TOKEN = $token
$fullName = "$owner/$repo"

Write-Host "Checking ignored secret files..."
git check-ignore -q .env.local
if ($LASTEXITCODE -ne 0) { throw ".env.local is not ignored by git." }
if (Test-Path -LiteralPath ".env.bak") {
    git check-ignore -q .env.bak
    if ($LASTEXITCODE -ne 0) { throw ".env.bak is not ignored by git." }
}

Write-Host "Running tests..."
$env:UV_CACHE_DIR = ".uv-cache"
$env:UV_PYTHON_INSTALL_DIR = ".uv-python"
$env:PYTHONPATH = "src"
uv run --python 3.12 python -m unittest discover -s tests

Write-Host "Checking GitHub token..."
gh api user --jq .login | Out-Null

Write-Host "Preparing git history..."
git branch -M main
git config user.name "Codex"
git config user.email "codex@local"
git add .

git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Initial project scaffold"
} else {
    Write-Host "No staged changes to commit."
}

Write-Host "Ensuring remote repository exists: $fullName"
$exists = $null
try {
    $exists = gh repo view $fullName --json nameWithOwner --jq .nameWithOwner 2>$null
} catch {
    $exists = $null
}

if (-not $exists) {
    if ($Visibility -eq "private") {
        gh repo create $fullName --private --source . --remote origin
    } else {
        gh repo create $fullName --public --source . --remote origin
    }
}

$originUrl = git remote get-url origin 2>$null
if (-not $originUrl) {
    git remote add origin "https://github.com/$fullName.git"
}

Write-Host "Pushing main..."
git push -u origin main

Write-Host "Published https://github.com/$fullName"
