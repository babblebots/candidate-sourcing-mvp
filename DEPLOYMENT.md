# 🚀 Deployment Guide

Quick deployment options for AWS and GCP (no GitHub integrations needed).

## 📋 Prerequisites

Before deploying:
1. ✅ Build the search index locally: `python diagnose_resumes.py`
2. ✅ Have your OpenAI API key ready
3. ✅ Have `storage/` folder with search index

---

## Option 1: GCP Cloud Run (Recommended) 💰 ~$0-5/month

**Best for:** Serverless, auto-scaling, pay-per-use

### Step 1: Install Google Cloud SDK

```bash
# Install if not already installed
# macOS:
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### Step 2: Authenticate

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Step 3: Update deployment script

Edit `deploy_gcp.sh`:
```bash
PROJECT_ID="your-actual-gcp-project-id"
OPENAI_API_KEY="sk-your-actual-openai-key"
```

### Step 4: Deploy

```bash
./deploy_gcp.sh
```

**That's it!** Your app will be live at the URL shown.

### Cost Estimate:
- First 2 million requests/month: FREE
- After that: ~$0.40 per million requests
- Typical usage: $0-5/month

---

## Option 2: AWS EC2 (Free Tier) 💰 FREE for 12 months

**Best for:** Full control, always-on, free tier available

### Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2
2. Click "Launch Instance"
3. Choose:
   - **AMI:** Ubuntu 22.04 LTS (Free tier eligible)
   - **Instance Type:** t2.micro (Free tier eligible)
   - **Storage:** 20 GB (Free tier eligible)
4. **Security Group:** Add rule:
   - Type: Custom TCP
   - Port: 8501
   - Source: 0.0.0.0/0 (or your IP for security)
5. Create/Select key pair
6. Launch instance

### Step 2: Connect to Instance

```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

### Step 3: Upload Your Files

```bash
# From your local machine
scp -i your-key.pem -r /Users/test/Desktop/test-repo/sourcing-mvp ubuntu@your-instance-ip:~/
```

### Step 4: Setup on Instance

```bash
# SSH into instance
cd sourcing-mvp

# Update deploy script with your API key
nano deploy_aws_ec2.sh
# Change: OPENAI_API_KEY='your-actual-key'

# Run setup
chmod +x deploy_aws_ec2.sh
./deploy_aws_ec2.sh
```

**Access your app at:** `http://your-instance-ip:8501`

### Cost Estimate:
- **Free tier (12 months):** $0/month
- **After free tier:** ~$8-10/month (t2.micro)

---

## Option 3: AWS Lightsail (Simplest) 💰 $3.50/month

**Best for:** Easiest AWS option, predictable pricing

### Step 1: Create Lightsail Instance

1. Go to AWS Lightsail console
2. Click "Create instance"
3. Choose:
   - **Platform:** Linux/Unix
   - **Blueprint:** OS Only → Ubuntu 22.04 LTS
   - **Instance plan:** $3.50/month (512 MB RAM)
4. Create instance

### Step 2: Upload and Setup

Same as EC2 steps above, or use the Lightsail browser SSH.

### Step 3: Open Port 8501

1. Go to instance → Networking
2. Add firewall rule: Custom TCP 8501

---

## Option 4: Docker + Any Platform 💰 Varies

**Best for:** Maximum flexibility

### Build Docker Image

```bash
# Make sure storage/ folder exists
docker build -t resume-search .

# Test locally
docker run -p 8501:8501 -e OPENAI_API_KEY='your-key' resume-search
```

### Deploy Docker Image

Can deploy to:
- **AWS ECS/Fargate:** ~$15/month
- **GCP Cloud Run:** ~$0-5/month (recommended)
- **DigitalOcean App Platform:** ~$5/month
- **Fly.io:** ~$0-3/month
- **Railway:** ~$5/month
- **Render:** ~$7/month

---

## Quick Comparison

| Platform | Cost | Setup Time | Best For |
|----------|------|------------|----------|
| **GCP Cloud Run** | $0-5/mo | 5 min | Minimal cost, auto-scale |
| **AWS EC2 Free Tier** | Free 12mo | 15 min | Learning, testing |
| **AWS Lightsail** | $3.50/mo | 10 min | Simple, predictable |
| **AWS EC2 (paid)** | $8-10/mo | 15 min | Full control |
| **Docker (various)** | Varies | 10 min | Flexibility |

---

## 🔐 Security Tips

1. **Never commit API keys** - Use environment variables
2. **Restrict firewall** - Only allow your IP if possible
3. **Use HTTPS** - Set up SSL/TLS for production
4. **Backup storage/** - Keep a local copy of your search index
5. **Monitor costs** - Set up billing alerts

---

## 🐛 Troubleshooting

### App won't start
```bash
# Check if storage/ folder exists
ls -la storage/

# Check environment variable
echo $OPENAI_API_KEY
```

### Port already in use
```bash
# Kill existing Streamlit process
pkill -f streamlit
```

### Out of memory
- Increase instance size
- For GCP Cloud Run: Change `--memory 2Gi` to `4Gi`

---

## 📊 Monitoring

### GCP Cloud Run
```bash
# View logs
gcloud run logs tail resume-search --region us-central1
```

### AWS EC2
```bash
# View app logs
pm2 logs resume-search

# Monitor resources
htop
```

---

## 🔄 Updating the App

### GCP Cloud Run
```bash
# Just run deploy script again
./deploy_gcp.sh
```

### AWS EC2
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Pull latest changes
cd sourcing-mvp
git pull

# Restart app
pm2 restart resume-search
```

---

## 💡 Recommendations

- **For testing/demo:** AWS EC2 Free Tier
- **For production (low cost):** GCP Cloud Run
- **For simplicity:** AWS Lightsail
- **For flexibility:** Docker + any platform

Need help? Check the main [README.md](README.md) or open an issue.

