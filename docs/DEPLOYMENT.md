# Deployment Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB (optional, for caching)
- Redis (optional, for caching)
- Virtuoso or GraphDB (optional, for production RDF store)

## Production Deployment

### Backend Deployment

#### Option 1: Docker (Recommended)

1. Create `Dockerfile` in backend directory:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Build and run:
```bash
docker build -t artwork-provenance-backend .
docker run -p 8000:8000 --env-file .env artwork-provenance-backend
```

#### Option 2: Manual Deployment

1. Set up production environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

2. Configure production settings in `.env`:
```
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

3. Run with Gunicorn:
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Option 3: Cloud Platforms

**Heroku:**
```bash
heroku create artwork-provenance-api
git push heroku main
```

**AWS Elastic Beanstalk:**
```bash
eb init -p python-3.11 artwork-provenance
eb create artwork-provenance-env
eb deploy
```

**Google Cloud Run:**
```bash
gcloud run deploy artwork-provenance --source .
```

### Frontend Deployment

#### Option 1: Static Hosting

1. Build for production:
```bash
cd frontend
npm run build
```

2. Deploy `dist/` folder to:
- **Netlify**: Drop folder or connect Git
- **Vercel**: `vercel --prod`
- **GitHub Pages**: Push to gh-pages branch
- **AWS S3 + CloudFront**
- **Azure Static Web Apps**

#### Option 2: Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Database Setup

#### MongoDB (Optional)

For production, use managed service:
- **MongoDB Atlas** (recommended)
- **AWS DocumentDB**
- **Azure Cosmos DB**

#### Triple Store (Recommended for Production)

**Virtuoso:**
```bash
docker run -d \
  --name virtuoso \
  -p 8890:8890 \
  -e DBA_PASSWORD=dba \
  -v /path/to/data:/data \
  openlink/virtuoso-opensource-7
```

**GraphDB:**
```bash
docker run -d \
  --name graphdb \
  -p 7200:7200 \
  ontotext/graphdb
```

## Environment Variables

### Backend
```
DEBUG=False
HOST=0.0.0.0
PORT=8000

RDF_STORE_TYPE=virtuoso
RDF_STORE_URL=http://virtuoso:8890/sparql
VIRTUOSO_USER=dba
VIRTUOSO_PASSWORD=your_secure_password

MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net
REDIS_URL=redis://redis:6379

EUROPEANA_API_KEY=your_key_here
```

### Frontend
```
VITE_API_URL=https://api.yourdom ain.com/api
```

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Frontend
    location / {
        root /var/www/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## SSL/HTTPS

Use Let's Encrypt with Certbot:
```bash
sudo certbot --nginx -d yourdomain.com
```

## Monitoring

### Application Monitoring
- **Sentry**: Error tracking
- **DataDog**: APM and metrics
- **New Relic**: Performance monitoring

### Logging
```python
# Add to app/main.py
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
logging.basicConfig(handlers=[handler], level=logging.INFO)
```

## Backup Strategy

### RDF Data
```bash
# Export from Virtuoso
isql-v "EXEC=dump_one_graph('http://arp-greatteam.org/heritage-provenance', 'file', 'backup.ttl');"
```

### MongoDB
```bash
mongodump --uri="mongodb://..." --out=/backup
```

## Performance Optimization

1. **Enable caching**: Use Redis for query results
2. **CDN**: Use CloudFlare or AWS CloudFront for frontend
3. **Database indexing**: Add indexes to frequently queried fields
4. **SPARQL query optimization**: Use FILTER after basic graph patterns
5. **Load balancing**: Use multiple backend instances

## Security Checklist

- [ ] HTTPS enabled
- [ ] CORS configured properly
- [ ] API rate limiting enabled
- [ ] Authentication implemented
- [ ] Secrets in environment variables
- [ ] Database access restricted
- [ ] Input validation enabled
- [ ] SQL/SPARQL injection prevention
- [ ] Regular security updates

## Scaling

### Horizontal Scaling
- Multiple backend instances behind load balancer
- Distributed RDF store (Virtuoso cluster)
- CDN for frontend assets

### Vertical Scaling
- Increase server resources
- Optimize RDF queries
- Add caching layers

## Troubleshooting

### Backend not starting
```bash
# Check logs
tail -f app.log

# Verify Python version
python --version

# Test dependencies
pip install -r requirements.txt
```

### Frontend build errors
```bash
# Clear cache
rm -rf node_modules dist
npm install
npm run build
```

### SPARQL queries slow
- Add RDF indexes
- Optimize query patterns
- Enable query caching
- Consider materialized views

## Maintenance

### Regular Tasks
- Weekly: Check error logs
- Monthly: Update dependencies
- Quarterly: Security audit
- Yearly: Performance review

### Updates
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
npm update
```
