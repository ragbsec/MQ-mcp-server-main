#!/bin/bash
set -e

echo "=== Starting IBM MQ Server ==="

# Start Podman machine
echo "Starting Podman machine..."
podman machine start

# Build IBM MQ image
echo "Building IBM MQ image..."
podman build -t ibm-mq-server .

# Run IBM MQ container
echo "Starting IBM MQ container..."
podman run -d --name ibm-mq-server \
  -p 1414:1414 \
  -p 9443:9443 \
  -p 9157:9157 \
  -e LICENSE=accept \
  -e MQ_QMGR_NAME=QM1 \
  -e MQ_APP_PASSWORD=passw0rd \
  -e MQ_ADMIN_PASSWORD=passw0rd \
  -e MQ_ENABLE_EMBEDDED_WEB_SERVER=1 \
  ibm-mq-server

# Wait for MQ to initialize
echo "Waiting for IBM MQ to initialize..."
sleep 30

# Test MQ REST API
echo "Testing IBM MQ REST API..."
curl -k -u admin:passw0rd https://localhost:9443/ibmmq/rest/v2/admin/qmgr/QM1

echo "=== IBM MQ Server Setup Complete ==="
echo "MQ Web Console: https://localhost:9443/ibmmq/console (admin/passw0rd)"