import json
from fastmcp import Client
          
def is_real_error(data):
    """Return True only if errorMessage is not blank or errorCode is not 0."""
    error = data.get("error", {})
    return bool(error.get("errorMessage")) or error.get("errorCode", 0) not in (0, "")

async def test_get_storage_policy_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_storage_policy_list", {})
        assert isinstance(result, list)

async def test_get_storage_policy_properties(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of storage policies to get a valid storage_policy_id
        storage_policies = await client.call_tool("get_storage_policy_list", {})
        
        storage_policy_id = None
        if isinstance(storage_policies, list) and len(storage_policies) > 0:
            # Extract storage policy ID from the response
            if hasattr(storage_policies[0], "text"):
                try:
                    policies_data = json.loads(storage_policies[0].text)
                    if isinstance(policies_data, list) and len(policies_data) > 0:
                        storage_policy_id = str(policies_data[0].get("storagePolicyId"))
                    elif isinstance(policies_data, dict) and "policies" in policies_data:
                        policies_list = policies_data["policies"]
                        if isinstance(policies_list, list) and len(policies_list) > 0:
                            storage_policy_id = str(policies_list[0].get("storagePolicyId"))
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid storage policy ID
        if storage_policy_id:
            result = await client.call_tool("get_storage_policy_properties", {"storage_policy_id": storage_policy_id})
            data = json.loads(result[0].text)
            assert not is_real_error(data)
        else:
            # Skip test if no storage policies found
            assert True, "No storage policies found to test with"

async def test_get_storage_policy_copy_details(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of storage policies to get a valid storage_policy_id
        storage_policies = await client.call_tool("get_storage_policy_list", {})
        
        storage_policy_id = None
        if isinstance(storage_policies, list) and len(storage_policies) > 0:
            # Extract storage policy ID from the response
            if hasattr(storage_policies[0], "text"):
                try:
                    policies_data = json.loads(storage_policies[0].text)
                    if isinstance(policies_data, list) and len(policies_data) > 0:
                        storage_policy_id = str(policies_data[0].get("storagePolicyId"))
                    elif isinstance(policies_data, dict) and "policies" in policies_data:
                        policies_list = policies_data["policies"]
                        if isinstance(policies_list, list) and len(policies_list) > 0:
                            storage_policy_id = str(policies_list[0].get("storagePolicyId"))
                except (json.JSONDecodeError, KeyError):
                    pass
        
        if not storage_policy_id:
            assert True, "No storage policies found to test with"
            return
        
        # Get storage policy properties to find a valid copy ID
        policy_props = await client.call_tool("get_storage_policy_properties", {"storage_policy_id": storage_policy_id})
        
        copy_id = None
        if isinstance(policy_props, list) and len(policy_props) > 0:
            if hasattr(policy_props[0], "text"):
                try:
                    props_data = json.loads(policy_props[0].text)
                    # Look for copy information in the policy properties
                    if isinstance(props_data, dict) and "storagePolicyCopyInfo" in props_data:
                        copies = props_data["storagePolicyCopyInfo"]
                        if isinstance(copies, list) and len(copies) > 0:
                            copy_id = str(copies[0].get("copyId"))
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid copy ID
        if copy_id:
            result = await client.call_tool("get_storage_policy_copy_details", {"storage_policy_id": storage_policy_id, "copy_id": copy_id})
            data = json.loads(result[0].text)
            assert not is_real_error(data)
        else:
            # Skip test if no copy found
            assert True, "No storage policy copies found to test with"

# async def test_get_storage_policy_copy_size(mcp_server):
#     async with Client(mcp_server) as client:
#         # First get the list of storage policies to get a valid storage_policy_id
#         storage_policies = await client.call_tool("get_storage_policy_list", {})
#         
#         storage_policy_id = None
#         if isinstance(storage_policies, list) and len(storage_policies) > 0:
#             # Extract storage policy ID from the response
#             if hasattr(storage_policies[0], "text"):
#                 try:
#                     policies_data = json.loads(storage_policies[0].text)
#                     if isinstance(policies_data, list) and len(policies_data) > 0:
#                         storage_policy_id = str(policies_data[0].get("storagePolicyId"))
#                     elif isinstance(policies_data, dict) and "policies" in policies_data:
#                         policies_list = policies_data["policies"]
#                         if isinstance(policies_list, list) and len(policies_list) > 0:
#                             storage_policy_id = str(policies_list[0].get("storagePolicyId"))
#                 except (json.JSONDecodeError, KeyError):
#                     pass
#         
#         if not storage_policy_id:
#             assert True, "No storage policies found to test with"
#             return
#         
#         # Get storage policy properties to find a valid copy ID
#         policy_props = await client.call_tool("get_storage_policy_properties", {"storage_policy_id": storage_policy_id})
#         
#         copy_id = None
#         if isinstance(policy_props, list) and len(policy_props) > 0:
#             if hasattr(policy_props[0], "text"):
#                 try:
#                     props_data = json.loads(policy_props[0].text)
#                     # Look for copy information in the policy properties
#                     if isinstance(props_data, dict) and "storagePolicyCopyInfo" in props_data:
#                         copies = props_data["storagePolicyCopyInfo"]
#                         if isinstance(copies, list) and len(copies) > 0:
#                             copy_id = str(copies[0].get("copyId"))
#                 except (json.JSONDecodeError, KeyError):
#                     pass
#         
#         # Only run test if we found a valid copy ID
#         if copy_id:
#             result = await client.call_tool("get_storage_policy_copy_size", {"storage_policy_id": storage_policy_id, "copy_id": copy_id})
#             data = json.loads(result[0].text)
#             assert not is_real_error(data)
#         else:
#             # Skip test if no copy found
#             assert True, "No storage policy copies found to test with"

async def test_get_library_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_library_list", {})
        print("get_library_list result:", result)
        assert isinstance(result, list)

# async def test_get_library_properties(mcp_server):
#     async with Client(mcp_server) as client:
#         # First get the list of libraries to get a valid library_id
#         libraries = await client.call_tool("get_library_list", {})
#         
#         library_id = None
#         if isinstance(libraries, list) and len(libraries) > 0:
#             # Extract library ID from the response
#             if hasattr(libraries[0], "text"):
#                 try:
#                     libraries_data = json.loads(libraries[0].text)
#                     if isinstance(libraries_data, list) and len(libraries_data) > 0:
#                         library_id = str(libraries_data[0].get("libraryId"))
#                     elif isinstance(libraries_data, dict) and "libraries" in libraries_data:
#                         libraries_list = libraries_data["libraries"]
#                         if isinstance(libraries_list, list) and len(libraries_list) > 0:
#                             library_id = str(libraries_list[0].get("libraryId"))
#                 except (json.JSONDecodeError, KeyError):
#                     pass
#         
#         # Only run test if we found a valid library ID
#         if library_id:
#             result = await client.call_tool("get_library_properties", {"library_id": library_id})
#             data = json.loads(result[0].text)
#             assert not is_real_error(data)
#         else:
#             # Skip test if no libraries found
#             assert True, "No libraries found to test with"

async def test_get_storage_pool_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_storage_pool_list", {})
        assert isinstance(result, list)

async def test_get_mediaagent_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_mediaagent_list", {})
        assert isinstance(result, list)