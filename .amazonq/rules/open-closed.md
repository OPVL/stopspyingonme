# Open/Closed Principle Rules

## Provider Adapters (O/C)
- Abstract inbound mail providers (Cloudflare primary)
- Abstract outbound SMTP relay patterns
- Pluggable spam scoring frameworks
- Configurable webhook delivery systems

## Extension Points (O/C)
- Redis-ready session storage
- Queue migration path from cron jobs
- Multiple authentication methods support
- Bandwidth enforcement policy variants

## Configuration Driven (O/C)
- Environment-based feature flags
- Pydantic config with validation
- Provider selection via config
- Threshold and limit customization
