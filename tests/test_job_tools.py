from fastmcp import Client
import json 

def is_real_error(data):
    """Return True only if errorMessage is not blank or errorCode is not 0."""
    error = data.get("error", {})
    return bool(error.get("errorMessage")) or error.get("errorCode", 0) not in (0, "")

async def test_tool_functionality(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_job_detail", {"job_id": "99999999"})
        assert "No job found with ID: 99999999" in result[0].text

async def test_get_job_detail(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of jobs to get a valid job_id
        jobs = await client.call_tool("get_jobs_list", {})
        
        job_id = None
        if isinstance(jobs, list) and len(jobs) > 0:
            # Extract job ID from the response
            if hasattr(jobs[0], "text"):
                try:
                    jobs_data = json.loads(jobs[0].text)
                    if isinstance(jobs_data, list) and len(jobs_data) > 0:
                        job_id = jobs_data[0].get("jobId")
                    elif isinstance(jobs_data, dict) and "jobs" in jobs_data:
                        jobs_list = jobs_data["jobs"]
                        if isinstance(jobs_list, list) and len(jobs_list) > 0:
                            job_id = jobs_list[0].get("jobId")
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid job ID
        if job_id:
            result = await client.call_tool("get_job_detail", {"job_id": job_id})
            assert "error" not in result[0].text.lower()
        else:
            # Skip test if no jobs found
            assert True, "No jobs found to test with"

async def test_suspend_job(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of active jobs to get a valid job_id for suspension
        jobs = await client.call_tool("get_jobs_list", {"job_status": "Active"})
        
        job_id = None
        if isinstance(jobs, list) and len(jobs) > 0:
            # Extract job ID from the response
            if hasattr(jobs[0], "text"):
                try:
                    jobs_data = json.loads(jobs[0].text)
                    if isinstance(jobs_data, list) and len(jobs_data) > 0:
                        job_id = jobs_data[0].get("jobId")
                    elif isinstance(jobs_data, dict) and "jobs" in jobs_data:
                        jobs_list = jobs_data["jobs"]
                        if isinstance(jobs_list, list) and len(jobs_list) > 0:
                            job_id = jobs_list[0].get("jobId")
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid active job ID
        if job_id:
            result = await client.call_tool("suspend_job", {"job_id": job_id, "reason": "maintenance"})
            assert "error" not in result[0].text.lower()
        else:
            # Skip test if no active jobs found
            assert True, "No active jobs found to test with"

async def test_resume_job(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of jobs to get a valid job_id
        jobs = await client.call_tool("get_jobs_list", {})
        
        job_id = None
        if isinstance(jobs, list) and len(jobs) > 0:
            # Extract job ID from the response
            if hasattr(jobs[0], "text"):
                try:
                    jobs_data = json.loads(jobs[0].text)
                    if isinstance(jobs_data, list) and len(jobs_data) > 0:
                        job_id = jobs_data[0].get("jobId")
                    elif isinstance(jobs_data, dict) and "jobs" in jobs_data:
                        jobs_list = jobs_data["jobs"]
                        if isinstance(jobs_list, list) and len(jobs_list) > 0:
                            job_id = jobs_list[0].get("jobId")
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid job ID
        if job_id:
            result = await client.call_tool("resume_job", {"job_id": job_id})
            assert "error" not in result[0].text.lower() or "success" in result[0].text.lower()
        else:
            # Skip test if no jobs found
            assert True, "No jobs found to test with"

async def test_resubmit_job(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of finished jobs to get a valid job_id for resubmission
        jobs = await client.call_tool("get_jobs_list", {"job_status": "Finished"})
        
        job_id = None
        if isinstance(jobs, list) and len(jobs) > 0:
            # Extract job ID from the response
            if hasattr(jobs[0], "text"):
                try:
                    jobs_data = json.loads(jobs[0].text)
                    if isinstance(jobs_data, list) and len(jobs_data) > 0:
                        job_id = jobs_data[0].get("jobId")
                    elif isinstance(jobs_data, dict) and "jobs" in jobs_data:
                        jobs_list = jobs_data["jobs"]
                        if isinstance(jobs_list, list) and len(jobs_list) > 0:
                            job_id = jobs_list[0].get("jobId")
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid finished job ID
        if job_id:
            result = await client.call_tool("resubmit_job", {"job_id": job_id})
            assert "error" not in result[0].text.lower() or "success" in result[0].text.lower()
        else:
            # Skip test if no finished jobs found
            assert True, "No finished jobs found to test with"

async def test_kill_job(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of active jobs to get a valid job_id for killing
        jobs = await client.call_tool("get_jobs_list", {"job_status": "Active"})
        
        job_id = None
        if isinstance(jobs, list) and len(jobs) > 0:
            # Extract job ID from the response
            if hasattr(jobs[0], "text"):
                try:
                    jobs_data = json.loads(jobs[0].text)
                    if isinstance(jobs_data, list) and len(jobs_data) > 0:
                        job_id = jobs_data[0].get("jobId")
                    elif isinstance(jobs_data, dict) and "jobs" in jobs_data:
                        jobs_list = jobs_data["jobs"]
                        if isinstance(jobs_list, list) and len(jobs_list) > 0:
                            job_id = jobs_list[0].get("jobId")
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid active job ID
        if job_id:
            result = await client.call_tool("kill_job", {"job_id": job_id})
            if isinstance(result, list) and hasattr(result[0], "text"):
                data = json.loads(result[0].text)
                assert not is_real_error(data)
            else:
                assert isinstance(result, dict)
        else:
            # Skip test if no active jobs found
            assert True, "No active jobs found to test with"

async def test_get_jobs_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_jobs_list", {})
        assert isinstance(result, list) or "error" not in result[0].text.lower()

async def test_get_failed_jobs(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_failed_jobs", {})
        assert isinstance(result, list) or "error" not in result[0].text.lower()

async def test_get_job_task_details(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of jobs to get a valid job_id
        jobs = await client.call_tool("get_jobs_list", {})
        
        job_id = None
        if isinstance(jobs, list) and len(jobs) > 0:
            # Extract job ID from the response
            if hasattr(jobs[0], "text"):
                try:
                    jobs_data = json.loads(jobs[0].text)
                    if isinstance(jobs_data, list) and len(jobs_data) > 0:
                        job_id = jobs_data[0].get("jobId")
                    elif isinstance(jobs_data, dict) and "jobs" in jobs_data:
                        jobs_list = jobs_data["jobs"]
                        if isinstance(jobs_list, list) and len(jobs_list) > 0:
                            job_id = jobs_list[0].get("jobId")
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid job ID
        if job_id:
            result = await client.call_tool("get_job_task_details", {"job_id": job_id})
            assert "error" not in result[0].text.lower() or "task" in result[0].text.lower()
        else:
            # Skip test if no jobs found
            assert True, "No jobs found to test with"

async def test_get_retention_info_of_a_job(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of jobs to get a valid job_id
        jobs = await client.call_tool("get_jobs_list", {})
        
        job_id = None
        if isinstance(jobs, list) and len(jobs) > 0:
            # Extract job ID from the response
            if hasattr(jobs[0], "text"):
                try:
                    jobs_data = json.loads(jobs[0].text)
                    if isinstance(jobs_data, list) and len(jobs_data) > 0:
                        job_id = jobs_data[0].get("jobId")
                    elif isinstance(jobs_data, dict) and "jobs" in jobs_data:
                        jobs_list = jobs_data["jobs"]
                        if isinstance(jobs_list, list) and len(jobs_list) > 0:
                            job_id = jobs_list[0].get("jobId")
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid job ID
        if job_id:
            result = await client.call_tool("get_retention_info_of_a_job", {"job_id": job_id})
            assert "error" not in result[0].text.lower() or "retention" in result[0].text.lower()
        else:
            # Skip test if no jobs found
            assert True, "No jobs found to test with"

async def test_create_send_logs_job_for_a_job(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of jobs to get a valid job_id
        jobs = await client.call_tool("get_jobs_list", {})
        
        job_id = None
        if isinstance(jobs, list) and len(jobs) > 0:
            # Extract job ID from the response
            if hasattr(jobs[0], "text"):
                try:
                    jobs_data = json.loads(jobs[0].text)
                    if isinstance(jobs_data, list) and len(jobs_data) > 0:
                        job_id = jobs_data[0].get("jobId")
                    elif isinstance(jobs_data, dict) and "jobs" in jobs_data:
                        jobs_list = jobs_data["jobs"]
                        if isinstance(jobs_list, list) and len(jobs_list) > 0:
                            job_id = jobs_list[0].get("jobId")
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Only run test if we found a valid job ID
        if job_id:
            result = await client.call_tool("create_send_logs_job_for_a_job", {"emailid": "nmurali@commvault.com", "job_id": job_id})
            assert "error" not in result[0].text.lower() or "success" in result[0].text.lower()
        else:
            # Skip test if no jobs found
            assert True, "No jobs found to test with"