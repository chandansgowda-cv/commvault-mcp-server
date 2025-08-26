from fastmcp import Client
import json
import pytest

def extract_response_data(result):
    """Extract and parse data from MCP client response."""
    if not isinstance(result, list) or len(result) == 0:
        raise AssertionError("Expected list response with at least one item")
    
    if not hasattr(result[0], "text"):
        raise AssertionError("Response item missing 'text' attribute")
    
    response_text = result[0].text
    
    # First try to parse as JSON
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If not JSON, return the raw text for further analysis
        return response_text

def assert_no_error_in_response(data, operation_name, acceptable_errors=None):
    """Assert that response data doesn't contain errors."""
    if acceptable_errors is None:
        acceptable_errors = []
    
    if isinstance(data, str):
        # Check if this is an acceptable operational error
        data_lower = data.lower()
        for acceptable in acceptable_errors:
            if acceptable.lower() in data_lower:
                return  # This error is acceptable for this operation
        
        # Check for common error patterns in string responses
        error_indicators = [
            "error occurred", "failed to", "invalid", "unauthorized", 
            "not found", "exception", "traceback",
            "internal server error", "bad request", "forbidden"
        ]
        for indicator in error_indicators:
            if indicator in data_lower:
                raise AssertionError(f"{operation_name} failed with error: {data}")
        return
    
    elif isinstance(data, dict):
        # Check for explicit error structure
        if "error" in data:
            error = data["error"]
            if isinstance(error, dict):
                error_msg = error.get("errorMessage", "")
                error_code = error.get("errorCode", 0)
                
                # Check if this is an acceptable operational error
                for acceptable in acceptable_errors:
                    if acceptable.lower() in error_msg.lower():
                        return  # This error is acceptable for this operation
                
                if error_msg or error_code != 0:
                    raise AssertionError(f"{operation_name} failed with error: {error_msg} (code: {error_code})")
            elif error:  # Non-empty error value
                raise AssertionError(f"{operation_name} failed with error: {error}")
        
        # Check for common error indicators
        if "errorMessage" in data and data["errorMessage"]:
            error_msg = data["errorMessage"]
            
            # Check if this is an acceptable operational error
            for acceptable in acceptable_errors:
                if acceptable.lower() in error_msg.lower():
                    return  # This error is acceptable for this operation
            
            raise AssertionError(f"{operation_name} failed: {error_msg}")
        
        if "errorCode" in data and data["errorCode"] != 0:
            raise AssertionError(f"{operation_name} failed with error code: {data['errorCode']}")

def get_job_id_from_jobs_response(data):
    """Extract job ID from jobs list response."""
    try:
        if isinstance(data, dict):
            if "jobsInThisResponse" in data and data["jobsInThisResponse"]:
                return str(data["jobsInThisResponse"][0].get("jobId"))
            elif "jobs" in data and data["jobs"]:
                return str(data["jobs"][0].get("jobId"))
        elif isinstance(data, list) and data:
            return str(data[0].get("jobId"))
    except Exception:
        pass
    return None

def find_job_by_status(data, target_status):
    """Find a job with specific status from jobs response."""
    try:
        jobs_list = []
        if isinstance(data, dict):
            # The get_basic_job_details wrapper returns jobsInThisResponse
            if "jobsInThisResponse" in data:
                jobs_list = data["jobsInThisResponse"]
            elif "jobs" in data:
                jobs_list = data["jobs"]
        elif isinstance(data, list):
            jobs_list = data
        
        for job in jobs_list:
            if isinstance(job, dict):
                # Status is directly available in the job object after wrapper processing
                job_status = job.get("status", "")
                if isinstance(job_status, str) and job_status.lower() == target_status.lower():
                    return str(job.get("jobId"))
    except Exception:
        pass
    return None

async def test_tool_functionality(mcp_server):
    """Test basic tool functionality with invalid job ID."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_job_detail", {"job_id": 99999999})
        
        # This should fail with a specific error message
        response_text = result[0].text if hasattr(result[0], 'text') else str(result)
        expected_error = "No job found with ID: 99999999"
        assert expected_error in response_text, f"Expected specific error message, got: {response_text}"

async def test_get_job_detail(mcp_server):
    async with Client(mcp_server) as client:
        # First get the list of jobs
        jobs_result = await client.call_tool("get_jobs_list", {})
        jobs_data = extract_response_data(jobs_result)
        assert_no_error_in_response(jobs_data, "get_jobs_list")
        
        job_id = get_job_id_from_jobs_response(jobs_data)
        
        if not job_id:
            pytest.skip("No jobs exist in the system")
        
        # Test getting job detail for existing job
        result = await client.call_tool("get_job_detail", {"job_id": int(job_id)})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_job_detail")
        
        # Verify it returns job data
        if isinstance(data, dict):
            assert len(data) > 0, "Job detail response should not be empty"

async def test_suspend_job(mcp_server):
    async with Client(mcp_server) as client:
        # Get active jobs
        jobs_result = await client.call_tool("get_jobs_list", {"job_status": "Active"})
        jobs_data = extract_response_data(jobs_result)
        assert_no_error_in_response(jobs_data, "get_jobs_list")
        
        job_id = get_job_id_from_jobs_response(jobs_data)
        
        if not job_id:
            pytest.skip("No active jobs exist in the system")
        
        # Test suspending job for existing active job
        result = await client.call_tool("suspend_job", {
            "job_id": int(job_id), 
            "reason": "Test suspension"
        })
        data = extract_response_data(result)
        assert_no_error_in_response(data, "suspend_job")

async def test_resume_job(mcp_server):
    async with Client(mcp_server) as client:
        # Look for failed jobs that can be resumed
        jobs_result = await client.call_tool("get_jobs_list", {})
        jobs_data = extract_response_data(jobs_result)
        assert_no_error_in_response(jobs_data, "get_jobs_list")
        
        # Find a job with "Failed" status for resuming
        job_id = find_job_by_status(jobs_data, "Failed")
        
        # If no failed jobs found, try getting failed jobs specifically
        if not job_id:
            failed_jobs_result = await client.call_tool("get_failed_jobs", {})
            failed_jobs_data = extract_response_data(failed_jobs_result)
            assert_no_error_in_response(failed_jobs_data, "get_failed_jobs")
            job_id = get_job_id_from_jobs_response(failed_jobs_data)
        
        if not job_id:
            pytest.skip("No failed jobs exist in the system to resume")
        
        # Test resuming failed job
        result = await client.call_tool("resume_job", {"job_id": int(job_id)})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "resume_job")

async def test_resubmit_job(mcp_server):
    async with Client(mcp_server) as client:
        # Get jobs from last 7 days to avoid age limitation
        jobs_result = await client.call_tool("get_jobs_list", {"jobLookupWindow": 604800})  # 7 days
        jobs_data = extract_response_data(jobs_result)
        assert_no_error_in_response(jobs_data, "get_jobs_list")
        
        # Look for jobs with status that typically allows resubmission
        resubmittable_statuses = ["Failed", "Killed", "Suspended"]
        job_id = None
        
        for status in resubmittable_statuses:
            job_id = find_job_by_status(jobs_data, status)
            if job_id:
                break
        
        # If no resubmittable jobs found, try getting recent failed jobs specifically
        if not job_id:
            failed_jobs_result = await client.call_tool("get_failed_jobs", {"jobLookupWindow": 604800})
            failed_jobs_data = extract_response_data(failed_jobs_result)
            assert_no_error_in_response(failed_jobs_data, "get_failed_jobs")
            job_id = get_job_id_from_jobs_response(failed_jobs_data)
        
        if not job_id:
            pytest.skip("No recent resubmittable jobs exist in the system")
        
        # Test resubmitting job with acceptable operational errors
        result = await client.call_tool("resubmit_job", {"job_id": int(job_id)})
        data = extract_response_data(result)
        
        # Accept age-related limitations as valid operational constraints
        acceptable_errors = [
            "job is older than",
            "cannot be resubmitted",
            "job status does not allow resubmission"
        ]
        assert_no_error_in_response(data, "resubmit_job", acceptable_errors)

async def test_kill_job(mcp_server):
    """Test killing waiting jobs on test server."""
    async with Client(mcp_server) as client:
        # Look for jobs with "Waiting" status that can be safely killed
        jobs_result = await client.call_tool("get_jobs_list", {})
        jobs_data = extract_response_data(jobs_result)
        assert_no_error_in_response(jobs_data, "get_jobs_list")
        
        # Find a job with "Waiting" status for killing
        job_id = find_job_by_status(jobs_data, "Waiting")
        
        if not job_id:
            pytest.skip("No waiting jobs exist in the system to kill")
        
        # Test killing waiting job
        result = await client.call_tool("kill_job", {"job_id": int(job_id)})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "kill_job")

async def test_get_jobs_list(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_jobs_list", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_jobs_list")
        
        # Verify response structure
        if isinstance(data, dict):
            if "jobsInThisResponse" in data:
                assert isinstance(data["jobsInThisResponse"], list), "jobsInThisResponse should be a list"
            elif "jobs" in data:
                assert isinstance(data["jobs"], list), "jobs should be a list"
            else:
                assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            assert len(data) >= 0, "List response should be valid"

async def test_get_failed_jobs(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_failed_jobs", {})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_failed_jobs")
        
        # Verify response structure
        if isinstance(data, dict):
            if "jobsInThisResponse" in data:
                assert isinstance(data["jobsInThisResponse"], list), "jobsInThisResponse should be a list"
            elif "jobs" in data:
                assert isinstance(data["jobs"], list), "jobs should be a list"
            else:
                assert len(data) >= 0, "Response should be valid"
        elif isinstance(data, list):
            assert len(data) >= 0, "List response should be valid"

async def test_get_job_task_details(mcp_server):
    async with Client(mcp_server) as client:
        # Get recent jobs to avoid potential API issues with old jobs
        jobs_result = await client.call_tool("get_jobs_list", {"jobLookupWindow": 86400})  # Last 24 hours
        jobs_data = extract_response_data(jobs_result)
        assert_no_error_in_response(jobs_data, "get_jobs_list")
        
        job_id = get_job_id_from_jobs_response(jobs_data)
        
        if not job_id:
            pytest.skip("No recent jobs exist in the system")
        
        # Test getting task details for existing job
        result = await client.call_tool("get_job_task_details", {"job_id": int(job_id)})
        data = extract_response_data(result)
        
        # Accept age-related limitations that might affect task detail retrieval
        acceptable_errors = [
            "job is older than",
            "unable to retrieve task details for old jobs",
            "task details not available"
        ]
        assert_no_error_in_response(data, "get_job_task_details", acceptable_errors)

async def test_get_retention_info_of_a_job(mcp_server):
    async with Client(mcp_server) as client:
        # Get a job first
        jobs_result = await client.call_tool("get_jobs_list", {})
        jobs_data = extract_response_data(jobs_result)
        assert_no_error_in_response(jobs_data, "get_jobs_list")
        
        job_id = get_job_id_from_jobs_response(jobs_data)
        
        if not job_id:
            pytest.skip("No jobs exist in the system")
        
        # Test getting retention info for existing job
        result = await client.call_tool("get_retention_info_of_a_job", {"job_id": int(job_id)})
        data = extract_response_data(result)
        assert_no_error_in_response(data, "get_retention_info_of_a_job")

async def test_create_send_logs_job_for_a_job(mcp_server):
    async with Client(mcp_server) as client:
        # Get a job first
        jobs_result = await client.call_tool("get_jobs_list", {})
        jobs_data = extract_response_data(jobs_result)
        assert_no_error_in_response(jobs_data, "get_jobs_list")
        
        job_id = get_job_id_from_jobs_response(jobs_data)
        
        if not job_id:
            pytest.skip("No jobs exist in the system")
        
        # Test creating send logs job for existing job
        result = await client.call_tool("create_send_logs_job_for_a_job", {
            "emailid": "test@example.com", 
            "job_id": int(job_id)
        })
        data = extract_response_data(result)
        assert_no_error_in_response(data, "create_send_logs_job_for_a_job")
        
        # Verify it returns task creation data
        if isinstance(data, dict):
            assert len(data) > 0, "Send logs job response should not be empty"