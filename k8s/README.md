# Weather App Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the weather app to a Kubernetes cluster.

## Prerequisites

- Docker installed and running
- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured to connect to your cluster
- NGINX Ingress Controller (for external access)

## Quick Start

### Option 1: Automated Deployment
```bash
./build-and-deploy.sh
```

### Option 2: Manual Deployment
```bash
# Build the Docker image
docker build -t weather-app:latest .

# Create namespace
kubectl create namespace weather-app

# Deploy all resources
kubectl apply -f k8s/ -n weather-app

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s deployment/weather-app -n weather-app
```

## Kubernetes Resources

### Deployment (`deployment.yaml`)
- **Replicas**: 3 pods for high availability
- **Resource Limits**: 256Mi memory, 500m CPU per pod
- **Health Checks**: Liveness and readiness probes on `/` endpoint
- **Environment**: Production Flask configuration

### Service (`service.yaml`)
- **Type**: ClusterIP (internal cluster access)
- **Port**: 80 → 5000 (forwards to Flask app)

### Ingress (`ingress.yaml`)
- **Host**: weather-app.local
- **Path**: / (all traffic)
- **Backend**: weather-app-service:80

### ConfigMap (`configmap.yaml`)
- Flask environment variables
- Easily configurable without rebuilding images

## Accessing the Application

### Local Development (Port Forward)
```bash
kubectl port-forward service/weather-app-service 8080:80 -n weather-app
```
Then visit: http://localhost:8080

### External Access (Ingress)
1. Ensure NGINX Ingress Controller is installed:
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

2. Add to `/etc/hosts`:
```
127.0.0.1 weather-app.local
```

3. Visit: http://weather-app.local

### LoadBalancer (Cloud Environments)
To use a LoadBalancer service instead of Ingress:
```bash
kubectl patch service weather-app-service -n weather-app -p '{"spec":{"type":"LoadBalancer"}}'
```

## Management Commands

### View Resources
```bash
kubectl get all -n weather-app
```

### View Logs
```bash
kubectl logs -f deployment/weather-app -n weather-app
```

### Scale Deployment
```bash
kubectl scale deployment weather-app --replicas=5 -n weather-app
```

### Update Image
```bash
kubectl set image deployment/weather-app weather-app=weather-app:v2.0.0 -n weather-app
```

### Delete Everything
```bash
kubectl delete namespace weather-app
```

## Configuration

### Environment Variables
Modify `configmap.yaml` to change Flask configuration:
```yaml
data:
  FLASK_ENV: "production"
  FLASK_RUN_HOST: "0.0.0.0"
  FLASK_RUN_PORT: "5000"
```

### Resource Limits
Adjust in `deployment.yaml`:
```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

### Ingress Host
Change the hostname in `ingress.yaml`:
```yaml
rules:
- host: your-domain.com
```

## Monitoring

### Health Checks
The deployment includes:
- **Liveness Probe**: Restarts unhealthy containers
- **Readiness Probe**: Routes traffic only to ready containers

### Metrics
For production monitoring, consider adding:
- Prometheus metrics
- Grafana dashboards
- Log aggregation (ELK stack)

## Security Considerations

### Production Recommendations
1. **Secrets Management**: Move API keys to Kubernetes Secrets
2. **Network Policies**: Restrict pod-to-pod communication
3. **RBAC**: Implement proper access controls
4. **Image Security**: Scan images for vulnerabilities
5. **TLS**: Enable HTTPS with cert-manager

### API Key Security
Currently, the OpenWeatherMap API key is hardcoded. For production:
```bash
kubectl create secret generic weather-api-key \
  --from-literal=API_KEY=your-actual-api-key \
  -n weather-app
```

Then reference in deployment:
```yaml
env:
- name: OPENWEATHER_API_KEY
  valueFrom:
    secretKeyRef:
      name: weather-api-key
      key: API_KEY
```