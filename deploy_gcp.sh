#!/bin/bash
# Deploy to GCP Cloud Run

# Configuration
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="resume-search"
REGION="us-central1"
OPENAI_API_KEY="your-openai-api-key"

echo "🚀 Deploying to GCP Cloud Run..."

# Set project
gcloud config set project $PROJECT_ID

# Build and deploy in one command
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10

echo "✅ Deployment complete!"
echo "🌐 Your app is available at the URL shown above"

