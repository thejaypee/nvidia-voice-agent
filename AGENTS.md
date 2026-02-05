# AGENTS.md - Automated Deployment Guide

This document guides any AI agent to fully automate the deployment of the NVIDIA Voice Agent to GitHub and AI Workbench.

## Overview

This is a complete, hands-off automated deployment system. No manual steps. The agent executes everything.

## Prerequisites

- Linux/WSL environment with git and curl installed
- GitHub personal access token (set as env var: `$GH_TOKEN`)
- NVIDIA API key (already in `.env` file)
- Project directory: `/home/sauly/nvidia-voice-agent`

## Automated Deployment Steps

### Step 1: Create GitHub Repository (if not exists)

```bash
curl -X POST https://api.github.com/user/repos \
  -H "Authorization: token $GH_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{"name":"nvidia-voice-agent","description":"Voice-enabled conversational AI agent with STT/TTS using Riva and Nvidia models","public":true}'
```

**Expected Output:** JSON response with repository URL

### Step 2: Initialize Git (if not already initialized)

```bash
cd /home/sauly/nvidia-voice-agent
git init
git config user.email "workbench@nvidia.local"
git config user.name "NVIDIA Workbench"
```

### Step 3: Add and Commit All Files

```bash
git add .
git commit -m "Initial: NVIDIA Voice Agent"
```

**Files to be committed:**
- `.project/spec.yaml` - AI Workbench configuration
- `code/` - Python source modules
- `compose.yaml` - Docker Compose for Riva
- `Dockerfile` - Container definition
- `requirements.txt` - Dependencies
- `tests/` - Test suite
- `notebooks/demo.ipynb` - Interactive demo
- `.env` - Environment configuration (with API keys)
- `README.md` - Documentation

### Step 4: Add GitHub Remote

```bash
git remote add origin "https://$GH_TOKEN@github.com/thejaypee/nvidia-voice-agent.git"
```

### Step 5: Push to GitHub

```bash
git branch -M main
git push -u origin main
```

**Expected Output:**
```
* [new branch]      main -> main
```

## Verification

After deployment, verify:

1. **GitHub Repository Exists:**
   ```bash
   curl -H "Authorization: token $GH_TOKEN" \
     https://api.github.com/repos/thejaypee/nvidia-voice-agent
   ```
   Expected: 200 OK with repo details

2. **Commits Pushed:**
   ```bash
   git log --oneline | head -1
   ```
   Expected: Initial commit message

## Next Steps for User

Once deployment completes, user proceeds in NVIDIA AI Workbench GUI:

1. **Clone Project:**
   - URL: `https://github.com/thejaypee/nvidia-voice-agent.git`
   - Workbench reads `.project/spec.yaml` automatically

2. **Start Containers:**
   - Riva service initializes (~30 min first time)
   - Voice agent container starts with JupyterLab access

3. **Run Agent:**
   - CLI: `python -m code.conversation`
   - Jupyter: Open `notebooks/demo.ipynb`

## Key Points for Agents

- **No manual intervention needed** - This process is fully automated
- **Environment variables** - All secrets are in `.env`, not hardcoded
- **Error handling** - If repo creation fails (already exists), continue with push
- **GitHub token** - Keep secret in environment, never commit to repository
- **WSL environment** - Execute all commands in Linux/WSL, not Windows
- **API keys** - Already configured in `.env` file

## Troubleshooting

| Error | Solution |
|-------|----------|
| `fatal: repository not found` | Create repo first using GitHub API |
| `Push protection: secret detected` | Remove files containing tokens, amend commit |
| `git: command not found` | Ensure executing in WSL environment |
| `permission denied` | Check GitHub token has repo creation scope |

## Files to Ignore from Git

The following are created but not committed:
- `setup.py`, `setup.bat`, `setup.ps1` - Contain secrets
- `init-git.sh`, `init_git.py` - For manual setup only
- `.git/` - Generated automatically

## Automation Integration

To integrate into automated workflows:

```bash
#!/bin/bash
set -e

TOKEN="$GH_TOKEN"
REPO_NAME="nvidia-voice-agent"
GITHUB_USER="thejaypee"

# Create repo
curl -X POST https://api.github.com/user/repos \
  -H "Authorization: token $TOKEN" \
  -d "{\"name\":\"$REPO_NAME\",\"public\":true}"

# Deploy
cd /home/sauly/nvidia-voice-agent
git init
git config user.email "workbench@nvidia.local"
git config user.name "NVIDIA Workbench"
git add .
git commit -m "Initial: NVIDIA Voice Agent"
git remote add origin "https://$TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"
git branch -M main
git push -u origin main

echo "✅ Deployment complete!"
```

---

**Document Version:** 1.0
**Last Updated:** 2026-02-05
**Status:** Fully Automated - No User Input Required
