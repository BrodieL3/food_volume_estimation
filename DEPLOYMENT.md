# Food Volume Estimation API - Google Cloud Run Deployment Guide

This guide will help you deploy the Food Volume Estimation API to Google Cloud Run.

## Prerequisites

✅ **Completed:**

- [x] Python 3.9 Docker container built
- [x] Google Cloud CLI installed
- [x] Docker Desktop installed and running

📋 **To Do Before Deployment:**

1. **Create a Google Cloud Project**

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Note your Project ID

2. **Set up Billing**

   - Enable billing for your project
   - Google Cloud Run has a generous free tier

3. **Authentication**
   - Run: `gcloud auth login`
   - Follow the browser authentication flow

## Deployment Options

### Option 1: Automated Deployment (Recommended)

Run the provided deployment script:

```bash
./deploy.sh
```

The script will:

- Guide you through the setup process
- Enable required APIs
- Build and push the Docker image
- Deploy to Cloud Run
- Provide you with the service URL

### Option 2: Manual Deployment

If you prefer to deploy manually:

1. **Set your project**

   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable APIs**

   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

3. **Configure Docker**

   ```bash
   gcloud auth configure-docker
   ```

4. **Build and tag image**

   ```bash
   docker build -t gcr.io/YOUR_PROJECT_ID/food-volume-estimator .
   ```

5. **Push to registry**

   ```bash
   docker push gcr.io/YOUR_PROJECT_ID/food-volume-estimator
   ```

6. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy food-volume-estimator \
     --image gcr.io/YOUR_PROJECT_ID/food-volume-estimator \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --memory 1Gi \
     --cpu 1
   ```

## Testing Your Deployment

After deployment, you'll receive a service URL. Test it with:

### Health Check

```bash
curl https://YOUR_SERVICE_URL/
```

### Volume Estimation

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "img": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "food_type": "apple"
  }' \
  https://YOUR_SERVICE_URL/predict
```

## API Usage

### Endpoints

- **GET /** - Health check
- **POST /predict** - Volume estimation

### Request Format

```json
{
  "img": "base64_encoded_image_data",
  "food_type": "apple",
  "plate_diameter": 24.0
}
```

### Response Format

```json
{
  "food_type_match": "apple",
  "weight_grams": 12.5,
  "volumes_ml": [8.3, 5.0],
  "density_g_per_ml": 0.6,
  "status": "success",
  "image_shape": [480, 640, 3]
}
```

### Supported Food Types

- apple
- banana
- rice
- chicken
- pasta
- salad
- default (unknown foods)

## Monitoring and Management

- **Cloud Run Console**: https://console.cloud.google.com/run
- **Logs**: `gcloud logging read "resource.type=cloud_run_revision"`
- **Metrics**: Available in the Cloud Run console

## Cost Estimation

Google Cloud Run pricing (as of 2024):

- **Free tier**: 2 million requests/month, 400,000 GB-seconds/month
- **After free tier**: $0.40 per million requests + compute time charges
- **This API**: Typically costs less than $5/month for moderate usage

## Scaling Configuration

The current deployment is configured with:

- **Memory**: 1 GB
- **CPU**: 1 vCPU
- **Max instances**: 10
- **Timeout**: 300 seconds

## Security

- The API is deployed as **publicly accessible** (no authentication required)
- For production use, consider adding authentication
- The container runs as a non-root user for security

## Troubleshooting

### Common Issues

1. **Authentication Error**

   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Permission Denied**

   - Ensure billing is enabled
   - Check that required APIs are enabled

3. **Build Fails**

   - Ensure Docker Desktop is running
   - Check available disk space

4. **Deployment Timeout**
   - The container might be taking too long to start
   - Check the logs in Cloud Run console

### Getting Help

- **Cloud Run Documentation**: https://cloud.google.com/run/docs
- **Google Cloud Support**: Available through the console

## Next Steps

1. **Add Real Models**: Replace dummy estimators with actual ML models
2. **Add Authentication**: Implement API keys or OAuth
3. **Add Monitoring**: Set up alerting and dashboards
4. **Add HTTPS**: Cloud Run provides HTTPS by default
5. **Custom Domain**: Configure a custom domain if needed

## Development

To run locally:

```bash
docker run -p 8080:8080 food-volume-estimator
```

Then visit http://localhost:8080/ to test.
