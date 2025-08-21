# MCP Server Test Suite

Test suite for the CommVault MCP (Model Context Protocol) server tools.

## Prerequisites

- Python 3.8+
- `uv` package manager
- Configured CommVault credentials in system keyring
- Active CommVault environment

## Test Files

- `test_client_tools.py` - Client and subclient operations
- `test_commcell_tools.py` - CommCell operations and monitoring
- `test_job_tools.py` - Job management and monitoring
- `test_plan_tools.py` - Plan configuration
- `test_schedule_tools.py` - Schedule management
- `test_storage_tools.py` - Storage policies and infrastructure
- `test_user_tools.py` - User and permission management
- `test_tool_combos_1.py` - Tool combination tests (Part 1)
- `test_tool_combos_2.py` - Tool combination tests (Part 2)
- `conftest.py` - Test configuration

## Running Tests

### All Tests
```bash
uv run pytest tests
```

### Individual Test Files
```bash
uv run pytest .\tests\test_client_tools.py
uv run pytest .\tests\test_job_tools.py
uv run pytest .\tests\test_storage_tools.py
```

### Specific Test Function
```bash
uv run pytest .\tests\test_client_tools.py::test_get_client_list
```

### With Options
```bash
# Verbose output
uv run pytest tests -v

# Show print statements
uv run pytest tests -s

# Stop on first failure
uv run pytest tests -x
```

## Test Output

Tests display results in the terminal:

```
=================== test session starts ===================
tests/test_client_tools.py ........                   [ 17%]
tests/test_job_tools.py ..........                    [ 53%]
tests/test_user_tools.py ........                     [ 91%]

=================== 45 passed, 2 skipped in 120s =================
```

**Symbols:**
- `.` = Passed
- `F` = Failed
- `s` = Skipped
- `E` = Error

## Authentication

Tests require CommVault credentials stored in system keyring:
```python
service_name = "commvault-mcp-server"
# Required: access_token, refresh_token, server_secret
```

## Notes

- Tests automatically discover valid IDs from your environment
- Tests skip gracefully when required data isn't available
- Some tests require active jobs, clients, or recent system activity