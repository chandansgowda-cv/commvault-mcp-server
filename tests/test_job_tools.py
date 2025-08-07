from fastmcp import Client


async def test_tool_functionality(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_job_detail", {"job_id": "99999999"})
        assert "No job found with ID: 99999999" in result[0].text