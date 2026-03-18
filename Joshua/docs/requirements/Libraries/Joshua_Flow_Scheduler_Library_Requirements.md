# joshua_flow_scheduler Library Requirements

**Status**: Stub - Requires detailed specification
**Layer**: Action Engine
**Version**: 0.7.0

---

## 1. Overview

`joshua_flow_scheduler` is the Action Engine library responsible for triggering scheduled and periodic flows within MADs. Per **ADR-032**, it enables proactive flows that run on schedules, not just reactively in response to external events.

**Purpose**: Provide infrastructure for:
- Cron-like scheduled flow execution
- Periodic flow triggers (every N seconds/minutes/hours)
- One-time delayed flow execution
- Flow scheduling based on system events

---

## 2. Core Functionality

### 2.1. Schedule Types

#### Cron-Style Schedules
- Standard cron expressions (minute, hour, day, month, weekday)
- Example: `"0 2 * * *"` - Daily at 2 AM

#### Interval Schedules
- Fixed intervals (seconds, minutes, hours)
- Example: `interval="5m"` - Every 5 minutes

#### One-Time Delayed
- Execute flow once after delay
- Example: `delay="30s"` - 30 seconds from now

#### Event-Based Triggers
- Trigger on system events (e.g., "on_startup", "on_shutdown")

### 2.2. Public API

```python
from joshua_flow_scheduler import FlowScheduler

scheduler = FlowScheduler(flow_runner=flow_runner)

# Cron-style schedule
scheduler.schedule_cron(
    flow_name="periodic_review_flow.json",
    cron_expression="0 */6 * * *",  # Every 6 hours
    flow_inputs={"review_type": "comprehensive"}
)

# Interval schedule
scheduler.schedule_interval(
    flow_name="metric_collection_flow.json",
    interval="5m",  # Every 5 minutes
    flow_inputs={}
)

# One-time delayed
scheduler.schedule_once(
    flow_name="startup_validation_flow.json",
    delay="30s",  # 30 seconds after startup
    flow_inputs={}
)

# Event-based
scheduler.on_event(
    event="on_startup",
    flow_name="initialization_flow.json"
)

# Start scheduler (runs in background)
await scheduler.start()

# Graceful shutdown
await scheduler.stop()
```

---

## 3. Configuration

### 3.1. MAD-Level Configuration

```yaml
# config/flow_config.yaml
scheduler:
  enabled: true
  timezone: "UTC"
  max_concurrent_scheduled_flows: 5

scheduled_flows:
  - name: "periodic_review_flow.json"
    schedule: "0 */6 * * *"  # Cron expression
    inputs:
      review_type: "comprehensive"

  - name: "metric_collection_flow.json"
    schedule: "interval:5m"  # Interval
    inputs: {}

  - name: "learning_update_flow.json"
    schedule: "0 3 * * 0"  # Weekly at 3 AM Sunday
    inputs:
      update_type: "weekly_consolidation"
```

### 3.2. Runtime Controls

- Pause/resume schedules
- Disable specific scheduled flows
- Manual trigger of scheduled flows
- Schedule modification without restart

---

## 4. Integration with Flow Runner

The scheduler delegates flow execution to `Joshua_Flow_Runner`:

```python
# When schedule fires
await flow_runner.execute(
    flow_name="periodic_review_flow.json",
    input_data={"review_type": "comprehensive"},
    execution_context={"triggered_by": "scheduler", "schedule": "0 */6 * * *"}
)
```

---

## 5. Persistence and Recovery

### 5.1. Schedule State Persistence
- Store schedule definitions in configuration
- Track last execution times
- Persist pending one-time schedules across restarts

### 5.2. Startup Behavior
- Resume all active schedules
- Skip missed executions (no catch-up by default)
- Optional catch-up mode for critical flows

---

## 6. Error Handling

### 6.1. Flow Execution Failures
- Log error with schedule context
- Continue with next scheduled execution
- Optional: Disable schedule after N consecutive failures

### 6.2. Scheduler Failures
- Graceful degradation if scheduling backend fails
- Fallback to simplified in-memory scheduler
- Alert/log scheduler health issues

---

## 7. Observability

### 7.1. Metrics
- Scheduled flow execution count
- Scheduled flow success/failure rates
- Schedule drift (actual vs. intended execution time)
- Scheduler health status

### 7.2. Logging
- Schedule registration/modification events
- Flow execution start/completion (with schedule context)
- Missed executions (if any)

---

## 8. Dependencies

### External Packages
- `croniter` - Cron expression parsing
- `asyncio` - Async task scheduling
- `apscheduler` (optional) - Advanced scheduling backend

### Internal Dependencies
- `Joshua_Flow_Runner` - Flow execution
- `joshua_communicator` - Logging infrastructure

---

## 9. Testing Requirements

### Unit Tests
- Cron expression parsing
- Interval calculation
- Schedule registration/modification
- Execution time calculation

### Integration Tests
- Scheduled flow execution with FlowRunner
- Schedule persistence across restarts
- Error handling and recovery
- Concurrent scheduled flow execution

---

## 10. Performance Characteristics

- **Schedule evaluation overhead**: < 1ms per schedule per tick
- **Max concurrent scheduled flows**: Configurable, default 5
- **Schedule granularity**: 1 second minimum

---

## 11. Implementation Status

**Current Status**: Specification only - implementation required

**Priority**: HIGH - Required for proactive MAD behavior

**Next Steps**:
1. Choose scheduling backend (apscheduler vs. custom)
2. Implement core FlowScheduler class
3. Implement cron and interval schedule types
4. Integrate with FlowRunner
5. Configuration loading and validation
6. Persistence layer for schedule state
7. Comprehensive test suite

---

## 12. Related Documentation

- **ADR-032**: Fully Flow-Based Architecture - Defines reactive vs. proactive flows
- **Joshua_Flow_Runner**: Flow execution engine
- **MAD Requirements**: Examples of scheduled flows per MAD

---

**Last Updated:** 2025-12-21
**Status:** Requires implementation and detailed API specification
