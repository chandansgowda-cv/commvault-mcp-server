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

async def test_get_sla_status(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_sla_status", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_sla_status")
        
        # Verify expected structure for SLA status
        if isinstance(data, dict):
            # SLA data should contain percentage or status info
            assert len(data) > 0, "SLA status response should not be empty"
        elif isinstance(data, str):
            # If it's a non-error string, that might be acceptable
            pass
        else:
            assert isinstance(data, (list, dict)), f"Expected dict, list, or string response, got {type(data)}"

async def test_get_security_posture(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_security_posture", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_security_posture")
        
        # Verify expected structure
        if isinstance(data, dict):
            assert len(data) > 0, "Security posture response should not be empty"
        elif isinstance(data, str):
            # If it's a non-error string, that might be acceptable
            pass
        else:
            assert isinstance(data, (list, dict)), f"Expected dict, list, or string response, got {type(data)}"

async def test_get_security_score(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_security_score", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_security_score")
        
        # Verify expected structure
        if isinstance(data, dict):
            # Should contain security score
            if "security_score" in data:
                assert isinstance(data["security_score"], (int, float)), "Security score should be numeric"
                assert 0 <= data["security_score"] <= 100, "Security score should be between 0 and 100"
            else:
                assert len(data) > 0, "Security score response should not be empty"
        elif isinstance(data, str):
            # If it's a non-error string, that might be acceptable
            pass
        else:
            assert isinstance(data, (list, dict)), f"Expected dict, list, or string response, got {type(data)}"

async def test_get_storage_space_utilization(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_storage_space_utilization", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_storage_space_utilization")
        
        # Verify expected structure
        if isinstance(data, dict):
            # Should contain records or utilization data
            if "records" in data:
                assert isinstance(data["records"], list), "Records should be a list"
            else:
                assert len(data) > 0, "Storage utilization response should not be empty"
        elif isinstance(data, str):
            # If it's a non-error string, that might be acceptable
            pass
        else:
            assert isinstance(data, (list, dict)), f"Expected dict, list, or string response, got {type(data)}"

async def test_get_commcell_details(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_commcell_details", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_commcell_details")
        
        # Verify expected structure
        if isinstance(data, dict):
            # Should contain records or commcell details
            if "records" in data:
                assert isinstance(data["records"], list), "Records should be a list"
            else:
                assert len(data) > 0, "CommCell details response should not be empty"
        elif isinstance(data, str):
            # If it's a non-error string, that might be acceptable
            pass
        else:
            assert isinstance(data, (list, dict)), f"Expected dict, list, or string response, got {type(data)}"

# async def test_get_entity_counts(mcp_server):
#     async with Client(mcp_server) as client:
#         result = await client.call_tool("get_entity_counts", {})
#         if isinstance(result, list) and hasattr(result[0], "text"):
#             data = json.loads(result[0].text)
#             assert not is_real_error(data)
#         else:
#             assert isinstance(result, dict)

async def test_create_send_logs_job_for_commcell(mcp_server):
    async with Client(mcp_server) as client:
        # First get CommCell details to extract a valid CommCell name
        commcell_details = await client.call_tool("get_commcell_details", {})
        
        # API failure should fail the test
        commcell_data = extract_response_data(commcell_details)
        assert_no_error_in_response(commcell_data, "get_commcell_details")
        
        commcell_name = None
        try:
            if isinstance(commcell_data, dict):
                if "records" in commcell_data and commcell_data["records"]:
                    for record in commcell_data["records"]:
                        if "commCellName" in record:
                            commcell_name = record["commCellName"]
                            break
                elif "commCellName" in commcell_data:
                    commcell_name = commcell_data["commCellName"]
            elif isinstance(commcell_data, list) and commcell_data:
                if "commCellName" in commcell_data[0]:
                    commcell_name = commcell_data[0]["commCellName"]
        except Exception as e:
            # If we can't extract CommCell name, try getting client list
            pass
        
        # If we can't get CommCell name from details, try getting client list and use first client name
        if not commcell_name:
            try:
                clients = await client.call_tool("get_client_list", {})
                clients_data = extract_response_data(clients)
                assert_no_error_in_response(clients_data, "get_client_list")
                
                if isinstance(clients_data, dict):
                    if "clients" in clients_data and clients_data["clients"]:
                        commcell_name = clients_data["clients"][0].get("clientName")
                elif isinstance(clients_data, list) and clients_data:
                    commcell_name = clients_data[0].get("clientName")
            except Exception:
                pass
        
        # Only run test if we found a valid CommCell name, otherwise skip
        if commcell_name:
            result = await client.call_tool(
                "create_send_logs_job_for_commcell",
                {"emailid": "test@example.com", "commcell_name": commcell_name}
            )
            data = extract_response_data(result)
            assert_no_error_in_response(data, "create_send_logs_job_for_commcell")
            
            # Verify task creation response
            if isinstance(data, dict):
                assert len(data) > 0, "Send logs job response should not be empty"
            elif isinstance(data, str):
                # String response without errors is acceptable
                pass
        else:
            # Skip test if no CommCell name found
            pytest.skip("No CommCell name found to test with")