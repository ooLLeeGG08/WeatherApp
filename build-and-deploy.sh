#!/bin/bash

# Weather App Kubernetes Deployment Script

set -e

echo "🏗️  Building Weather App..."

# Build Docker image
echo "Building Docker image..."
docker build -t weather-app:latest .

echo "✅ Docker image built successfully!"

# Apply Kubernetes manifests
echo "🚀 Deploying to Kubernetes..."

# Create namespace if it doesn't exist
kubectl create namespace weather-app --dry-run=client -o yaml | kubectl apply -f -

# Apply all Kubernetes resources
kubectl apply -f k8s/ -n weather-app

echo "✅ Deployment completed!"

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/weather-app -n weather-app

echo "🎉 Weather App is now running on Kubernetes!"

# Show service information
echo "📋 Service Information:"
kubectl get services -n weather-app

# Show pod status
echo "📋 Pod Status:"
kubectl get pods -n weather-app

# Show ingress information
echo "📋 Ingress Information:"
kubectl get ingress -n weather-app

echo ""
echo "🌐 To access the app:"
echo "   Local access: kubectl port-forward service/weather-app-service 8080:80 -n weather-app"
echo "   Then visit: http://localhost:8080"
echo ""
echo "   External access (if ingress is configured): http://weather-app.local"
echo "   (Add '127.0.0.1 weather-app.local' to your /etc/hosts file for local testing)"