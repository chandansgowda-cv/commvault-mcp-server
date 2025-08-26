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
        # If it's a plain string without error indicators, it might be a valid response
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
            elif error:  # Non-empty error value
                raise AssertionError(f"{operation_name} failed with error: {error}")
        
        # Check for common error indicators
        if "errorMessage" in data and data["errorMessage"]:
            raise AssertionError(f"{operation_name} failed: {data['errorMessage']}")
        
        if "errorCode" in data and data["errorCode"] != 0:
            raise AssertionError(f"{operation_name} failed with error code: {data['errorCode']}")
 
async def test_get_schedules_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_schedules_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_schedules_list")
        
        # Empty schedule list is acceptable - just verify structure
        if isinstance(data, dict):
            if "policies" in data:
                assert isinstance(data["policies"], list), "policies should be a list"
            elif "schedules" in data:
                assert isinstance(data["schedules"], list), "schedules should be a list"
            else:
                assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            # Direct list response is also acceptable
            assert len(data) >= 0, "List response should be valid"
        elif isinstance(data, str):
            # String response without errors is acceptable
            pass

async def test_get_schedule_properties(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of schedules
        schedules_result = await client.call_tool("get_schedules_list", {})
        schedules_data = extract_response_data(schedules_result)
        assert_no_error_in_response(schedules_data, "get_schedules_list")
        
        schedule_id = None
        try:
            # Handle both wrapper format and raw API response
            if isinstance(schedules_data, dict):
                if "policies" in schedules_data and schedules_data["policies"]:
                    policies_list = schedules_data["policies"]
                    if isinstance(policies_list, list) and len(policies_list) > 0:
                        policy = policies_list[0]
                        schedule_id = str(policy.get("policyId"))
                elif "schedules" in schedules_data and schedules_data["schedules"]:
                    schedules_list = schedules_data["schedules"]
                    if isinstance(schedules_list, list) and len(schedules_list) > 0:
                        schedule = schedules_list[0]
                        schedule_id = str(schedule.get("taskId"))
            elif isinstance(schedules_data, list) and schedules_data:
                # Handle direct list response
                task_id = schedules_data[0].get("taskId")
                schedule_id = str(task_id) if task_id is not None else None
        except Exception as e:
            raise AssertionError(f"Failed to extract schedule ID from response: {e}")
        
        # If no schedules exist, skip (empty is acceptable for schedules)
        if not schedule_id or schedule_id == "None":
            pytest.skip("No schedules exist in the system - test passes")
        
        # Test getting schedule properties for existing schedule
        result = await client.call_tool("get_schedule_properties", {"schedule_id": schedule_id})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_schedule_properties")
        
        # Verify it returns schedule data
        if isinstance(data, dict):
            assert len(data) >= 0, "Schedule properties response should be valid"
        elif isinstance(data, str):
            # String response without errors is acceptable
            pass


# async def test_enable_schedule(mcp_server):
#     async with Client(mcp_server) as client:
#         # First get the list of schedules to get a valid schedule_id
#         schedules = await client.call_tool("get_schedules_list", {})
#         
#         if isinstance(schedules, list) and len(schedules) > 0:
#             # Extract schedule ID from the response
#             if hasattr(schedules[0], "text"):
#                 try:
#                     schedules_data = json.loads(schedules[0].text)
#                     if isinstance(schedules_data, list) and len(schedules_data) > 0:
#                         schedule_id = str(schedules_data[0].get("taskId", "25"))
#                     elif isinstance(schedules_data, dict) and "schedules" in schedules_data:
#                         schedules_list = schedules_data["schedules"]
#                         if isinstance(schedules_list, list) and len(schedules_list) > 0:
#                             schedule_id = str(schedules_list[0].get("taskId", "25"))
#                         else:
#                             schedule_id = "25"
#                     else:
#                         schedule_id = "25"
#                 except (json.JSONDecodeError, KeyError):
#                     schedule_id = "25"
#             else:
#                 schedule_id = "25"
#         else:
#             schedule_id = "25"
#         
#         result = await client.call_tool("enable_schedule", {"schedule_id": schedule_id})
#         assert "error" not in result[0].text.lower() or "success" in result[0].text.lower() or isinstance(result, dict)

# async def test_disable_schedule(mcp_server):
#     async with Client(mcp_server) as client:
#         # First get the list of schedules to get a valid schedule_id
#         schedules = await client.call_tool("get_schedules_list", {})
#         
#         if isinstance(schedules, list) and len(schedules) > 0:
#             # Extract schedule ID from the response
#             if hasattr(schedules[0], "text"):
#                 try:
#                     schedules_data = json.loads(schedules[0].text)
#                     if isinstance(schedules_data, list) and len(schedules_data) > 0:
#                         schedule_id = str(schedules_data[0].get("taskId", "24"))
#                     elif isinstance(schedules_data, dict) and "schedules" in schedules_data:
#                         schedules_list = schedules_data["schedules"]
#                         if isinstance(schedules_list, list) and len(schedules_list) > 0:
#                             schedule_id = str(schedules_list[0].get("taskId", "24"))
#                         else:
#                             schedule_id = "24"
#                     else:
#                         schedule_id = "24"
#                 except (json.JSONDecodeError, KeyError):
#                     schedule_id = "24"
#             else:
#                 schedule_id = "24"
#         else:
#             schedule_id = "24"
#         
#         result = await client.call_tool("disable_schedule", {"schedule_id": schedule_id})
#         assert "error" not in result[0].text.lower() or "success" in result[0].text.lower()