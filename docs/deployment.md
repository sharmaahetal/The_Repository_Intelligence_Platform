# Repository Intelligence Platform (RIP) — Deployment & Production Guide

This guide outlines end-to-end multi-cloud deployment instructions for the Repository Intelligence Platform (RIP) FastAPI backend, PostgreSQL database, Redis caching layer, Cloudflare R2 object storage, and Manifest V3 browser extension.

---

## 1. Environment Configuration (`.env`)

Create a production `.env` file in the root directory based on `.env.example`:

```env
# Application Environment
APP_ENV=production
LOG_LEVEL=INFO
SECRET_KEY=your-production-secret-key-change-this

# GitHub API Credentials
GITHUB_TOKEN=ghp_your_production_github_personal_access_token
GITHUB_API_URL=https://api.github.com
REQUEST_TIMEOUT_SECONDS=10.0
MAX_RETRIES=3

# PostgreSQL Database (Neon / Cloud SQL / RDS)
DATABASE_URL=postgresql+asyncpg://user:password@ep-cool-name-123456.us-east-2.aws.neon.tech/rip_db?ssl=require
DB_ECHO=false
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis Cache (Upstash / ElastiCache)
REDIS_URL=rediss://default:your-upstash-password@cool-redis-12345.upstash.io:6379

# Object Storage (Cloudflare R2 / AWS S3)
STORAGE_PROVIDER=s3
S3_BUCKET_NAME=rip-model-registry
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
AWS_ACCESS_KEY_ID=your_cloudflare_r2_access_key
AWS_SECRET_ACCESS_KEY=your_cloudflare_r2_secret_key
```

---

## 2. FastAPI Backend Deployment

### **Option A: Railway (Recommended)**
1. Connect your GitHub repository to [Railway](https://railway.app).
2. Create a new service selecting the root `Dockerfile`.
3. Set environment variables in the Railway dashboard.
4. Set custom domain (e.g. `https://api.yourdomain.com`).

### **Option B: Render**
1. Create a new **Web Service** on [Render](https://render.com).
2. Environment: `Docker`.
3. Branch: `main`.
4. Add environment variables under service configuration.

### **Option C: Fly.io**
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Initialize app: `fly launch`
3. Deploy container: `fly deploy`

---

## 3. Database & Cache Provisioning

### **Neon PostgreSQL**
1. Create a serverless PostgreSQL project on [Neon](https://neon.tech).
2. Copy the connection string with `sslmode=require`.
3. Set `DATABASE_URL` in environment variables.

### **Upstash Redis**
1. Create a serverless Redis store on [Upstash](https://upstash.com).
2. Copy the TLS connection URL (`rediss://...`).
3. Set `REDIS_URL` in environment variables.

---

## 4. Object Storage Provisioning (Cloudflare R2)

1. Log in to Cloudflare Dashboard $\rightarrow$ **R2 Object Storage**.
2. Create bucket `rip-model-registry`.
3. Create API token with Edit permissions.
4. Set `S3_BUCKET_NAME` and `S3_ENDPOINT_URL` in environment variables.

---

## 5. Cross-Browser Extension (Manifest V3) Publishing

### **Packaging the Extension**:
```bash
cd extension
npm install
npm run build
# Zip contents of dist/ directory
zip -r rip-extension-v1.0.0.zip dist/
```

### **Store Submissions**:

1. **Chrome Web Store**:
   - Go to [Chrome Developer Dashboard](https://chrome.google.com/webstore/devconsole).
   - Upload `rip-extension-v1.0.0.zip`.
   - Complete store listing (icons, screenshots, privacy policy).

2. **Microsoft Edge Add-ons**:
   - Go to [Microsoft Partner Center](https://partner.microsoft.com/dashboard/microsoftedge).
   - Upload the same Manifest V3 `.zip` package.

3. **Firefox Add-ons (AMO)**:
   - Go to [Mozilla Add-on Developer Hub](https://addons.mozilla.org/developers/).
   - Submit package for automated signing.

---

## 6. Health & Verification Endpoints

Once deployed, verify deployment status via HTTP:

- **Liveness Probe**: `GET https://api.yourdomain.com/api/v1/health/live`
- **Readiness Probe**: `GET https://api.yourdomain.com/api/v1/health/ready`
- **OpenAPI Reference**: `GET https://api.yourdomain.com/docs`
