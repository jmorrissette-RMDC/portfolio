# ADR-047: MCP Request Logging

Status: Accepted
Date: 2026-01-10
Updated: 2026-01-11

## Context

Joshua26 MADs expose tools via MCP. For operational visibility and audit trails, we need to track:
- What tools are being called
- When they are called
- From where (client IP)
- Success or failure

Individual applications (like Langflow) may not have native LDAP/SSO support for user attribution. Rather than implement auth in each application, we handle logging as a cross-cutting concern in the shared mad-core library.

## Decision

All MCP tool invocations are logged by mad-core automatically to stdout/stderr (Docker logs).

### Log Format

Each log entry contains:

```
timestamp | tool_name | client_ip | params_summary | status | duration_ms
```

Example:
```
2026-01-10T16:45:23.456Z | flow_create | 192.168.1.50 | {name:"research"} | success | 234
2026-01-10T16:45:25.789Z | browser_navigate | 192.168.1.50 | {url:"https://..."} | success | 1523
2026-01-10T16:45:30.123Z | docs_read | 192.168.1.50 | {documentId:"1abc..."} | error | 89
```

Fields:
- timestamp: ISO 8601 with milliseconds
- tool_name: The MCP tool that was called
- client_ip: IP address from HTTP request
- params_summary: Truncated/sanitized parameters (max 100 chars)
- status: success | error
- duration_ms: Execution time in milliseconds

### Parameter Sanitization

To avoid logging sensitive data:
- Truncate long values (>50 chars show first 20 + "...")
- Never log fields named: password, secret, token, key, credential
- Full parameters available in debug mode only

### Log Destination

Logs are written to **stdout/stderr** following container best practices:

- **Info/success logs** → stdout
- **Error logs** → stderr
- **Format**: Structured JSON (one entry per line)

Docker automatically captures these streams. Access logs via:
```bash
docker logs <container-name>
docker-compose logs -f <service-name>
```

### Implementation in mad-core

The MadServer class wraps tool execution:

```python
# Pseudocode
async executeTool(name, params, clientIp):
    start = Date.now()
    try:
        result = await tool.execute(params)
        self.log(name, clientIp, params, 'success', Date.now() - start)
        return result
    except error:
        self.log(name, clientIp, params, 'error', Date.now() - start)
        raise error

def log(self, ...):
    entry = json.dumps({...})
    if level == 'error':
        print(entry, file=sys.stderr)
    else:
        print(entry)
```

### Optional Client Identity Header

For attributed requests, clients may pass:
```
X-Client-Identity: user@domain.com
```

If present, logged as additional field:
```
2026-01-10T16:45:23.456Z | flow_create | 192.168.1.50 | user@domain.com | {name:"research"} | success | 234
```

This is optional - logging works without it.

### Configuration

Environment variables:
- MCP_LOG_LEVEL: info (default) | debug | error
- LOG_LEVEL: Alternative name (for consistency with Docker conventions)

## Consequences

### Benefits
- Automatic audit trail for all MADs
- No auth required in individual applications
- Centralized implementation (one code change benefits all)
- Performance metrics (duration_ms)
- Troubleshooting visibility
- Container-native logging (stdout/stderr)
- No file permissions complexity

### Trade-offs
- Log persistence depends on Docker daemon configuration

## Migration

Existing MADs (Brin, Malory, Henson, CLI wrappers) automatically gain logging when mad-core is updated. Container rebuild required to pick up new library version.

## References

- ADR-042: Shared MAD Core Library
- ADR-045: MAD Template Standard
- 12-Factor App Methodology: Logs as streams
