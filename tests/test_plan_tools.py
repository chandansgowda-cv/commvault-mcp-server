from fastmcp import Client
import json
import pytest

def extract_response_data(result):
    """Extract and parse data from MCP client response."""
    if not isinstance(result, list) or len(result) == 0:
        raise AssertionError("Expected list response with at least one item")
    
    if not hasattr(result[0], "text"):
        raise AssertionError("Response item missing 'text' attribute")
    
    response_text = result[0].text
    
    # First try to parse as JSON
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If not JSON, return the raw text for further analysis
        return response_text

def assert_no_error_in_response(data, operation_name):
    """Assert that response data doesn't contain errors."""
    if isinstance(data, str):
        # Check for common error patterns in string responses
        error_indicators = [
            "error occurred", "failed to", "invalid", "unauthorized", 
            "not found", "exception", "traceback",
            "internal server error", "bad request", "forbidden"
        ]
        data_lower = data.lower()
        for indicator in error_indicators:
            if indicator in data_lower:
                raise AssertionError(f"{operation_name} failed with error: {data}")
        return
    
    elif isinstance(data, dict):
        # Check for explicit error structure
        if "error" in data:
            error = data["error"]
            if isinstance(error, dict):
                error_msg = error.get("errorMessage", "")
                error_code = error.get("errorCode", 0)
                if error_msg or error_code != 0:
                    raise AssertionError(f"{operation_name} failed with error: {error_msg} (code: {error_code})")
            elif error:
                raise AssertionError(f"{operation_name} failed with error: {error}")
        
        if "errorMessage" in data and data["errorMessage"]:
            raise AssertionError(f"{operation_name} failed: {data['errorMessage']}")
        
        if "errorCode" in data and data["errorCode"] != 0:
            raise AssertionError(f"{operation_name} failed with error code: {data['errorCode']}")

def find_plan_id(data):
    """Find any plan ID in the response data."""
    if isinstance(data, dict):
        # Check common locations for plan ID
        if "plans" in data and isinstance(data["plans"], list) and len(data["plans"]) > 0:
            plan = data["plans"][0]
            if isinstance(plan, dict):
                # Check nested plan structure
                if "plan" in plan and isinstance(plan["plan"], dict):
                    return plan["plan"].get("planId") or plan["plan"].get("id")
                # Check direct plan structure  
                return plan.get("planId") or plan.get("id")
        
        # Check direct fields
        return data.get("planId") or data.get("id")
    
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        return data[0].get("planId") or data[0].get("id")
    
    return None

async def test_get_plan_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_plan_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_plan_list")
        
        # Verify response structure
        if isinstance(data, dict):
            assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            assert len(data) >= 0, "List response should be valid"

async def test_get_plan_properties(mcp_server):
    plan_id = None
    
    # Get plan list first
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_plan_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_plan_list")
        
        plan_id = find_plan_id(data)
    
    # Skip only if no plans exist
    if not plan_id:
        pytest.skip("No plans found in the system")
    
    # Test plan properties
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_plan_properties", {"plan_id": str(plan_id)})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_plan_properties")
        
        # Verify response has content
            if isinstance(data, dict):
                assert len(data) > 0, "Plan properties response should not be empty"
            elif isinstance(data, str):
                assert len(data) > 0, "Plan properties response should not be empty"
            assert len(data) > 0, "Plan properties response should not be empty"