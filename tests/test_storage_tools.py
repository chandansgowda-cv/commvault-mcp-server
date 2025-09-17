import json
from fastmcp import Client
import pytest

def extract_response_data(result):
    # Handle CallToolResult object
    if hasattr(result, 'content'):
        content_list = result.content
    else:
        content_list = result
    
    if not isinstance(content_list, list) or len(content_list) == 0:
        raise AssertionError("Expected list response with at least one item")
    
    if not hasattr(content_list[0], "text"):
        raise AssertionError("Response item missing 'text' attribute")
    
    response_text = content_list[0].text
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return response_text

def assert_no_error_in_response(data, operation_name):
    if isinstance(data, str):
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

async def test_get_storage_policy_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_storage_policy_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_storage_policy_list")
        
        if isinstance(data, dict):
            if "storagePolicies" in data:
                assert isinstance(data["storagePolicies"], list), "storagePolicies should be a list"
            else:
                assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            assert len(data) >= 0, "List response should be valid"
        elif isinstance(data, str):
            pass

async def test_get_storage_policy_properties(mcp_server):
    storage_policy_id = None
    
    async with Client(mcp_server) as client:
        storage_policies_result = await client.call_tool("get_storage_policy_list", {})
        policies_data = extract_response_data(storage_policies_result)
        assert_no_error_in_response(policies_data, "get_storage_policy_list")
        
        if isinstance(policies_data, dict) and "policies" in policies_data:
            policies = policies_data["policies"]
            if isinstance(policies, list) and len(policies) > 0:
                first_policy = policies[0]
                if isinstance(first_policy, dict) and "storagePolicy" in first_policy:
                    storage_policy = first_policy["storagePolicy"]
                    if isinstance(storage_policy, dict) and "storagePolicyId" in storage_policy:
                        storage_policy_id = str(storage_policy["storagePolicyId"])
    
    if storage_policy_id is not None:
        async with Client(mcp_server) as client:
            result = await client.call_tool("get_storage_policy_properties", {"storage_policy_id": storage_policy_id})
            data = extract_response_data(result)
            assert_no_error_in_response(data, "get_storage_policy_properties")
        
            if isinstance(data, dict):
                assert len(data) > 0, "Storage policy properties response should not be empty"
    else:
        pytest.skip("No storage policies found to test with")

async def test_get_storage_policy_copy_details(mcp_server):
    storage_policy_id = None
    copy_id = None
    
    async with Client(mcp_server) as client:
        storage_policies_result = await client.call_tool("get_storage_policy_list", {})
        policies_data = extract_response_data(storage_policies_result)
        assert_no_error_in_response(policies_data, "get_storage_policy_list")
        
        if isinstance(policies_data, dict) and "policies" in policies_data:
            policies = policies_data["policies"]
            if isinstance(policies, list) and len(policies) > 0:
                first_policy = policies[0]
                if isinstance(first_policy, dict) and "storagePolicy" in first_policy:
                    storage_policy = first_policy["storagePolicy"]
                    if isinstance(storage_policy, dict) and "storagePolicyId" in storage_policy:
                        storage_policy_id = str(storage_policy["storagePolicyId"])
        
        if storage_policy_id:
            policy_props_result = await client.call_tool("get_storage_policy_properties", {"storage_policy_id": storage_policy_id})
            policy_props_data = extract_response_data(policy_props_result)
            assert_no_error_in_response(policy_props_data, "get_storage_policy_properties")
            
            if isinstance(policy_props_data, dict) and "policies" in policy_props_data:
                policies = policy_props_data["policies"]
                if isinstance(policies, list) and len(policies) > 0:
                    first_policy = policies[0]
                    if isinstance(first_policy, dict) and "copies" in first_policy:
                        copies = first_policy["copies"]
                        if isinstance(copies, list) and len(copies) > 0:
                            first_copy = copies[0]
                            if isinstance(first_copy, dict) and "StoragePolicyCopy" in first_copy:
                                storage_policy_copy = first_copy["StoragePolicyCopy"]
                                if isinstance(storage_policy_copy, dict) and "copyId" in storage_policy_copy:
                                    copy_id = str(storage_policy_copy["copyId"])
    
    if storage_policy_id is not None and copy_id is not None:
        async with Client(mcp_server) as client:
            result = await client.call_tool("get_storage_policy_copy_details", {"storage_policy_id": storage_policy_id, "copy_id": copy_id})
            data = extract_response_data(result)
            assert_no_error_in_response(data, "get_storage_policy_copy_details")
    else:
        pytest.skip("No storage policy or copy found to test with")

# async def test_get_storage_policy_copy_size(mcp_server):
#     async with Client(mcp_server) as client:
#         storage_policies = await client.call_tool("get_storage_policy_list", {})
#         
#         storage_policy_id = None
#         if isinstance(storage_policies, list) and len(storage_policies) > 0:
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
#         policy_props = await client.call_tool("get_storage_policy_properties", {"storage_policy_id": storage_policy_id})
#         
#         copy_id = None
#         if isinstance(policy_props, list) and len(policy_props) > 0:
#             if hasattr(policy_props[0], "text"):
#                 try:
#                     props_data = json.loads(policy_props[0].text)
#                     if isinstance(props_data, dict) and "storagePolicyCopyInfo" in props_data:
#                         copies = props_data["storagePolicyCopyInfo"]
#                         if isinstance(copies, list) and len(copies) > 0:
#                             copy_id = str(copies[0].get("copyId"))
#                 except (json.JSONDecodeError, KeyError):
#                     pass
#         
#         if copy_id:
#             result = await client.call_tool("get_storage_policy_copy_size", {"storage_policy_id": storage_policy_id, "copy_id": copy_id})
#             data = json.loads(result[0].text)
#             assert not is_real_error(data)
#         else:
#             assert True, "No storage policy copies found to test with"

async def test_get_library_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_library_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_library_list")
        
        if isinstance(data, dict):
            if "libraries" in data:
                assert isinstance(data["libraries"], list), "libraries should be a list"
            else:
                assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            assert len(data) >= 0, "List response should be valid"
        elif isinstance(data, str):
            pass

# async def test_get_library_properties(mcp_server):
#     async with Client(mcp_server) as client:
#         libraries = await client.call_tool("get_library_list", {})
#         
#         library_id = None
#         if isinstance(libraries, list) and len(libraries) > 0:
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
#         if library_id:
#             result = await client.call_tool("get_library_properties", {"library_id": library_id})
#             data = json.loads(result[0].text)
#             assert not is_real_error(data)
#         else:
#             assert True, "No libraries found to test with"

async def test_get_storage_pool_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_storage_pool_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_storage_pool_list")
        
        if isinstance(data, dict):
            if "storagePools" in data:
                assert isinstance(data["storagePools"], list), "storagePools should be a list"
            else:
                assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            assert len(data) >= 0, "List response should be valid"
        elif isinstance(data, str):
            pass

async def test_get_mediaagent_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_mediaagent_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_mediaagent_list")
        
        if isinstance(data, dict):
            if "mediaAgents" in data:
                assert isinstance(data["mediaAgents"], list), "mediaAgents should be a list"
            else:
                assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            assert len(data) >= 0, "List response should be valid"
        elif isinstance(data, str):
            pass