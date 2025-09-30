# IBM MQ Server Docker Setup

## Quick Start

1. **Build and run the container with Podman:**
   ```bash
   # Build the image
   podman build -t ibm-mq-server .
   
   # Run the container
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
   ```

2. **Access the MQ Web Console:**
   - URL: https://localhost:9443/ibmmq/console
   - Username: admin
   - Password: passw0rd

3. **REST API Base URL:**
   - https://localhost:9443/ibmmq/rest/v2/

## Connection Details

- **Queue Manager:** QM1
- **Test Queue:** TEST.QUEUE
- **Channel:** DEV.APP.SVRCONN
- **Host:** localhost
- **Port:** 1414

## Client Testing

Use these connection parameters in your MQ client:
- Server: localhost:1414
- Queue Manager: QM1
- Channel: DEV.APP.SVRCONN
- Queue: TEST.QUEUE

## REST API Examples

```bash
# Get queue manager status
curl -k -u admin:passw0rd https://localhost:9443/ibmmq/rest/v2/admin/qmgr/QM1

# Test message operations
podman exec ibm-mq-server bash -c "echo 'Hello World' | /opt/mqm/samp/bin/amqsput TEST.QUEUE QM1"
podman exec ibm-mq-server /opt/mqm/samp/bin/amqsget TEST.QUEUE QM1
```