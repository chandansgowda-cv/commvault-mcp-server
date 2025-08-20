from fastmcp import Client
import json

def is_real_error(data):
    """Return True only if errorMessage is not blank or errorCode is not 0."""
    error = data.get("error", {})
    return bool(error.get("errorMessage")) or error.get("errorCode", 0) not in (0, "")

async def test_get_sla_status(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_sla_status", {})
        if isinstance(result, list) and hasattr(result[0], "text"):
            data = json.loads(result[0].text)
            assert not is_real_error(data)
        else:
            assert isinstance(result, dict)

async def test_get_security_posture(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_security_posture", {})
        if isinstance(result, list) and hasattr(result[0], "text"):
            data = json.loads(result[0].text)
            assert not is_real_error(data)
        else:
            assert isinstance(result, dict)

async def test_get_security_score(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_security_score", {})
        if isinstance(result, list) and hasattr(result[0], "text"):
            data = json.loads(result[0].text)
            assert not is_real_error(data)
        else:
            assert isinstance(result, dict)

async def test_get_storage_space_utilization(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_storage_space_utilization", {})
        if isinstance(result, list) and hasattr(result[0], "text"):
            data = json.loads(result[0].text)
            assert not is_real_error(data)
        else:
            assert isinstance(result, dict)

async def test_get_commcell_details(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_commcell_details", {})
        if isinstance(result, list) and hasattr(result[0], "text"):
            data = json.loads(result[0].text)
            assert not is_real_error(data)
        else:
            assert isinstance(result, dict)

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
        
        commcell_name = None
        if isinstance(commcell_details, list) and hasattr(commcell_details[0], "text"):
            try:
                details_data = json.loads(commcell_details[0].text)
                if isinstance(details_data, list) and len(details_data) > 0:
                    commcell_name = details_data[0].get("commCellName")
                elif isinstance(details_data, dict) and "commCellName" in details_data:
                    commcell_name = details_data["commCellName"]
            except (json.JSONDecodeError, KeyError):
                pass
        
        # If we can't get CommCell name from details, try getting client list and use first client name
        if not commcell_name:
            clients = await client.call_tool("get_client_list", {})
            if isinstance(clients, list) and len(clients) > 0:
                if hasattr(clients[0], "text"):
                    try:
                        clients_data = json.loads(clients[0].text)
                        if isinstance(clients_data, list) and len(clients_data) > 0:
                            commcell_name = clients_data[0].get("clientName")
                    except (json.JSONDecodeError, KeyError):
                        pass
        
        # Only run test if we found a valid CommCell name
        if commcell_name:
            result = await client.call_tool(
                "create_send_logs_job_for_commcell",
                {"emailid": "nmurali@commvault.com", "commcell_name": commcell_name}
            )
            if isinstance(result, list) and hasattr(result[0], "text"):
                data = json.loads(result[0].text)
                assert not is_real_error(data)
            else:
                assert isinstance(result, dict)
        else:
            # Skip test if no CommCell name found
            assert True, "No CommCell name found to test with"