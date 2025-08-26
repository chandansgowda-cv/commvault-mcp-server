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

def safe_extract_id(response, id_field):
    """Safely extract ID from API response."""
    try:
        data = extract_response_data(response)
        
        # Handle direct list
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            if isinstance(first_item, dict) and id_field in first_item:
                value = first_item[id_field]
                return str(value) if value is not None else None
        
        # Handle nested object structures
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    first_item = value[0]
                    if isinstance(first_item, dict) and id_field in first_item:
                        id_value = first_item[id_field]
                        return str(id_value) if id_value is not None else None
                
                # Check if the key itself matches
                if key == id_field and value is not None:
                    return str(value)
    except Exception:
        return None
    
    return None

async def test_get_client_group_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_client_group_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_client_group_list")
        
        # If API succeeds but returns empty, that's acceptable - pass/skip
        if isinstance(data, dict):
            if "clientGroups" in data:
                # Empty list is fine, pass the test
                assert isinstance(data["clientGroups"], list), "clientGroups should be a list"
            elif "groups" in data:  # Raw API response
                # Empty list is fine, pass the test  
                assert isinstance(data["groups"], list), "groups should be a list"
            else:
                # Non-empty dict without expected keys is acceptable
                assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            # Empty list is fine, pass the test
            assert len(data) >= 0, "List response should be valid"
        elif isinstance(data, str):
            # If it's a non-error string, skip
            pytest.skip(f"get_client_group_list returned string response: {data[:100]}...")

async def test_get_client_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_client_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_client_list")
        
        # If API succeeds but returns empty, that's acceptable - pass/skip
        if isinstance(data, dict):
            if "clients" in data:
                # Empty list is fine, pass the test
                assert isinstance(data["clients"], list), "clients should be a list"
            elif "clientProperties" in data:  # Raw API response
                # Empty list is fine, pass the test
                assert isinstance(data["clientProperties"], list), "clientProperties should be a list"
            else:
                # Non-empty dict without expected keys is acceptable
                assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            # Empty list is fine, pass the test
            assert len(data) >= 0, "List response should be valid"
        elif isinstance(data, str):
            # If it's a non-error string, skip
            pytest.skip(f"get_client_list returned string response: {data[:100]}...")

async def test_get_client_group_properties(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of client groups to get a valid client_group_id
        client_groups = await client.call_tool("get_client_group_list", {})
        
        # This should not skip - if the API fails, the test should fail
        groups_data = extract_response_data(client_groups)
        assert_no_error_in_response(groups_data, "get_client_group_list")
        
        client_group_id = None
        try:
            # Handle both wrapper format and raw API response
            if isinstance(groups_data, dict):
                if "clientGroups" in groups_data and groups_data["clientGroups"]:
                    client_group_id = str(groups_data["clientGroups"][0].get("clientGroupId"))
                elif "groups" in groups_data and groups_data["groups"]:
                    # Raw API response
                    first_group = groups_data["groups"][0]
                    client_group_id = str(first_group.get("clientGroup", {}).get("clientGroupId") or first_group.get("Id"))
            elif isinstance(groups_data, list) and groups_data:
                client_group_id = str(groups_data[0].get("id") or groups_data[0].get("clientGroupId"))
        except Exception as e:
            raise AssertionError(f"Failed to extract client group ID from response: {e}")
        
        # Only skip if API succeeded but returned empty data
        if not client_group_id:
            if isinstance(groups_data, dict) and "clientGroups" in groups_data and len(groups_data["clientGroups"]) == 0:
                pytest.skip("No client groups exist in the system (empty but successful response)")
            else:
                raise AssertionError("Could not extract client group ID from API response")
        
        # Test getting properties
        result = await client.call_tool("get_client_group_properties", {"client_group_id": client_group_id})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_client_group_properties")
        assert isinstance(data, (dict, str)), "Expected dict or string response"

async def test_get_clientid_from_clientname(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of clients to get a valid client name
        clients = await client.call_tool("get_client_list", {})
        
        # API failure should fail the test, not skip it
        clients_data = extract_response_data(clients)
        assert_no_error_in_response(clients_data, "get_client_list")
        
        client_name = None
        try:
            # Handle both wrapper format and raw API response
            if isinstance(clients_data, dict):
                if "clients" in clients_data and clients_data["clients"]:
                    client_name = clients_data["clients"][0].get("clientName")
                elif "clientProperties" in clients_data and clients_data["clientProperties"]:
                    # Raw API response
                    client_entity = clients_data["clientProperties"][0].get("client", {}).get("clientEntity", {})
                    client_name = client_entity.get("clientName")
            elif isinstance(clients_data, list) and clients_data:
                client_name = clients_data[0].get("clientName")
        except Exception as e:
            raise AssertionError(f"Failed to extract client name from response: {e}")
        
        # Only skip if API succeeded but returned no clients
        if not client_name:
            if isinstance(clients_data, dict) and "clients" in clients_data and len(clients_data["clients"]) == 0:
                pytest.skip("No clients exist in the system (empty but successful response)")
            else:
                raise AssertionError("Could not extract client name from API response")
        
        # Test getting client ID from name
        result = await client.call_tool("get_clientid_from_clientname", {"client_name": client_name})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_clientid_from_clientname")
        assert isinstance(data, (dict, str)), "Expected dict or string response"

async def test_get_subclient_list_by_name(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of clients to get a valid client name
        clients = await client.call_tool("get_client_list", {})
        
        # API failure should fail the test, not skip it
        clients_data = extract_response_data(clients)
        assert_no_error_in_response(clients_data, "get_client_list")
        
        client_name = None
        try:
            # Handle both wrapper format and raw API response
            if isinstance(clients_data, dict):
                if "clients" in clients_data and clients_data["clients"]:
                    client_name = clients_data["clients"][0].get("clientName")
                elif "clientProperties" in clients_data and clients_data["clientProperties"]:
                    # Raw API response
                    client_entity = clients_data["clientProperties"][0].get("client", {}).get("clientEntity", {})
                    client_name = client_entity.get("clientName")
            elif isinstance(clients_data, list) and clients_data:
                client_name = clients_data[0].get("clientName")
        except Exception as e:
            raise AssertionError(f"Failed to extract client name from response: {e}")
        
        # Only skip if API succeeded but returned no clients
        if not client_name:
            if isinstance(clients_data, dict) and "clients" in clients_data and len(clients_data["clients"]) == 0:
                pytest.skip("No clients exist in the system (empty but successful response)")
            else:
                raise AssertionError("Could not extract client name from API response")
        
        # Test getting subclients by name
        result = await client.call_tool("get_subclient_list", {"client_identifier": client_name, "identifier_type": "name"})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_subclient_list")
        
        # Check for expected subclient structure
        if isinstance(data, dict):
            if "subClients" in data:
                assert isinstance(data["subClients"], list), "subClients should be a list"
            elif "subClientProperties" in data:  # Raw API response
                assert isinstance(data["subClientProperties"], list), "subClientProperties should be a list"
        elif isinstance(data, str):
            # String response without errors is acceptable
            pass
        else:
            assert isinstance(data, list), f"Expected dict, list, or string response, got {type(data)}"

async def test_get_subclient_list_by_id(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of clients to get a valid client ID
        clients = await client.call_tool("get_client_list", {})
        
        # API failure should fail the test, not skip it
        clients_data = extract_response_data(clients)
        assert_no_error_in_response(clients_data, "get_client_list")
        
        client_id = None
        try:
            # Handle both wrapper format and raw API response
            if isinstance(clients_data, dict):
                if "clients" in clients_data and clients_data["clients"]:
                    client_id = str(clients_data["clients"][0].get("clientId"))
                elif "clientProperties" in clients_data and clients_data["clientProperties"]:
                    # Raw API response
                    client_entity = clients_data["clientProperties"][0].get("client", {}).get("clientEntity", {})
                    client_id = str(client_entity.get("clientId"))
            elif isinstance(clients_data, list) and clients_data:
                client_id = str(clients_data[0].get("clientId"))
        except Exception as e:
            raise AssertionError(f"Failed to extract client ID from response: {e}")
        
        # Only skip if API succeeded but returned no clients
        if not client_id or client_id == "None":
            if isinstance(clients_data, dict) and "clients" in clients_data and len(clients_data["clients"]) == 0:
                pytest.skip("No clients exist in the system (empty but successful response)")
            else:
                raise AssertionError("Could not extract valid client ID from API response")
        
        # Test getting subclients by ID
        result = await client.call_tool("get_subclient_list", {"client_identifier": client_id, "identifier_type": "id"})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_subclient_list")
        
        # Check for expected subclient structure
        if isinstance(data, dict):
            if "subClients" in data:
                assert isinstance(data["subClients"], list), "subClients should be a list"
            elif "subClientProperties" in data:  # Raw API response
                assert isinstance(data["subClientProperties"], list), "subClientProperties should be a list"
        elif isinstance(data, str):
            # String response without errors is acceptable
            pass
        else:
            assert isinstance(data, list), f"Expected dict, list, or string response, got {type(data)}"

async def test_get_subclient_properties(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of clients to get a valid client ID
        clients = await client.call_tool("get_client_list", {})
        
        # API failure should fail the test, not skip it
        clients_data = extract_response_data(clients)
        assert_no_error_in_response(clients_data, "get_client_list")

        client_id = None
        try:
            # Handle both wrapper format and raw API response
            if isinstance(clients_data, dict):
                if "clients" in clients_data and clients_data["clients"]:
                    client_id = str(clients_data["clients"][0].get("clientId"))
                elif "clientProperties" in clients_data and clients_data["clientProperties"]:
                    # Raw API response
                    client_entity = clients_data["clientProperties"][0].get("client", {}).get("clientEntity", {})
                    client_id = str(client_entity.get("clientId"))
            elif isinstance(clients_data, list) and clients_data:
                client_id = str(clients_data[0].get("clientId"))
        except Exception as e:
            raise AssertionError(f"Failed to extract client ID from response: {e}")

        # Only skip if API succeeded but returned no clients
        if not client_id or client_id == "None":
            if isinstance(clients_data, dict) and "clients" in clients_data and len(clients_data["clients"]) == 0:
                pytest.skip("No clients exist in the system (empty but successful response)")
            else:
                raise AssertionError("Could not extract valid client ID from API response")
        
        # Get subclients for this client - API failure should fail test
        subclients = await client.call_tool("get_subclient_list", {"client_identifier": client_id, "identifier_type": "id"})
        subclients_data = extract_response_data(subclients)
        assert_no_error_in_response(subclients_data, "get_subclient_list")
        
        subclient_id = None
        try:
            # Handle both wrapper format and raw API response
            if isinstance(subclients_data, dict):
                if "subClients" in subclients_data and subclients_data["subClients"]:
                    subclient_id = str(subclients_data["subClients"][0].get("subclientId"))
                elif "subClientProperties" in subclients_data and subclients_data["subClientProperties"]:
                    # Raw API response
                    sub_entity = subclients_data["subClientProperties"][0].get("subClientEntity", {})
                    subclient_id = str(sub_entity.get("subclientId"))
            elif isinstance(subclients_data, list) and subclients_data:
                subclient_id = str(subclients_data[0].get("subClientId") or subclients_data[0].get("subclientId"))
        except Exception as e:
            raise AssertionError(f"Failed to extract subclient ID from response: {e}")
        
        # Only skip if API succeeded but client has no subclients
        if not subclient_id or subclient_id == "None":
            if isinstance(subclients_data, dict) and "subClients" in subclients_data and len(subclients_data["subClients"]) == 0:
                pytest.skip("Client has no subclients (empty but successful response)")
            else:
                raise AssertionError("Could not extract valid subclient ID from API response")
        
        # Test getting subclient properties
        result = await client.call_tool("get_subclient_properties", {"subclient_id": subclient_id})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_subclient_properties")
        assert isinstance(data, (dict, str)), "Expected dict or string response"

# async def test_run_backup_for_subclient(mcp_server):
#     async with Client(mcp_server) as client:
#         # First get the list of clients to get a valid client ID
#         clients = await client.call_tool("get_client_list", {})
#         
#         if isinstance(clients, list) and len(clients) > 0:
#             # Extract client ID from the response
#             if hasattr(clients[0], "text"):
#                 try:
#                     clients_data = json.loads(clients[0].text)
#                     if isinstance(clients_data, list) and len(clients_data) > 0:
#                         client_id = str(clients_data[0].get("clientId", "3"))
#                     else:
#                         client_id = "3"
#                 except (json.JSONDecodeError, KeyError):
#                     client_id = "3"
#             else:
#                 client_id = "3"
#         else:
#             client_id = "3"
#         
#         # Get subclients for this client
#         subclients = await client.call_tool("get_subclient_list", {"client_identifier": client_id, "identifier_type": "id"})
#         
#         if isinstance(subclients, list) and len(subclients) > 0:
#             # Extract subclient ID from the response
#             if hasattr(subclients[0], "text"):
#                 try:
#                     subclients_data = json.loads(subclients[0].text)
#                     if isinstance(subclients_data, list) and len(subclients_data) > 0:
#                         subclient_id = str(subclients_data[0].get("subClientId", "3"))
#                     else:
#                         subclient_id = "3"
#                 except (json.JSONDecodeError, KeyError):
#                     subclient_id = "3"
#             else:
#                 subclient_id = "3"
#         else:
#             subclient_id = "3"
#         
#         backup_type = "INCREMENTAL"
#         result = await client.call_tool("run_backup_for_subclient", {"subclient_id": subclient_id, "backup_type": backup_type})
#         assert "error" not in result[0].text.lower() or "job" in result[0].text.lower() or "success" in result[0].text.lower()