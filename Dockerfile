FROM icr.io/ibm-messaging/mq:latest

# Set environment variables
ENV LICENSE=accept
ENV MQ_QMGR_NAME=QM1
ENV MQ_APP_PASSWORD=passw0rd
ENV MQ_ADMIN_PASSWORD=passw0rd
ENV MQ_ENABLE_EMBEDDED_WEB_SERVER=1

# Expose ports
EXPOSE 1414 9443 9157

# Copy MQ configuration
COPY 20-config.mqsc /etc/mqm