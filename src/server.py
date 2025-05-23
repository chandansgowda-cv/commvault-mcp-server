from typing import Annotated
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cv_api_client import CommvaultApiClient
from src.helpers import compute_security_score, transform_sla_data
from src.logger import logger
from src.utils import get_env_var

mcp = FastMCP(name="Commvault MCP Server", instructions="You can use this server to interact with Commvault Product")
commvault_api_client = CommvaultApiClient()


@mcp.tool()
def get_sla_status():
    """
    Retrieves the SLA status from Commvault.
    Returns:
        A dictionary containing information about the SLA status.
    """
    try:
        sla_data = commvault_api_client.get("cr/reportsplusengine/datasets/getslacounts/data?cache=true&parameter.i_dashboardtype=commcell&datasource=2")
        sla_status = transform_sla_data(sla_data)
        return sla_status
    except Exception as e:
        logger.error(f"Error retrieving SLA status: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_security_posture():
    """
    Retrieves the security posture of the Commcell.
    Returns:
        A dictionary containing information about the security posture of the Commcell.
    """
    try:
        security_posture = commvault_api_client.get("Security/Dashboard")
        return security_posture
    except Exception as e:
        logger.error(f"Error retrieving security posture: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_security_score():
    """
    Retrieves the security score of the Commcell.
    Returns:
        A dictionary containing information about the security score of the Commcell.
    """
    try:
        security_posture = commvault_api_client.get("Security/Dashboard")
        security_score = compute_security_score(security_posture)
        response = {
            "security_score": security_score
        }
        return response
    except Exception as e:
        logger.error(f"Error retrieving security score: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_jobs_in_last_24_hours(
    limit: Annotated[int, Field(description="The maximum number of jobs to retrieve. Default is 10. Try to keep it low.")] = 10,
    offset: Annotated[int, Field(description="The number of jobs to skip before starting to retrieve. Default is 0.")] = 0,
):
    """
    Retrieves all jobs in the last 24 hours from Commvault.
    Returns:
        A dictionary containing information about all the jobs in the last 24 hours.
    """
    try:
        jobs = commvault_api_client.get("Job?completedJobLookupTime=86400", headers={"limit": str(limit), "offset": str(offset)})
        return jobs
    except Exception as e:
        logger.error(f"Error retrieving jobs in the last 24 hours: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_active_jobs(
    limit: Annotated[int, Field(description="The maximum number of jobs to retrieve. Default is 10. Try to keep it low.")] = 10,
    offset: Annotated[int, Field(description="The number of jobs to skip before starting to retrieve. Default is 0.")] = 0,
):
    """
    Retrieves all active jobs from Commvault.
    Returns:
        A dictionary containing information about all the active jobs.
    """
    try:
        jobs = commvault_api_client.get("Job?jobCategory=Active", headers={"limit": str(limit), "offset": str(offset)})
        return jobs
    except Exception as e:
        logger.error(f"Error retrieving active jobs: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_job_by_id(job_id: Annotated[int, Field(description="The ID of the job to retrieve.")],):
    """
    Retrieves a specific job from Commvault.

    Returns:
        A dictionary containing information about the specified job.
    """
    try:
        job = commvault_api_client.get(f"Job/{job_id}")
        return job
    except Exception as e:
        logger.error(f"Error retrieving job with ID {job_id}: {e}")
        return ToolError({"error": str(e)})


if __name__ == "__main__":
    mcp_transport_mode = get_env_var("MCP_TRANSPORT_MODE")

    if mcp_transport_mode == "stdio":
        mcp.run(transport=mcp_transport_mode)
    else:
        mcp_host = get_env_var("MCP_HOST")
        mcp_port = get_env_var("MCP_PORT")
        mcp_path = get_env_var("MCP_PATH")
        mcp.run(transport=mcp_transport_mode, host=mcp_host, port=int(mcp_port), path=mcp_path)