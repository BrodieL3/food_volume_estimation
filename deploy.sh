#!/bin/bash

# Google Cloud Run deployment script for Food Volume Estimation API

# Set variables
PROJECT_ID="food-volume-estimator"  # Replace with your actual project ID
SERVICE_NAME="food-volume-estimator"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Food Volume Estimation API - Cloud Run Deployment${NC}"
echo "=================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Pre-deployment checklist:${NC}"
echo "1. Make sure you have a Google Cloud Project created"
echo "2. Enable the following APIs in your project:"
echo "   - Cloud Run API"
echo "   - Container Registry API"
echo "   - Artifact Registry API"
echo "3. Set up billing for your project"
echo ""

read -p "Have you completed the above steps? (y/n): " -n 1 -r
echo ""
if [[ ! $PRESPONSE =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  Please complete the checklist and run this script again.${NC}"
    exit 0
fi

# Get project ID from user if not set
if [ "$PROJECT_ID" = "your-project-id" ]; then
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ Project ID cannot be empty${NC}"
        exit 1
    fi
    IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
fi

echo -e "${GREEN}🔧 Setting up Google Cloud configuration...${NC}"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${GREEN}🔌 Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Configure Docker to use gcloud as a credential helper
echo -e "${GREEN}🐳 Configuring Docker for Google Container Registry...${NC}"
gcloud auth configure-docker

echo -e "${GREEN}🏗️  Building and tagging Docker image...${NC}"
docker build -t $IMAGE_NAME .

echo -e "${GREEN}📤 Pushing image to Google Container Registry...${NC}"
docker push $IMAGE_NAME

echo -e "${GREEN}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --timeout 300 \
    --set-env-vars="PORT=8080"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo ""
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    echo -e "${GREEN}🌐 Your API is now available at:${NC}"
    echo "   $SERVICE_URL"
    echo ""
    echo -e "${GREEN}🧪 Test your API:${NC}"
    echo "   Health check: curl $SERVICE_URL/"
    echo "   Prediction: curl -X POST -H \"Content-Type: application/json\" -d '{\"img\":\"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==\",\"food_type\":\"apple\"}' $SERVICE_URL/predict"
    echo ""
    echo -e "${GREEN}📊 Monitor your service:${NC}"
    echo "   Cloud Run Console: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/metrics?project=$PROJECT_ID"
    
else
    echo -e "${RED}❌ Deployment failed. Check the error messages above.${NC}"
    exit 1
fi 