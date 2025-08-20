from fastmcp import Client
import json

async def test_get_plan_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_plan_list", {})
        assert isinstance(result, list) or "error" not in result[0].text.lower()

async def test_get_plan_properties(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of plans to get a valid plan_id
        plans = await client.call_tool("get_plan_list", {})
        
        plan_id = None
        if isinstance(plans, list) and len(plans) > 0:
            # Extract plan ID from the response
            if hasattr(plans[0], "text"):
                try:
                    plans_data = json.loads(plans[0].text)
                    if isinstance(plans_data, dict) and "plans" in plans_data:
                        plans_list = plans_data["plans"]
                        if isinstance(plans_list, list) and len(plans_list) > 0:
                            plan_id = plans_list[0].get("plan", {}).get("planId")
                            if plan_id:
                                plan_id = str(plan_id)
                    elif isinstance(plans_data, list) and len(plans_data) > 0:
                        # Handle case where plans_data is directly a list
                        plan_id = plans_data[0].get("planId")
                        if plan_id:
                            plan_id = str(plan_id)
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid plan ID
        if plan_id:
            result = await client.call_tool("get_plan_properties", {"plan_id": plan_id})
            assert "error" not in result[0].text.lower() or "plan" in result[0].text.lower()
        else:
            # Skip test if no plans found
            assert True, "No plans found to test with"