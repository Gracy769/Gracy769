# PowerShell script to deploy Gracy769 profile README

$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoDir

Write-Host "Deploying Gracy769 profile README..." -ForegroundColor Cyan

# Initialize Git if not already done
if (-not (Test-Path ".git")) {
    git init
    Write-Host "Initialized empty Git repository." -ForegroundColor Green
}

# Set local repository identity
git config user.name "Gracy769"
git config user.email "samcoper656@gmail.com"
Write-Host "Set local repository user to Gracy769." -ForegroundColor Green

# Set or update remote (using HTTPS to trigger Credential Manager popup)
$remoteUrl = "https://github.com/Gracy769/Gracy769.git"
$remotes = git remote
if ($remotes -contains "origin") {
    git remote set-url origin $remoteUrl
} else {
    git remote add origin $remoteUrl
}
Write-Host "Set remote origin to $remoteUrl" -ForegroundColor Green

# Rename branch to main
git branch -M main

# Add files
git add README.md

# Commit
git commit -m "Update profile README with modern tech theme"

# Push
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "NOTE: A browser login window may pop up on your screen. Please authenticate when prompted." -ForegroundColor Cyan
git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
} else {
    Write-Warning "Push failed. Ensure you have created the public repository 'Gracy769' on GitHub and signed in when prompted."
}
