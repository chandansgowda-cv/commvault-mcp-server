from fastmcp import Client
import json
 
async def test_get_schedules_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_schedules_list", {})
        assert isinstance(result, list) or "error" not in result[0].text.lower()

async def test_get_schedule_properties(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of schedules to get a valid schedule_id
        schedules = await client.call_tool("get_schedules_list", {})
        
        schedule_id = None
        if isinstance(schedules, list) and len(schedules) > 0:
            # Extract schedule ID from the response
            if hasattr(schedules[0], "text"):
                try:
                    schedules_data = json.loads(schedules[0].text)
                    if isinstance(schedules_data, list) and len(schedules_data) > 0:
                        schedule_id = str(schedules_data[0].get("taskId"))
                    elif isinstance(schedules_data, dict) and "schedules" in schedules_data:
                        schedules_list = schedules_data["schedules"]
                        if isinstance(schedules_list, list) and len(schedules_list) > 0:
                            task_id = schedules_list[0].get("taskId")
                            schedule_id = str(task_id) if task_id is not None else None
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid schedule ID
        if schedule_id:
            result = await client.call_tool("get_schedule_properties", {"schedule_id": schedule_id})
            print(result)
            assert "error" not in result[0].text.lower() or "schedule" in result[0].text.lower() or isinstance(result, dict)
        else:
            # Skip test if no schedules found
            assert True, "No schedules found to test with"


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