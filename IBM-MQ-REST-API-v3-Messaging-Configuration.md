# IBM MQ REST API v3 Messaging Configuration

## Overview
To enable IBM MQ REST API v3 messaging endpoints (`/ibmmq/rest/v3/messaging/`), specific Liberty server configuration is required beyond the standard administrative API setup.

## Error Without Configuration
```
HTTP 403 Forbidden
MQWB0108E: The authenticated principal 'admin' is not granted access to any of the required roles: 'MQWebUser'.
```

## Required Configuration Files

### 1. Liberty Server Configuration
**File:** `/opt/mqm/web/installations/Installation1/servers/mqweb/server.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<server description="IBM MQ Web Server">
    <featureManager>
        <feature>appSecurity-2.0</feature>
        <feature>basicAuthenticationMQ-1.0</feature>
    </featureManager>

    <basicRegistry id="basic" realm="defaultRealm">
        <user name="admin" password="{xor}Lz4sLChvLTs=" />
        <user name="app" password="{xor}Lz4sLChvLTs=" />
        <group name="MQWebAdmin">
            <member name="admin" />
        </group>
        <group name="MQWebUser">
            <member name="admin" />
            <member name="app" />
        </group>
    </basicRegistry>

    <authorizationRoles id="com.ibm.mq.rest">
        <security-role name="MQWebAdmin">
            <group name="MQWebAdmin" />
        </security-role>
        <security-role name="MQWebUser">
            <group name="MQWebUser" />
        </security-role>
    </authorizationRoles>

    <cors domain="/ibmmq/rest"
          allowedOrigins="*"
          allowedMethods="GET, DELETE, POST, PUT"
          allowedHeaders="Content-Type, Authorization"
          allowCredentials="true" />
</server>
```

### 2. MQ Web Configuration
**File:** `/opt/mqm/web/installations/Installation1/servers/mqweb/mqweb.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mqweb>
    <messaging>
        <enabled>true</enabled>
        <queueManager name="*">
            <queue name="*" access="get,put,browse"/>
        </queueManager>
    </messaging>
    
    <security>
        <authorization>
            <role name="MQWebAdmin" topic="ibmmq.rest.admin.**"/>
            <role name="MQWebUser" topic="ibmmq.rest.messaging.**"/>
        </authorization>
    </security>
</mqweb>
```

### 3. Bootstrap Properties
**File:** `/opt/mqm/web/installations/Installation1/servers/mqweb/bootstrap.properties`

```properties
com.ibm.mq.rest.messaging.enabled=true
com.ibm.mq.rest.messaging.cors.allowedOrigins=*
com.ibm.mq.rest.messaging.cors.allowedMethods=GET,POST,PUT,DELETE,OPTIONS
com.ibm.mq.rest.messaging.cors.allowedHeaders=Content-Type,Authorization
com.ibm.mq.rest.messaging.cors.allowCredentials=true
```

## Key Requirements

### User Roles
- **MQWebAdmin**: Administrative API access (`/v2/admin/`)
- **MQWebUser**: Messaging API access (`/v3/messaging/`)

### Password Encoding
- Plain text: `passw0rd`
- XOR encoded: `{xor}Lz4sLChvLTs=`

### File Permissions
- Files must be owned by MQ user (typically `1001:root` in containers)
- Proper read permissions for Liberty server

## REST API Endpoints

### Administrative (v2)
```bash
curl -k -u admin:passw0rd https://localhost:9443/ibmmq/rest/v2/admin/qmgr/QM1
```

### Messaging (v3)
```bash
# Get message
curl -k -u admin:passw0rd https://localhost:9443/ibmmq/rest/v3/messaging/qmgr/QM1/queue/TEST.QUEUE/message

# Put message
curl -k -u admin:passw0rd -X POST \
  -H "Content-Type: application/json" \
  -d '{"applicationData":"Hello World"}' \
  https://localhost:9443/ibmmq/rest/v3/messaging/qmgr/QM1/queue/TEST.QUEUE/message
```

## Container Implementation Challenges

1. **File Locations**: Liberty server files are in specific nested directories
2. **User Permissions**: Container user mapping complexity
3. **Configuration Persistence**: Files must survive container restarts
4. **Service Restart**: Liberty server requires restart after configuration changes

## Alternative Approach

For containerized environments, using MQSC commands and MQ sample programs (`amqsput`, `amqsget`, `amqsbcg`) is more reliable than configuring REST API v3 messaging permissions.

## Current Working Solution

The SSE MCP server uses MQSC commands which work without additional configuration:
- `dspmq` - List queue managers
- `runmqsc` - Execute MQSC commands
- Sample programs via `podman exec` for message operations

This approach provides full MQ functionality without complex Liberty server configuration.