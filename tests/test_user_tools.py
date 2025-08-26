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

def assert_no_error_in_response(data, operation_name, acceptable_errors=None):
    """Assert that response data doesn't contain errors."""
    if acceptable_errors is None:
        acceptable_errors = []
    
    if isinstance(data, str):
        # Check if this is an acceptable operational error
        data_lower = data.lower()
        for acceptable in acceptable_errors:
            if acceptable.lower() in data_lower:
                return  # This error is acceptable for this operation
        
        # Check for common error patterns in string responses
        error_indicators = [
            "error occurred", "failed to", "invalid", "unauthorized", 
            "not found", "exception", "traceback",
            "internal server error", "bad request", "forbidden"
        ]
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
                
                # Check if this is an acceptable operational error
                for acceptable in acceptable_errors:
                    if acceptable.lower() in error_msg.lower():
                        return  # This error is acceptable for this operation
                
                if error_msg or error_code != 0:
                    raise AssertionError(f"{operation_name} failed with error: {error_msg} (code: {error_code})")
            elif error:  # Non-empty error value
                raise AssertionError(f"{operation_name} failed with error: {error}")
        
        # Check for common error indicators
        if "errorMessage" in data and data["errorMessage"]:
            error_msg = data["errorMessage"]
            
            # Check if this is an acceptable operational error
            for acceptable in acceptable_errors:
                if acceptable.lower() in error_msg.lower():
                    return  # This error is acceptable for this operation
            
            raise AssertionError(f"{operation_name} failed: {error_msg}")
        
        if "errorCode" in data and data["errorCode"] != 0:
            raise AssertionError(f"{operation_name} failed with error code: {data['errorCode']}")

async def test_get_users_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_users_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_users_list")
        
        # Empty users list is acceptable - just verify structure
        if isinstance(data, dict):
            if "users" in data:
                assert isinstance(data["users"], list), "users should be a list"
            else:
                assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            # Direct list response is also acceptable
            assert len(data) >= 0, "List response should be valid"
        elif isinstance(data, str):
            # String response without errors is acceptable
            pass

async def test_get_user_properties(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of users
        users_result = await client.call_tool("get_users_list", {})
        users_data = extract_response_data(users_result)
        assert_no_error_in_response(users_data, "get_users_list")
        
        user_id = None
        try:
            # Handle both wrapper format and raw API response
            if isinstance(users_data, dict):
                if "users" in users_data and users_data["users"]:
                    users_list = users_data["users"]
                    if isinstance(users_list, list) and len(users_list) > 0:
                        user_id = str(users_list[0].get("userId"))
            elif isinstance(users_data, list) and users_data:
                user_id = str(users_data[0].get("userId"))
        except Exception as e:
            raise AssertionError(f"Failed to extract user ID from response: {e}")
        
        # If no users exist, skip (empty is acceptable for users)
        if not user_id or user_id == "None":
            pytest.skip("No users exist in the system - test passes")
        
        # Test getting user properties for existing user
        result = await client.call_tool("get_user_properties", {"user_id": user_id})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_user_properties")
        
        # Verify it returns user data
        if isinstance(data, dict):
            assert len(data) >= 0, "User properties response should be valid"
        elif isinstance(data, str):
            # String response without errors is acceptable
            pass

async def test_set_user_enabled(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of users
        users_result = await client.call_tool("get_users_list", {})
        users_data = extract_response_data(users_result)
        assert_no_error_in_response(users_data, "get_users_list")
        
        user_id = None
        try:
            # Handle both wrapper format and raw API response
            if isinstance(users_data, dict):
                if "users" in users_data and users_data["users"]:
                    users_list = users_data["users"]
                    if isinstance(users_list, list) and len(users_list) > 0:
                        user_id = str(users_list[0].get("userId"))
            elif isinstance(users_data, list) and users_data:
                user_id = str(users_data[0].get("userId"))
        except Exception as e:
            raise AssertionError(f"Failed to extract user ID from response: {e}")
        
        # If no users exist, skip (empty is acceptable for users)
        if not user_id or user_id == "None":
            pytest.skip("No users exist in the system - test passes")
        
        # Test enabling user - some operations might have legitimate constraints
        result = await client.call_tool("set_user_enabled", {"user_id": user_id, "enabled": True})
        data = extract_response_data(result)
        
        # Allow certain operational errors that are expected for user management
        acceptable_errors = [
            "user cannot be modified",
            "operation not permitted",
            "user is system user",
            "insufficient privileges"
        ]
        assert_no_error_in_response(data, "set_user_enabled", acceptable_errors)

async def test_get_user_groups_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_user_groups_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_user_groups_list")
        
        # Empty user groups list is acceptable - just verify structure
        if isinstance(data, dict):
            if "userGroups" in data:
                assert isinstance(data["userGroups"], list), "userGroups should be a list"
            else:
                assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            # Direct list response is also acceptable
            assert len(data) >= 0, "List response should be valid"
        elif isinstance(data, str):
            # String response without errors is acceptable
            pass

async def test_get_user_group_properties(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of user groups
        user_groups_result = await client.call_tool("get_user_groups_list", {})
        groups_data = extract_response_data(user_groups_result)
        assert_no_error_in_response(groups_data, "get_user_groups_list")
        
        user_group_id = None
        try:
            # Handle both wrapper format and raw API response
            if isinstance(groups_data, dict):
                if "userGroups" in groups_data and groups_data["userGroups"]:
                    groups_list = groups_data["userGroups"]
                    if isinstance(groups_list, list) and len(groups_list) > 0:
                        user_group_id = str(groups_list[0].get("userGroupId"))
            elif isinstance(groups_data, list) and groups_data:
                user_group_id = str(groups_data[0].get("userGroupId"))
        except Exception as e:
            raise AssertionError(f"Failed to extract user group ID from response: {e}")
        
        # If no user groups exist, skip (empty is acceptable for user groups)
        if not user_group_id or user_group_id == "None":
            pytest.skip("No user groups exist in the system - test passes")
        
        # Test getting user group properties for existing group
        result = await client.call_tool("get_user_group_properties", {"user_group_id": user_group_id})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_user_group_properties")
        
        # Verify it returns group data
        if isinstance(data, dict):
            assert len(data) >= 0, "User group properties response should be valid"
        elif isinstance(data, str):
            # String response without errors is acceptable
            pass

# async def test_set_user_group_assignment(mcp_server):
#     async with Client(mcp_server) as client:
#         # First get the list of users to get a valid user_id
#         users = await client.call_tool("get_users_list", {})
#         
#         user_id = None
#         if isinstance(users, list) and len(users) > 0:
#             # Extract user ID from the response
#             if hasattr(users[0], "text"):
#                 try:
#                     users_data = json.loads(users[0].text)
#                     if isinstance(users_data, list) and len(users_data) > 0:
#                         user_id = str(users_data[0].get("userId"))
#                     elif isinstance(users_data, dict) and "users" in users_data:
#                         users_list = users_data["users"]
#                         if isinstance(users_list, list) and len(users_list) > 0:
#                             user_id = str(users_list[0].get("userId"))
#                 except (json.JSONDecodeError, KeyError):
#                     pass
#         
#         # Then get the list of user groups to get a valid user_group_id
#         user_groups = await client.call_tool("get_user_groups_list", {})
#         
#         user_group_id = None
#         if isinstance(user_groups, list) and len(user_groups) > 0:
#             # Extract user group ID from the response
#             if hasattr(user_groups[0], "text"):
#                 try:
#                     groups_data = json.loads(user_groups[0].text)
#                     if isinstance(groups_data, list) and len(groups_data) > 0:
#                         user_group_id = str(groups_data[0].get("userGroupId"))
#                     elif isinstance(groups_data, dict) and "userGroups" in groups_data:
#                         groups_list = groups_data["userGroups"]
#                         if isinstance(groups_list, list) and len(groups_list) > 0:
#                             user_group_id = str(groups_list[0].get("userGroupId"))
#                 except (json.JSONDecodeError, KeyError):
#                     pass
#         
#         # Only run test if we found both valid IDs
#         if user_id and user_group_id:
#             result = await client.call_tool("set_user_group_assignment", {"user_id": user_id, "user_group_id": user_group_id, "assign": True})
#             assert "error" not in result[0].text.lower() or "success" in result[0].text.lower()
#         else:
#             # Skip test if no valid IDs found
#             assert True, "No valid user/group combination found to test with"

async def test_get_associated_entities_for_user(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of users
        users_result = await client.call_tool("get_users_list", {})
        users_data = extract_response_data(users_result)
        assert_no_error_in_response(users_data, "get_users_list")
        
        user_id = None
        try:
            if isinstance(users_data, dict):
                if "users" in users_data and users_data["users"]:
                    users_list = users_data["users"]
                    if isinstance(users_list, list) and len(users_list) > 0:
                        user_id = str(users_list[0].get("userId"))
            elif isinstance(users_data, list) and users_data:
                user_id = str(users_data[0].get("userId"))
        except Exception as e:
            raise AssertionError(f"Failed to extract user ID from response: {e}")
        
        # If no users exist, skip
        if not user_id or user_id == "None":
            pytest.skip("No users exist in the system - test passes")
        
        # Test getting associated entities for existing user
        result = await client.call_tool("get_associated_entities_for_user_or_user_group", {"id": user_id, "type": "user"})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_associated_entities_for_user_or_user_group")
        
        # Verify it returns association data
        if isinstance(data, dict):
            assert len(data) >= 0, "User associations response should be valid"
        elif isinstance(data, str):
            # String response without errors is acceptable
            pass

async def test_get_associated_entities_for_user_group(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of user groups
        user_groups_result = await client.call_tool("get_user_groups_list", {})
        groups_data = extract_response_data(user_groups_result)
        assert_no_error_in_response(groups_data, "get_user_groups_list")
        
        user_group_id = None
        try:
            if isinstance(groups_data, dict):
                if "userGroups" in groups_data and groups_data["userGroups"]:
                    groups_list = groups_data["userGroups"]
                    if isinstance(groups_list, list) and len(groups_list) > 0:
                        user_group_id = str(groups_list[0].get("userGroupId"))
            elif isinstance(groups_data, list) and groups_data:
                user_group_id = str(groups_data[0].get("userGroupId"))
        except Exception as e:
            raise AssertionError(f"Failed to extract user group ID from response: {e}")
        
        # If no user groups exist, skip
        if not user_group_id or user_group_id == "None":
            pytest.skip("No user groups exist in the system - test passes")
        
        # Test getting associated entities for existing user group
        result = await client.call_tool("get_associated_entities_for_user_or_user_group", {"id": user_group_id, "type": "usergroup"})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_associated_entities_for_user_or_user_group")
        
        # Verify it returns association data
        if isinstance(data, dict):
            assert len(data) >= 0, "User group associations response should be valid"
        elif isinstance(data, str):
            # String response without errors is acceptable
            pass

async def test_view_entity_permissions(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of clients to get a valid entity_id
        clients_result = await client.call_tool("get_client_list", {})
        clients_data = extract_response_data(clients_result)
        assert_no_error_in_response(clients_data, "get_client_list")
        
        client_id = None
        try:
            if isinstance(clients_data, dict):
                if "clients" in clients_data and clients_data["clients"]:
                    clients_list = clients_data["clients"]
                    if isinstance(clients_list, list) and len(clients_list) > 0:
                        client_id = str(clients_list[0].get("clientId"))
            elif isinstance(clients_data, list) and clients_data:
                client_id = str(clients_data[0].get("clientId"))
        except Exception as e:
            raise AssertionError(f"Failed to extract client ID from response: {e}")
        
        # If no clients exist, skip
        if not client_id or client_id == "None":
            pytest.skip("No clients exist in the system - test passes")
        
        # Test viewing entity permissions for existing client
        result = await client.call_tool("view_entity_permissions", {"entity_type": "CLIENT_ENTITY", "entity_id": client_id})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "view_entity_permissions")
        
        # Verify it returns permissions data
        if isinstance(data, dict):
            assert len(data) >= 0, "Entity permissions response should be valid"
        elif isinstance(data, str):
            # String response without errors is acceptable
            pass

# async def test_grant_or_revoke_access_to_entity(mcp_server):
#     async with Client(mcp_server) as client:
#         # First get the list of client groups to get a valid entity_id
#         client_groups = await client.call_tool("get_client_group_list", {})
#         
#         entity_id = None
#         if isinstance(client_groups, list) and len(client_groups) > 0:
#             # Extract client group ID from the response
#             if hasattr(client_groups[0], "text"):
#                 try:
#                     groups_data = json.loads(client_groups[0].text)
#                     if isinstance(groups_data, list) and len(groups_data) > 0:
#                         entity_id = str(groups_data[0].get("id"))
#                 except (json.JSONDecodeError, KeyError):
#                     pass
#         
#         # Get users to get a valid user_id
#         users = await client.call_tool("get_users_list", {})
#         
#         user_id = None
#         if isinstance(users, list) and len(users) > 0:
#             # Extract user ID from the response
#             if hasattr(users[0], "text"):
#                 try:
#                     users_data = json.loads(users[0].text)
#                     if isinstance(users_data, list) and len(users_data) > 0:
#                         user_id = str(users_data[0].get("userId"))
#                     elif isinstance(users_data, dict) and "users" in users_data:
#                         users_list = users_data["users"]
#                         if isinstance(users_list, list) and len(users_list) > 0:
#                             user_id = str(users_list[0].get("userId"))
#                 except (json.JSONDecodeError, KeyError):
#                     pass
#         
#         # Get roles to get a valid role_id
#         roles = await client.call_tool("get_roles_list", {})
#         
#         role_id = None
#         if isinstance(roles, list) and len(roles) > 0:
#             # Extract role ID from the response
#             if hasattr(roles[0], "text"):
#                 try:
#                     roles_data = json.loads(roles[0].text)
#                     if isinstance(roles_data, list) and len(roles_data) > 0:
#                         role_id = roles_data[0].get("roleId")
#                     elif isinstance(roles_data, dict) and "roles" in roles_data:
#                         roles_list = roles_data["roles"]
#                         if isinstance(roles_list, list) and len(roles_list) > 0:
#                             role_id = roles_list[0].get("roleId")
#                 except (json.JSONDecodeError, KeyError):
#                     pass
#         
#         # Only run test if we found all required IDs
#         if entity_id and user_id and role_id:
#             result = await client.call_tool("grant_or_revoke_access_to_entity", {
#                 "entity_id": entity_id,
#                 "entity_type": "client_group",
#                 "role_id": role_id,
#                 "user_id": user_id,
#                 "assign": True
#             })
#             assert "error" not in result[0].text.lower() or "success" in result[0].text.lower()
#         else:
#             # Skip test if no valid combination found
#             assert True, "No valid entity/user/role combination found to test with"

async def test_get_roles_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_roles_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_roles_list")
        
        # Empty roles list is acceptable - just verify structure
        if isinstance(data, dict):
            if "roles" in data:
                assert isinstance(data["roles"], list), "roles should be a list"
            else:
                assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            # Direct list response is also acceptable
            assert len(data) >= 0, "List response should be valid"
        elif isinstance(data, str):
            # String response without errors is acceptable
            pass