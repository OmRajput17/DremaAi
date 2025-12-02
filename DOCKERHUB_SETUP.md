# Docker Hub Setup Guide

## Step 1: Create Docker Hub Account (if you don't have one)

1. Go to: https://hub.docker.com/signup
2. Sign up with your email
3. Verify your email address
4. **Remember your username** (this is what you'll use in secrets)

---

## Step 2: Create Docker Hub Access Token

1. Log in to Docker Hub: https://hub.docker.com
2. Click your username (top right) → **Account Settings**
3. Go to **Security** tab
4. Click **New Access Token**
5. **Token description:** `GitHub Actions`
6. **Access permissions:** `Read, Write, Delete`
7. Click **Generate**
8. **COPY THE TOKEN IMMEDIATELY** - you won't see it again!

---

## Step 3: Add GitHub Secrets

Go to: https://github.com/OmRajput17/DremaAi/settings/secrets/actions

Add these **2 new secrets**:

### 1. DOCKERHUB_USERNAME
- Click **New repository secret**
- Name: `DOCKERHUB_USERNAME`
- Value: Your Docker Hub username (e.g., `john123`)
- Click **Add secret**

### 2. DOCKERHUB_TOKEN
- Click **New repository secret**
- Name: `DOCKERHUB_TOKEN`
- Value: The access token you just copied from Docker Hub
- Click **Add secret**

---

## Step 4: Update docker-compose.yml on EC2

When you SSH into EC2, update the docker-compose.yml file:

Replace `YOUR_DOCKERHUB_USERNAME` with your actual Docker Hub username:

```yaml
image: ${DOCKER_IMAGE:-your-actual-username/drema-ai:latest}
```

For example, if your username is `john123`:
```yaml
image: ${DOCKER_IMAGE:-john123/drema-ai:latest}
```

---

## Step 5: Push to GitHub

After adding both secrets:

```bash
git add .github/workflows/ci-cd.yml docker-compose.yml
git commit -m "Configure Docker Hub integration"
git push origin main
```

---

## Verification

After the workflow completes:

1. **Check GitHub Actions**: https://github.com/OmRajput17/DremaAi/actions
2. **Check Docker Hub**: https://hub.docker.com/r/YOUR_USERNAME/drema-ai
   - You should see your image there!

---

## Required Secrets Summary

You now need these **5 secrets** total:

### Docker Hub (2 secrets):
- ✅ `DOCKERHUB_USERNAME` - Your Docker Hub username
- ✅ `DOCKERHUB_TOKEN` - Access token from Docker Hub

### EC2 Deployment (3 secrets):
- ✅ `EC2_HOST` - Your EC2 IP address
- ✅ `EC2_USER` - SSH username (ubuntu/ec2-user)
- ✅ `EC2_SSH_KEY` - Your .pem file contents

### API Keys (1 secret):
- ✅ `OPENAI_API_KEY` - Your OpenAI API key

**Total: 6 secrets**

---

## Troubleshooting

### "Authentication required" error
- Verify `DOCKERHUB_TOKEN` is correct
- Make sure token has Read, Write, Delete permissions

### "Repository not found" error
- Check `DOCKERHUB_USERNAME` matches exactly (case-sensitive)
- Docker Hub username should be lowercase

### Image won't pull on EC2
- Make sure docker-compose.yml has correct username
- Image name format: `username/drema-ai:latest` (all lowercase)
