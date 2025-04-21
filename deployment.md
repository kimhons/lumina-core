# Deployment Configuration for Lumina Core

This file contains deployment configuration for the Lumina Core component.

## Docker Configuration

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY . .
RUN pip install -e .

EXPOSE 8000

CMD ["python", "-m", "lumina.api.gateway"]
```

## Kubernetes Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lumina-core
  labels:
    app: lumina-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lumina-core
  template:
    metadata:
      labels:
        app: lumina-core
    spec:
      containers:
      - name: lumina-core
        image: lumina-core:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
          requests:
            cpu: "500m"
            memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: lumina-core-service
spec:
  selector:
    app: lumina-core
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

## Environment Variables

```
# Development
ENVIRONMENT=development
LOG_LEVEL=debug
API_PORT=8000

# Production
ENVIRONMENT=production
LOG_LEVEL=info
API_PORT=8000
```

## Deployment Instructions

1. Build the Docker image:
   ```
   docker build -t lumina-core:latest .
   ```

2. Run locally:
   ```
   docker run -p 8000:8000 -e ENVIRONMENT=development lumina-core:latest
   ```

3. Deploy to Kubernetes:
   ```
   kubectl apply -f kubernetes.yaml
   ```

4. Monitor deployment:
   ```
   kubectl get pods -l app=lumina-core
   ```
