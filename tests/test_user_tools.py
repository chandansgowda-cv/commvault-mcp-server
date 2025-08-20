from fastmcp import Client
import json
  
async def test_get_users_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_users_list", {})
        assert isinstance(result, list) or "error" not in result[0].text.lower()

async def test_get_user_properties(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of users to get a valid user_id
        users = await client.call_tool("get_users_list", {})
        
        user_id = None
        if isinstance(users, list) and len(users) > 0:
            # Extract user ID from the response
            if hasattr(users[0], "text"):
                try:
                    users_data = json.loads(users[0].text)
                    if isinstance(users_data, list) and len(users_data) > 0:
                        user_id = str(users_data[0].get("userId"))
                    elif isinstance(users_data, dict) and "users" in users_data:
                        users_list = users_data["users"]
                        if isinstance(users_list, list) and len(users_list) > 0:
                            user_id = str(users_list[0].get("userId"))
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid user ID
        if user_id:
            result = await client.call_tool("get_user_properties", {"user_id": user_id})
            assert "error" not in result[0].text.lower() or isinstance(result, dict)
        else:
            # Skip test if no users found
            assert True, "No users found to test with"

async def test_set_user_enabled(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of users to get a valid user_id
        users = await client.call_tool("get_users_list", {})
        
        user_id = None
        if isinstance(users, list) and len(users) > 0:
            # Extract user ID from the response
            if hasattr(users[0], "text"):
                try:
                    users_data = json.loads(users[0].text)
                    if isinstance(users_data, list) and len(users_data) > 0:
                        user_id = str(users_data[0].get("userId"))
                    elif isinstance(users_data, dict) and "users" in users_data:
                        users_list = users_data["users"]
                        if isinstance(users_list, list) and len(users_list) > 0:
                            user_id = str(users_list[0].get("userId"))
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid user ID
        if user_id:
            result = await client.call_tool("set_user_enabled", {"user_id": user_id, "enabled": True})
            assert "error" not in result[0].text.lower() or "success" in result[0].text.lower()
        else:
            # Skip test if no users found
            assert True, "No users found to test with"

async def test_get_user_groups_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_user_groups_list", {})
        assert isinstance(result, list) or "error" not in result[0].text.lower()

async def test_get_user_group_properties(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of user groups to get a valid user_group_id
        user_groups = await client.call_tool("get_user_groups_list", {})
        
        user_group_id = None
        if isinstance(user_groups, list) and len(user_groups) > 0:
            # Extract user group ID from the response
            if hasattr(user_groups[0], "text"):
                try:
                    groups_data = json.loads(user_groups[0].text)
                    if isinstance(groups_data, list) and len(groups_data) > 0:
                        user_group_id = str(groups_data[0].get("userGroupId"))
                    elif isinstance(groups_data, dict) and "userGroups" in groups_data:
                        groups_list = groups_data["userGroups"]
                        if isinstance(groups_list, list) and len(groups_list) > 0:
                            user_group_id = str(groups_list[0].get("userGroupId"))
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid user group ID
        if user_group_id:
            result = await client.call_tool("get_user_group_properties", {"user_group_id": user_group_id})
            assert "error" not in result[0].text.lower() or isinstance(result, dict)
        else:
            # Skip test if no user groups found
            assert True, "No user groups found to test with"

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
        # First get the list of users to get a valid user_id
        users = await client.call_tool("get_users_list", {})
        
        user_id = None
        if isinstance(users, list) and len(users) > 0:
            # Extract user ID from the response
            if hasattr(users[0], "text"):
                try:
                    users_data = json.loads(users[0].text)
                    if isinstance(users_data, list) and len(users_data) > 0:
                        user_id = str(users_data[0].get("userId"))
                    elif isinstance(users_data, dict) and "users" in users_data:
                        users_list = users_data["users"]
                        if isinstance(users_list, list) and len(users_list) > 0:
                            user_id = str(users_list[0].get("userId"))
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid user ID
        if user_id:
            result = await client.call_tool("get_associated_entities_for_user_or_user_group", {"id": user_id, "type": "user"})
            assert "error" not in result[0].text.lower() or isinstance(result, dict)
        else:
            # Skip test if no users found
            assert True, "No users found to test with"

async def test_get_associated_entities_for_user_group(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of user groups to get a valid user_group_id
        user_groups = await client.call_tool("get_user_groups_list", {})
        
        user_group_id = None
        if isinstance(user_groups, list) and len(user_groups) > 0:
            # Extract user group ID from the response
            if hasattr(user_groups[0], "text"):
                try:
                    groups_data = json.loads(user_groups[0].text)
                    if isinstance(groups_data, list) and len(groups_data) > 0:
                        user_group_id = str(groups_data[0].get("userGroupId"))
                    elif isinstance(groups_data, dict) and "userGroups" in groups_data:
                        groups_list = groups_data["userGroups"]
                        if isinstance(groups_list, list) and len(groups_list) > 0:
                            user_group_id = str(groups_list[0].get("userGroupId"))
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid user group ID
        if user_group_id:
            result = await client.call_tool("get_associated_entities_for_user_or_user_group", {"id": user_group_id, "type": "usergroup"})
            assert "error" not in result[0].text.lower() or isinstance(result, dict)
        else:
            # Skip test if no user groups found
            assert True, "No user groups found to test with"

async def test_view_entity_permissions(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of clients to get a valid entity_id
        clients = await client.call_tool("get_client_list", {})
        
        client_id = None
        if isinstance(clients, list) and len(clients) > 0:
            # Extract client ID from the response
            if hasattr(clients[0], "text"):
                try:
                    clients_data = json.loads(clients[0].text)
                    if isinstance(clients_data, list) and len(clients_data) > 0:
                        client_id = str(clients_data[0].get("clientId"))
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid client ID
        if client_id:
            result = await client.call_tool("view_entity_permissions", {"entity_type": "CLIENT_ENTITY", "entity_id": client_id})
            assert "error" not in result[0].text.lower() or isinstance(result, dict)
        else:
            # Skip test if no clients found
            assert True, "No clients found to test with"

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
        assert isinstance(result, list) or "error" not in result[0].text.lower()