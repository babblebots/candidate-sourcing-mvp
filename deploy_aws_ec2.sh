#!/bin/bash
# Setup script for AWS EC2 (run on the instance)

echo "📦 Setting up Resume Search Engine on EC2..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.10
sudo apt-get install -y python3.10 python3.10-venv python3-pip git

# Clone your repo (or upload files)
# git clone https://github.com/babblebots/candidate-sourcing-mvp.git
# cd candidate-sourcing-mvp

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY='your-openai-api-key-here'
echo 'export OPENAI_API_KEY="your-openai-api-key-here"' >> ~/.bashrc

# Install PM2 for process management (keeps app running)
sudo apt-get install -y npm
sudo npm install -g pm2

# Start the app with PM2
pm2 start "streamlit run app.py" --name resume-search
pm2 startup
pm2 save

echo "✅ Setup complete!"
echo "🌐 Access your app at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"

