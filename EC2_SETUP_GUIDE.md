# Complete EC2 Setup Guide - Step by Step

## 🎯 Current Status
✅ Docker image built and published to Docker Hub: `omrajput17/drema-ai:latest`  
⏳ Need to set up EC2 to pull and run this image

---

## 📋 Step-by-Step Instructions

### **STEP 1: Connect to Your EC2 Instance**

Open PowerShell or Command Prompt on your Windows PC:

```bash
ssh -i "C:\path\to\your-key.pem" ubuntu@YOUR_EC2_IP
```

**Replace:**
- `C:\path\to\your-key.pem` with the actual path to your .pem file
- `YOUR_EC2_IP` with your EC2's public IP address

**Expected Output:**
```
Welcome to Ubuntu...
ubuntu@ip-xxx-xxx-xxx-xxx:~$
```

✅ **You're in!** Proceed to Step 2.

---

### **STEP 2: Install Docker**

Copy and paste this entire block:

```bash
# Download Docker installation script
curl -fsSL https://get.docker.com -o get-docker.sh

# Run the installation
sudo sh get-docker.sh

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Verify installation
docker --version
```

**Expected Output:**
```
Docker version 24.x.x, build...
```

✅ **Docker installed!** Proceed to Step 3.

---

### **STEP 3: Install Docker Compose**

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

**Expected Output:**
```
docker-compose version 2.x.x
```

✅ **Docker Compose installed!** Proceed to Step 4.

---

### **STEP 4: Log Out and Back In**

For the docker group permissions to take effect:

```bash
# Log out
exit
```

Then SSH back in:

```bash
ssh -i "C:\path\to\your-key.pem" ubuntu@YOUR_EC2_IP
```

Test Docker works without sudo:

```bash
docker ps
```

**Expected Output:**
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

(Empty list is fine - no containers running yet)

✅ **Permissions working!** Proceed to Step 5.

---

### **STEP 5: Find and Stop Your Current Python App**

Find what's running on port 5000:

```bash
# Check if anything is using port 5000
sudo lsof -i :5000

# Find Python processes
ps aux | grep python
```

**Stop the app based on how it's running:**

**Option A - If using systemd service:**
```bash
sudo systemctl stop drema-ai
sudo systemctl disable drema-ai
```

**Option B - If running with pm2:**
```bash
pm2 stop drema-ai
pm2 delete drema-ai
```

**Option C - If running directly:**
```bash
# Kill the process (replace PID with actual number from ps aux)
kill -9 PID
```

**Option D - If you don't know:**
```bash
# This will kill any Python process running main.py
pkill -f "python main.py"
pkill -f "python3 main.py"
```

**Verify port 5000 is free:**
```bash
sudo lsof -i :5000
```

**Expected Output:** (nothing - command returns empty)

✅ **Old app stopped!** Proceed to Step 6.

---

### **STEP 6: Navigate to Your Drema Ai Directory**

```bash
# Go to your project directory
cd "$HOME/Drema Ai"

# If that doesn't work, try:
cd ~/Drema\ Ai

# Verify you're in the right place
pwd
ls -la
```

**Expected Output:**
You should see your `.env` file and other project files.

✅ **In the right directory!** Proceed to Step 7.

---

### **STEP 7: Verify Your .env File**

```bash
# Check if .env exists
cat .env
```

**Expected Output:** Should show your environment variables:
```
OPENAI_API_KEY=sk-...
LANGCHAIN_PROJECT=DremaAI
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
PORT=5000
FLASK_ENV=production
```

**If .env doesn't exist or is missing values, create it:**

```bash
cat > .env << 'EOF'
OPENAI_API_KEY=your_actual_openai_api_key_here
LANGCHAIN_PROJECT=DremaAI
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
PORT=5000
FLASK_ENV=production
EOF
```

**Then edit it to add your real API key:**
```bash
nano .env
# Press Ctrl+X, then Y, then Enter to save
```

✅ **.env file ready!** Proceed to Step 8.

---

### **STEP 8: Create docker-compose.yml**

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  drema-ai:
    image: omrajput17/drema-ai:latest
    container_name: drema-ai
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LANGCHAIN_PROJECT=${LANGCHAIN_PROJECT:-DremaAI}
      - LANGSMITH_ENDPOINT=${LANGSMITH_ENDPOINT:-https://api.smith.langchain.com}
      - PORT=${PORT:-5000}
      - FLASK_ENV=${FLASK_ENV:-production}
    volumes:
      - ./cache:/app/cache
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/boards"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - drema-network

networks:
  drema-network:
    driver: bridge
EOF
```

**Verify it was created:**
```bash
cat docker-compose.yml
```

✅ **docker-compose.yml created!** Proceed to Step 9.

---

### **STEP 9: Pull the Docker Image from Docker Hub**

```bash
# Pull the latest image
docker-compose pull
```

**Expected Output:**
```
Pulling drema-ai ... done
```

This downloads your Docker image from `omrajput17/drema-ai:latest`

✅ **Image downloaded!** Proceed to Step 10.

---

### **STEP 10: Start the Docker Container**

```bash
# Start the application in detached mode
docker-compose up -d
```

**Expected Output:**
```
Creating network "drema-ai_drema-network" ... done
Creating drema-ai ... done
```

**Verify it's running:**
```bash
docker ps
```

**Expected Output:**
```
CONTAINER ID   IMAGE                         STATUS         PORTS
abc123def456   omrajput17/drema-ai:latest   Up 10 seconds  0.0.0.0:5000->5000/tcp
```

✅ **Container running!** Proceed to Step 11.

---

### **STEP 11: Check Container Logs**

```bash
# View logs to ensure no errors
docker logs drema-ai
```

**Expected Output:**
```
Starting Flask development server...
* Running on http://0.0.0.0:5000
```

✅ **No errors!** Proceed to Step 12.

---

### **STEP 12: Test the API Locally on EC2**

```bash
# Test from inside EC2
curl http://localhost:5000/api/boards
```

**Expected Output:**
```json
{"success":true,"boards":["CBSE","ICSE","IB",...]}
```

✅ **API responding!** Proceed to Step 13.

---

### **STEP 13: Test from Your Windows PC**

Open a **new PowerShell window** on your local PC (don't close the SSH session):

```bash
curl http://YOUR_EC2_IP:5000/api/boards
```

**Replace** `YOUR_EC2_IP` with your actual EC2 public IP.

**Expected Output:**
```json
{"success":true,"boards":["CBSE","ICSE","IB",...]}
```

**If you get "Connection refused":**
- Check EC2 Security Group allows inbound traffic on port 5000
- Go to AWS Console → EC2 → Security Groups
- Add rule: Type=Custom TCP, Port=5000, Source=0.0.0.0/0

✅ **Accessible from outside!** You're done!

---

## 🎉 SUCCESS! Your App is Running on EC2

### What You've Accomplished:
- ✅ Docker installed on EC2
- ✅ Docker Compose installed
- ✅ Old Python app stopped
- ✅ Docker container running
- ✅ API accessible from internet

### Future Deployments (Fully Automatic):

From now on, just push code to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

GitHub Actions will automatically:
1. Run tests
2. Build Docker image
3. Push to Docker Hub
4. SSH into EC2 and update the container

**Your CI/CD pipeline is LIVE!** 🚀

---

## 📊 Useful Commands

### View logs:
```bash
docker logs -f drema-ai
```

### Restart container:
```bash
docker-compose restart
```

### Stop container:
```bash
docker-compose down
```

### Update to latest image:
```bash
docker-compose pull
docker-compose up -d
```

### Check container status:
```bash
docker ps
```

### Remove old images:
```bash
docker image prune -f
```

---

## 🔧 Troubleshooting

### Container won't start:
```bash
docker logs drema-ai
docker-compose down
docker-compose up -d
```

### Port already in use:
```bash
sudo lsof -i :5000
sudo kill -9 PID
docker-compose up -d
```

### Can't pull image:
```bash
docker pull omrajput17/drema-ai:latest
```

### Environment variables not working:
```bash
cat .env
docker-compose down
docker-compose up -d
```

---

## ✅ Verification Checklist

After completing all steps, verify:

- [ ] SSH into EC2 works
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Old Python app stopped
- [ ] In "Drema Ai" directory
- [ ] .env file exists with correct values
- [ ] docker-compose.yml created
- [ ] Container running (`docker ps`)
- [ ] No errors in logs (`docker logs drema-ai`)
- [ ] API works locally (`curl http://localhost:5000/api/boards`)
- [ ] API works from internet (`curl http://YOUR_EC2_IP:5000/api/boards`)

**All checked?** You're done! 🎉
