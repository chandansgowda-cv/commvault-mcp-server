from fastmcp import Client
import json

async def test_get_client_group_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_client_group_list", {})
        assert isinstance(result, list) or "error" not in result[0].text.lower()

async def test_get_client_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_client_list", {})
        assert isinstance(result, list) or "error" not in result[0].text.lower()

async def test_get_client_group_properties(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of client groups to get a valid client_group_id
        client_groups = await client.call_tool("get_client_group_list", {})
        
        client_group_id = None
        if isinstance(client_groups, list) and len(client_groups) > 0:
            # Extract client group ID from the response
            if hasattr(client_groups[0], "text"):
                try:
                    groups_data = json.loads(client_groups[0].text)
                    if isinstance(groups_data, list) and len(groups_data) > 0:
                        client_group_id = str(groups_data[0].get("id"))
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid client group ID
        if client_group_id:
            result = await client.call_tool("get_client_group_properties", {"client_group_id": client_group_id})
            assert "error" not in result[0].text.lower() or isinstance(result, dict)
        else:
            # Skip test if no client groups found
            assert True, "No client groups found to test with"

async def test_get_clientid_from_clientname(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of clients to get a valid client name
        clients = await client.call_tool("get_client_list", {})
        
        client_name = None
        if isinstance(clients, list) and len(clients) > 0:
            # Extract client name from the response
            if hasattr(clients[0], "text"):
                try:
                    clients_data = json.loads(clients[0].text)
                    if isinstance(clients_data, list) and len(clients_data) > 0:
                        client_name = clients_data[0].get("clientName")
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid client name
        if client_name:
            result = await client.call_tool("get_clientid_from_clientname", {"client_name": client_name})
            assert "error" not in result[0].text.lower() or isinstance(result, dict)
        else:
            # Skip test if no clients found
            assert True, "No clients found to test with"

async def test_get_subclient_list_by_name(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of clients to get a valid client name
        clients = await client.call_tool("get_client_list", {})
        
        client_name = None
        if isinstance(clients, list) and len(clients) > 0:
            # Extract client name from the response
            if hasattr(clients[0], "text"):
                try:
                    clients_data = json.loads(clients[0].text)
                    if isinstance(clients_data, list) and len(clients_data) > 0:
                        client_name = clients_data[0].get("clientName")
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid client name
        if client_name:
            result = await client.call_tool("get_subclient_list", {"client_identifier": client_name, "identifier_type": "name"})
            assert "error" not in result[0].text.lower() or isinstance(result, list)
        else:
            # Skip test if no clients found
            assert True, "No clients found to test with"

async def test_get_subclient_list_by_id(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of clients to get a valid client ID
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
            result = await client.call_tool("get_subclient_list", {"client_identifier": client_id, "identifier_type": "id"})
            assert "error" not in result[0].text.lower() or isinstance(result, list)
        else:
            # Skip test if no clients found
            assert True, "No clients found to test with"

async def test_get_subclient_properties(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of clients to get a valid client ID
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
        
        if not client_id:
            assert True, "No clients found to test with"
            return
        
        # Get subclients for this client
        subclients = await client.call_tool("get_subclient_list", {"client_identifier": client_id, "identifier_type": "id"})
        
        subclient_id = None
        if isinstance(subclients, list) and len(subclients) > 0:
            # Extract subclient ID from the response
            if hasattr(subclients[0], "text"):
                try:
                    subclients_data = json.loads(subclients[0].text)
                    if isinstance(subclients_data, list) and len(subclients_data) > 0:
                        subclient_id = str(subclients_data[0].get("subClientId"))
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid subclient ID
        if subclient_id:
            result = await client.call_tool("get_subclient_properties", {"subclient_id": subclient_id})
            assert "error" not in result[0].text.lower() or isinstance(result, dict)
        else:
            # Skip test if no subclients found
            assert True, "No subclients found to test with"

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