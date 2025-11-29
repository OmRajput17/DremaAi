# Docker Guide - Drema AI Chunk Retrieval API

This guide provides all the commands needed to build and run the Drema AI application using Docker.

---

## Prerequisites

- **Docker Desktop** installed and running
- **OPENAI_API_KEY** configured in `.env` file

---

## 🐳 Building the Docker Image

### Build Image
```bash
docker build -t drema-ai:latest .
```

### Verify Image was Created
```bash
docker images | findstr drema-ai
```

**Expected Output:**
```
drema-ai    latest    <image-id>    <time>    <size>
```

---

## 🚀 Running the Container

### Option 1: Run with Environment File (Recommended)
```bash
docker run -d `
  --name drema-ai-container `
  -p 8080:8080 `
  --env-file .env `
  drema-ai:latest
```

### Option 2: Run with Inline Environment Variables
```bash
docker run -d `
  --name drema-ai-container `
  -p 8080:8080 `
  -e OPENAI_API_KEY=your_openai_api_key_here `
  -e LANGCHAIN_API_KEY=your_langchain_key_here `
  drema-ai:latest
```

### Option 3: Run in Interactive Mode (for debugging)
```bash
docker run -it `
  --name drema-ai-container `
  -p 8080:8080 `
  --env-file .env `
  drema-ai:latest
```

### Option 4: Run with Volume Mounts (persist cache and logs)
```bash
docker run -d `
  --name drema-ai-container `
  -p 8080:8080 `
  --env-file .env `
  -v ${PWD}/cache:/app/cache `
  -v ${PWD}/logs:/app/logs `
  drema-ai:latest
```

---

## 🔍 Managing the Container

### Check Running Containers
```bash
docker ps
```

### Check All Containers (including stopped)
```bash
docker ps -a
```

### View Container Logs
```bash
docker logs drema-ai-container
```

### Follow Logs in Real-time
```bash
docker logs -f drema-ai-container
```

### View Last 100 Log Lines
```bash
docker logs --tail 100 drema-ai-container
```

### Execute Command Inside Container
```bash
docker exec -it drema-ai-container bash
```

### Inspect Container Details
```bash
docker inspect drema-ai-container
```

### Check Container Resource Usage
```bash
docker stats drema-ai-container
```

---

## 🛑 Stopping and Removing

### Stop the Container
```bash
docker stop drema-ai-container
```

### Start the Container Again
```bash
docker start drema-ai-container
```

### Restart the Container
```bash
docker restart drema-ai-container
```

### Remove the Container
```bash
docker rm drema-ai-container
```

### Force Remove Running Container
```bash
docker rm -f drema-ai-container
```

### Remove the Image
```bash
docker rmi drema-ai:latest
```

### Remove All Stopped Containers
```bash
docker container prune
```

### Remove Unused Images
```bash
docker image prune
```

---

## 🧪 Testing the Containerized API

After starting the container, test the API:

### Test Health/Boards Endpoint
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/boards" -Method Get | ConvertTo-Json
```

### Test Chunk Retrieval
```powershell
$body = @{
    board = "CBSE"
    class = "11"
    subject = "Physics"
    topics = @("1")
    num_chunks = 5
    difficulty = "medium"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/retrieve_chunks" `
    -Method Post `
    -Body $body `
    -ContentType "application/json" | ConvertTo-Json -Depth 10
```

---

## 📦 Saving and Loading Images

### Save Image to TAR File
```bash
docker save drema-ai:latest -o drema-ai-image.tar
```

### Load Image from TAR File
```bash
docker load -i drema-ai-image.tar
```

### Export Container to TAR File
```bash
docker export drema-ai-container -o drema-ai-container.tar
```

---

## 🏷️ Tagging and Pushing to Registry

### Tag for Docker Hub
```bash
docker tag drema-ai:latest yourusername/drema-ai:latest
docker tag drema-ai:latest yourusername/drema-ai:v1.0
```

### Push to Docker Hub
```bash
docker login
docker push yourusername/drema-ai:latest
docker push yourusername/drema-ai:v1.0
```

### Pull from Docker Hub
```bash
docker pull yourusername/drema-ai:latest
```

---

## 🔧 Troubleshooting

### Container Won't Start
```bash
# Check logs for errors
docker logs drema-ai-container

# Run in interactive mode to see errors
docker run -it --env-file .env -p 8080:8080 drema-ai:latest
```

### Port Already in Use
```bash
# Use a different port
docker run -d --name drema-ai-container -p 9000:8080 --env-file .env drema-ai:latest
```

### Environment Variables Not Working
```bash
# Verify .env file exists
ls .env

# Check environment variables inside container
docker exec drema-ai-container env
```

### Rebuild Image (no cache)
```bash
docker build --no-cache -t drema-ai:latest .
```

### Clean Everything and Start Fresh
```bash
# Stop and remove container
docker stop drema-ai-container
docker rm drema-ai-container

# Remove image
docker rmi drema-ai:latest

# Rebuild
docker build -t drema-ai:latest .

# Run again
docker run -d --name drema-ai-container -p 8080:8080 --env-file .env drema-ai:latest
```

---

## 📋 Quick Start (Copy-Paste Ready)

```powershell
# 1. Build the image
docker build -t drema-ai:latest .

# 2. Run the container
docker run -d --name drema-ai-container -p 8080:8080 --env-file .env drema-ai:latest

# 3. Check logs
docker logs -f drema-ai-container

# 4. Test API (in new terminal)
Invoke-RestMethod -Uri "http://localhost:8080/api/boards" -Method Get | ConvertTo-Json

# 5. Stop when done
docker stop drema-ai-container
```

---

## 🐳 Docker Compose (Optional)

Create a `docker-compose.yml` for easier management:

```yaml
version: '3.8'

services:
  drema-ai:
    build: .
    image: drema-ai:latest
    container_name: drema-ai-container
    ports:
      - "8080:8080"
    env_file:
      - .env
    volumes:
      - ./cache:/app/cache
      - ./logs:/app/logs
    restart: unless-stopped
```

**Usage:**
```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

---

## 📊 Image Information

After building, check the image details:

```bash
docker images drema-ai:latest
docker history drema-ai:latest
docker inspect drema-ai:latest
```

---

## 🔐 Security Notes

- Never commit `.env` file to Git
- Use Docker secrets for production deployments
- Keep base image updated (`docker pull python:3.11-slim`)
- Scan image for vulnerabilities: `docker scan drema-ai:latest`

---

## 📝 Container Lifecycle

```
Build → Run → Test → Stop → Remove
  ↓       ↓      ↓      ↓       ↓
docker  docker docker docker  docker
build   run    logs   stop    rm
```

---

**Last Updated**: November 29, 2025  
**Docker Image**: `drema-ai:latest`  
**Base Image**: `python:3.11-slim`  
**Exposed Port**: 8080
