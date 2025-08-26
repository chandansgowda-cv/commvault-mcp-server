# test_additional_integration_workflows.py
"""
Additional integration tests for tool combinations.
"""
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

def safe_extract_id(response, id_field):
    """Safely extract ID from API response with comprehensive error handling."""
    try:
        data = extract_response_data(response)
        
        # Handle direct list
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            if isinstance(first_item, dict) and id_field in first_item:
                value = first_item[id_field]
                return str(value) if value is not None else None
        
        # Handle nested object structures
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    first_item = value[0]
                    if isinstance(first_item, dict) and id_field in first_item:
                        id_value = first_item[id_field]
                        return str(id_value) if id_value is not None else None
                
                # Check if the key itself matches
                if key == id_field and value is not None:
                    return str(value)
    except Exception:
        return None
    
    return None

def safe_extract_ids(response, id_field, max_count=2):
    """Safely extract multiple IDs from API response."""
    try:
        data = extract_response_data(response)
        ids = []
        
        # Handle direct list
        if isinstance(data, list):
            for item in data[:max_count]:
                if isinstance(item, dict) and id_field in item:
                    value = item[id_field]
                    if value is not None:
                        ids.append(str(value))
        
        # Handle nested object structures
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    for item in value[:max_count]:
                        if isinstance(item, dict) and id_field in item:
                            id_value = item[id_field]
                            if id_value is not None:
                                ids.append(str(id_value))
                    break
        
        return ids
    
    except Exception:
        return []

class TestComprehensiveDataAnalysisWorkflows:
    """Test comprehensive data analysis workflows across multiple tool categories."""
    
    async def test_complete_environment_assessment_workflow(self, mcp_server):
        """Test workflow: complete environment assessment using all available tools."""
        async with Client(mcp_server) as client:
            # Step 1: CommCell Infrastructure Assessment
            commcell_details = await client.call_tool("get_commcell_details", {})
            commcell_data = extract_response_data(commcell_details)
            assert_no_error_in_response(commcell_data, "get_commcell_details")
            
            # Step 2: Client Infrastructure Analysis
            all_clients = await client.call_tool("get_client_list", {})
            all_clients_data = extract_response_data(all_clients)
            assert_no_error_in_response(all_clients_data, "get_client_list")
            
            client_groups = await client.call_tool("get_client_group_list", {})
            client_groups_data = extract_response_data(client_groups)
            assert_no_error_in_response(client_groups_data, "get_client_group_list")
            
            # Step 3: Storage Infrastructure Analysis
            storage_policies = await client.call_tool("get_storage_policy_list", {})
            storage_policies_data = extract_response_data(storage_policies)
            assert_no_error_in_response(storage_policies_data, "get_storage_policy_list")
            
            storage_pools = await client.call_tool("get_storage_pool_list", {})
            storage_pools_data = extract_response_data(storage_pools)
            assert_no_error_in_response(storage_pools_data, "get_storage_pool_list")
            
            media_agents = await client.call_tool("get_mediaagent_list", {})
            media_agents_data = extract_response_data(media_agents)
            assert_no_error_in_response(media_agents_data, "get_mediaagent_list")
            
            # Step 4: Job Performance Analysis
            recent_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 86400,
                "limit": 50
            })
            recent_jobs_data = extract_response_data(recent_jobs)
            assert_no_error_in_response(recent_jobs_data, "get_jobs_list")
            
            failed_jobs = await client.call_tool("get_failed_jobs", {
                "jobLookupWindow": 86400,
                "limit": 25
            })
            failed_jobs_data = extract_response_data(failed_jobs)
            assert_no_error_in_response(failed_jobs_data, "get_failed_jobs")
            
            # Step 5: Security and User Analysis
            users_list = await client.call_tool("get_users_list", {})
            users_data = extract_response_data(users_list)
            assert_no_error_in_response(users_data, "get_users_list")
            
            security_posture = await client.call_tool("get_security_posture", {})
            security_data = extract_response_data(security_posture)
            assert_no_error_in_response(security_data, "get_security_posture")

    async def test_client_subclient_job_correlation_workflow(self, mcp_server):
        """Test workflow: correlate clients, subclients, and their job performance."""
        async with Client(mcp_server) as client:
            # Step 1: Get client infrastructure
            all_clients = await client.call_tool("get_client_list", {})
            all_clients_data = extract_response_data(all_clients)
            assert_no_error_in_response(all_clients_data, "get_client_list")
            
            # Extract client IDs dynamically
            client_ids = safe_extract_ids(all_clients, "clientId", 2)
            
            # Step 2: Analyze specific clients and their subclients
            client_analysis = {}
            for client_id in client_ids:
                # Get client subclients
                subclients = await client.call_tool("get_subclient_list", {
                    "client_identifier": client_id,
                    "identifier_type": "id"
                })
                subclients_data = extract_response_data(subclients)
                assert_no_error_in_response(subclients_data, "get_subclient_list")
                
                # Get jobs for this client
                client_jobs = await client.call_tool("get_jobs_list", {
                    "client_id": client_id,
                    "jobLookupWindow": 86400,
                    "limit": 25
                })
                client_jobs_data = extract_response_data(client_jobs)
                assert_no_error_in_response(client_jobs_data, "get_jobs_list")
                
                # Get detailed subclient properties
                subclient_id = safe_extract_id(subclients, "subClientId")
                
                if subclient_id:
                    subclient_props = await client.call_tool("get_subclient_properties", {
                        "subclient_id": subclient_id
                    })
                    subclient_props_data = extract_response_data(subclient_props)
                    assert_no_error_in_response(subclient_props_data, "get_subclient_properties")
                    
                    client_analysis[client_id] = {
                        'subclients': subclients,
                        'jobs': client_jobs,
                        'subclient_props': subclient_props
                    }
            
            # Step 3: Compare performance across clients
            backup_jobs_all = await client.call_tool("get_jobs_list", {
                "job_filter": "Backup",
                "jobLookupWindow": 86400,
                "limit": 50
            })
            backup_jobs_data = extract_response_data(backup_jobs_all)
            assert_no_error_in_response(backup_jobs_data, "get_jobs_list")

    async def test_storage_policy_utilization_workflow(self, mcp_server):
        """Test workflow: analyze storage policy utilization and performance."""
        async with Client(mcp_server) as client:
            # Step 1: Get all storage policies
            storage_policies = await client.call_tool("get_storage_policy_list", {})
            storage_policies_data = extract_response_data(storage_policies)
            assert_no_error_in_response(storage_policies_data, "get_storage_policy_list")
            
            # Extract policy IDs dynamically
            policy_ids = safe_extract_ids(storage_policies, "storagePolicyId", 3)
            
            # Step 2: Analyze specific storage policies
            policy_analysis = {}
            for policy_id in policy_ids:
                # Get policy properties
                policy_props = await client.call_tool("get_storage_policy_properties", {
                    "storage_policy_id": policy_id
                })
                policy_props_data = extract_response_data(policy_props)
                assert_no_error_in_response(policy_props_data, "get_storage_policy_properties")
                
                # Get copy details if available
                if isinstance(policy_props_data, dict) and "storagePolicyCopyInfo" in policy_props_data:
                    copies = policy_props_data["storagePolicyCopyInfo"]
                    if isinstance(copies, list) and len(copies) > 0:
                        copy_id = str(copies[0].get("copyId"))
                        if copy_id:
                            copy_details = await client.call_tool("get_storage_policy_copy_details", {
                                "storage_policy_id": policy_id,
                                "copy_id": copy_id
                            })
                            copy_details_data = extract_response_data(copy_details)
                            assert_no_error_in_response(copy_details_data, "get_storage_policy_copy_details")
                            
                            policy_analysis[policy_id] = {
                                'properties': policy_props,
                                'copy_details': copy_details
                            }
            
            # Step 3: Correlate with storage utilization
            storage_util = await client.call_tool("get_storage_space_utilization", {})
            storage_util_data = extract_response_data(storage_util)
            assert_no_error_in_response(storage_util_data, "get_storage_space_utilization")
            
            # Step 4: Check related infrastructure
            storage_pools = await client.call_tool("get_storage_pool_list", {})
            storage_pools_data = extract_response_data(storage_pools)
            assert_no_error_in_response(storage_pools_data, "get_storage_pool_list")
            
            media_agents = await client.call_tool("get_mediaagent_list", {})
            media_agents_data = extract_response_data(media_agents)
            assert_no_error_in_response(media_agents_data, "get_mediaagent_list")

class TestJobTrendAnalysisWorkflows:
    """Test job trend analysis workflows with different time windows and filters."""
    
    async def test_job_trend_analysis_workflow(self, mcp_server):
        """Test workflow: analyze job trends across different time periods."""
        async with Client(mcp_server) as client:
            # Step 1: Short-term analysis (last hour)
            recent_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 3600,  # 1 hour
                "limit": 30
            })
            recent_jobs_data = extract_response_data(recent_jobs)
            assert_no_error_in_response(recent_jobs_data, "get_jobs_list")
            
            # Step 2: Medium-term analysis (last day)
            daily_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 86400,  # 24 hours
                "limit": 100
            })
            daily_jobs_data = extract_response_data(daily_jobs)
            assert_no_error_in_response(daily_jobs_data, "get_jobs_list")
            
            # Step 3: Long-term analysis (last week)
            weekly_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 604800,  # 1 week
                "limit": 200
            })
            weekly_jobs_data = extract_response_data(weekly_jobs)
            assert_no_error_in_response(weekly_jobs_data, "get_jobs_list")
            
            # Step 4: Failure trend analysis
            daily_failures = await client.call_tool("get_failed_jobs", {
                "jobLookupWindow": 86400,
                "limit": 25
            })
            daily_failures_data = extract_response_data(daily_failures)
            assert_no_error_in_response(daily_failures_data, "get_failed_jobs")
            
            weekly_failures = await client.call_tool("get_failed_jobs", {
                "jobLookupWindow": 604800,
                "limit": 75
            })
            weekly_failures_data = extract_response_data(weekly_failures)
            assert_no_error_in_response(weekly_failures_data, "get_failed_jobs")

    async def test_job_type_distribution_workflow(self, mcp_server):
        """Test workflow: analyze distribution of different job types."""
        async with Client(mcp_server) as client:
            job_types = [
                "Backup", "Restore", "AUXCOPY", "MEDIAINIT", 
                "SEND_LOGFILE", "CATALOG_MIGRATION", "Online"
            ]
            
            job_type_analysis = {}
            for job_type in job_types:
                # Get jobs for each type
                type_jobs = await client.call_tool("get_jobs_list", {
                    "job_filter": job_type,
                    "jobLookupWindow": 86400,
                    "limit": 25
                })
                type_jobs_data = extract_response_data(type_jobs)
                assert_no_error_in_response(type_jobs_data, "get_jobs_list")
                
                job_type_analysis[job_type] = type_jobs
            
            # Compare with overall job distribution
            all_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 86400,
                "limit": 100
            })
            all_jobs_data = extract_response_data(all_jobs)
            assert_no_error_in_response(all_jobs_data, "get_jobs_list")

    async def test_client_performance_comparison_workflow(self, mcp_server):
        """Test workflow: compare job performance across different clients."""
        async with Client(mcp_server) as client:
            # Get available clients first
            clients = await client.call_tool("get_client_list", {})
            clients_to_analyze = safe_extract_ids(clients, "clientId", 2)
            
            client_performance = {}
            
            for client_id in clients_to_analyze:
                # Get all jobs for client
                all_client_jobs = await client.call_tool("get_jobs_list", {
                    "client_id": client_id,
                    "jobLookupWindow": 86400,
                    "limit": 30
                })
                all_client_jobs_data = extract_response_data(all_client_jobs)
                assert_no_error_in_response(all_client_jobs_data, "get_jobs_list")
                
                # Get backup jobs specifically
                backup_jobs = await client.call_tool("get_jobs_list", {
                    "client_id": client_id,
                    "job_filter": "Backup",
                    "jobLookupWindow": 86400,
                    "limit": 20
                })
                backup_jobs_data = extract_response_data(backup_jobs)
                assert_no_error_in_response(backup_jobs_data, "get_jobs_list")
                
                # Get client details
                client_subclients = await client.call_tool("get_subclient_list", {
                    "client_identifier": client_id,
                    "identifier_type": "id"
                })
                client_subclients_data = extract_response_data(client_subclients)
                assert_no_error_in_response(client_subclients_data, "get_subclient_list")
                
                client_performance[client_id] = {
                    'all_jobs': all_client_jobs,
                    'backup_jobs': backup_jobs,
                    'subclients': client_subclients
                }

class TestSecurityComplianceWorkflows:
    """Test security compliance and audit workflows."""
    
    async def test_security_audit_workflow(self, mcp_server):
        """Test workflow: comprehensive security audit across all components."""
        async with Client(mcp_server) as client:
            # Step 1: Overall security assessment
            security_posture = await client.call_tool("get_security_posture", {})
            security_posture_data = extract_response_data(security_posture)
            assert_no_error_in_response(security_posture_data, "get_security_posture")
            
            security_score = await client.call_tool("get_security_score", {})
            security_score_data = extract_response_data(security_score)
            assert_no_error_in_response(security_score_data, "get_security_score")
            
            # Step 2: User access audit
            all_users = await client.call_tool("get_users_list", {})
            all_users_data = extract_response_data(all_users)
            assert_no_error_in_response(all_users_data, "get_users_list")
            
            user_groups = await client.call_tool("get_user_groups_list", {})
            user_groups_data = extract_response_data(user_groups)
            assert_no_error_in_response(user_groups_data, "get_user_groups_list")
            
            # Step 3: Role and permission analysis
            roles_list = await client.call_tool("get_roles_list", {})
            roles_data = extract_response_data(roles_list)
            assert_no_error_in_response(roles_data, "get_roles_list")
            
            # Step 4: Entity permission audit with dynamic IDs
            clients = await client.call_tool("get_client_list", {})
            storage_policies = await client.call_tool("get_storage_policy_list", {})
            
            client_id = safe_extract_id(clients, "clientId")
            storage_policy_id = safe_extract_id(storage_policies, "storagePolicyId")
            
            critical_entities = [
                ("CLIENT_ENTITY", client_id),
                ("COMMCELL_ENTITY", "1"),
                ("STORAGE_POLICY_ENTITY", storage_policy_id)
            ]
            
            for entity_type, entity_id in critical_entities:
                if entity_id:
                    entity_perms = await client.call_tool("view_entity_permissions", {
                        "entity_type": entity_type,
                        "entity_id": entity_id
                    })
                    entity_perms_data = extract_response_data(entity_perms)
                    assert_no_error_in_response(entity_perms_data, "view_entity_permissions")

    async def test_user_access_review_workflow(self, mcp_server):
        """Test workflow: comprehensive user access review."""
        async with Client(mcp_server) as client:
            # Step 1: Get all users and groups
            all_users = await client.call_tool("get_users_list", {})
            all_users_data = extract_response_data(all_users)
            assert_no_error_in_response(all_users_data, "get_users_list")
            
            all_groups = await client.call_tool("get_user_groups_list", {})
            all_groups_data = extract_response_data(all_groups)
            assert_no_error_in_response(all_groups_data, "get_user_groups_list")
            
            # Step 2: Detailed analysis of key users
            key_users = safe_extract_ids(all_users, "userId", 4)
            user_analysis = {}
            
            for user_id in key_users:
                # Get user properties
                user_props = await client.call_tool("get_user_properties", {"user_id": user_id})
                user_props_data = extract_response_data(user_props)
                assert_no_error_in_response(user_props_data, "get_user_properties")
                
                # Get user associations
                user_entities = await client.call_tool("get_associated_entities_for_user_or_user_group", {
                    "id": user_id,
                    "type": "user"
                })
                user_entities_data = extract_response_data(user_entities)
                assert_no_error_in_response(user_entities_data, "get_associated_entities_for_user_or_user_group")
                
                user_analysis[user_id] = {
                    'properties': user_props,
                    'entities': user_entities
                }
            
            # Step 3: Group analysis
            key_groups = safe_extract_ids(all_groups, "userGroupId", 2)
            for group_id in key_groups:
                group_props = await client.call_tool("get_user_group_properties", {"user_group_id": group_id})
                group_props_data = extract_response_data(group_props)
                assert_no_error_in_response(group_props_data, "get_user_group_properties")
                
                group_entities = await client.call_tool("get_associated_entities_for_user_or_user_group", {
                    "id": group_id,
                    "type": "usergroup"
                })
                group_entities_data = extract_response_data(group_entities)
                assert_no_error_in_response(group_entities_data, "get_associated_entities_for_user_or_user_group")

class TestOperationalWorkflows:
    """Test operational workflows combining multiple tool categories."""
    
    async def test_daily_operations_checkup_workflow(self, mcp_server):
        """Test workflow: daily operations health checkup."""
        async with Client(mcp_server) as client:
            # Step 1: Overall system health
            sla_status = await client.call_tool("get_sla_status", {})
            sla_data = extract_response_data(sla_status)
            assert_no_error_in_response(sla_data, "get_sla_status")
            
            storage_util = await client.call_tool("get_storage_space_utilization", {})
            storage_util_data = extract_response_data(storage_util)
            assert_no_error_in_response(storage_util_data, "get_storage_space_utilization")
            
            # Step 2: Job performance check
            last_24h_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 86400,
                "limit": 50
            })
            last_24h_jobs_data = extract_response_data(last_24h_jobs)
            assert_no_error_in_response(last_24h_jobs_data, "get_jobs_list")
            
            failed_jobs = await client.call_tool("get_failed_jobs", {
                "jobLookupWindow": 86400,
                "limit": 20
            })
            failed_jobs_data = extract_response_data(failed_jobs)
            assert_no_error_in_response(failed_jobs_data, "get_failed_jobs")
            
            # Step 3: Infrastructure check
            all_clients = await client.call_tool("get_client_list", {})
            all_clients_data = extract_response_data(all_clients)
            assert_no_error_in_response(all_clients_data, "get_client_list")
            
            schedules_list = await client.call_tool("get_schedules_list", {})
            schedules_data = extract_response_data(schedules_list)
            assert_no_error_in_response(schedules_data, "get_schedules_list")
            
            # Step 4: Plans and policies check
            plans_list = await client.call_tool("get_plan_list", {})
            plans_data = extract_response_data(plans_list)
            assert_no_error_in_response(plans_data, "get_plan_list")
            
            storage_policies = await client.call_tool("get_storage_policy_list", {})
            storage_policies_data = extract_response_data(storage_policies)
            assert_no_error_in_response(storage_policies_data, "get_storage_policy_list")

    async def test_incident_response_workflow(self, mcp_server):
        """Test workflow: incident response and investigation."""
        async with Client(mcp_server) as client:
            # Step 1: Identify issues
            failed_jobs = await client.call_tool("get_failed_jobs", {
                "jobLookupWindow": 86400,
                "limit": 30
            })
            failed_jobs_data = extract_response_data(failed_jobs)
            assert_no_error_in_response(failed_jobs_data, "get_failed_jobs")
            
            # Step 2: Investigate specific incidents using dynamic job IDs
            incident_jobs = safe_extract_ids(failed_jobs, "jobId", 2)
            
            # If no failed jobs, get some regular jobs
            if not incident_jobs:
                all_jobs = await client.call_tool("get_jobs_list", {"limit": 2})
                incident_jobs = safe_extract_ids(all_jobs, "jobId", 2)
            
            for job_id in incident_jobs:
                if job_id:
                    # Get comprehensive job information
                    job_details = await client.call_tool("get_job_detail", {"job_id": job_id})
                    job_details_data = extract_response_data(job_details)
                    assert_no_error_in_response(job_details_data, "get_job_detail")
                    
                    task_details = await client.call_tool("get_job_task_details", {"job_id": job_id})
                    task_details_data = extract_response_data(task_details)
                    acceptable_errors = ["job is older than", "task details not available"]
                    assert_no_error_in_response(task_details_data, "get_job_task_details", acceptable_errors)
                    
                    retention_info = await client.call_tool("get_retention_info_of_a_job", {"job_id": job_id})
                    retention_info_data = extract_response_data(retention_info)
                    assert_no_error_in_response(retention_info_data, "get_retention_info_of_a_job")
                    
                    # Generate logs for investigation
                    send_logs = await client.call_tool("create_send_logs_job_for_a_job", {
                        "emailid": "incident@test.com",
                        "job_id": job_id
                    })
                    send_logs_data = extract_response_data(send_logs)
                    assert_no_error_in_response(send_logs_data, "create_send_logs_job_for_a_job")
            
            # Step 3: Check related infrastructure with dynamic subclient ID
            clients = await client.call_tool("get_client_list", {})
            client_id = safe_extract_id(clients, "clientId")
            
            if client_id:
                subclients = await client.call_tool("get_subclient_list", {
                    "client_identifier": client_id,
                    "identifier_type": "id"
                })
                subclient_id = safe_extract_id(subclients, "subClientId")
                
                if subclient_id:
                    subclient_props = await client.call_tool("get_subclient_properties", {"subclient_id": subclient_id})
                    subclient_props_data = extract_response_data(subclient_props)
                    assert_no_error_in_response(subclient_props_data, "get_subclient_properties")
            
            # Step 4: Generate comprehensive logs using dynamic CommCell name
            commcell_details = await client.call_tool("get_commcell_details", {})
            commcell_name = safe_extract_id(commcell_details, "commCellName")
            
            if not commcell_name:
                commcell_name = safe_extract_id(clients, "clientName")
            
            if commcell_name:
                commcell_logs = await client.call_tool("create_send_logs_job_for_commcell", {
                    "emailid": "incident@test.com",
                    "commcell_name": commcell_name
                })
                commcell_logs_data = extract_response_data(commcell_logs)
                assert_no_error_in_response(commcell_logs_data, "create_send_logs_job_for_commcell")

class TestReportingWorkflows:
    """Test comprehensive reporting workflows."""
    
    async def test_executive_dashboard_workflow(self, mcp_server):
        """Test workflow: generate executive dashboard data."""
        async with Client(mcp_server) as client:
            # Step 1: High-level metrics
            commcell_details = await client.call_tool("get_commcell_details", {})
            commcell_data = extract_response_data(commcell_details)
            assert_no_error_in_response(commcell_data, "get_commcell_details")
            
            sla_status = await client.call_tool("get_sla_status", {})
            sla_data = extract_response_data(sla_status)
            assert_no_error_in_response(sla_data, "get_sla_status")
            
            security_score = await client.call_tool("get_security_score", {})
            security_score_data = extract_response_data(security_score)
            assert_no_error_in_response(security_score_data, "get_security_score")
            
            # Step 2: Infrastructure overview
            client_count = await client.call_tool("get_client_list", {})
            client_count_data = extract_response_data(client_count)
            assert_no_error_in_response(client_count_data, "get_client_list")
            
            storage_overview = await client.call_tool("get_storage_space_utilization", {})
            storage_overview_data = extract_response_data(storage_overview)
            assert_no_error_in_response(storage_overview_data, "get_storage_space_utilization")
            
            # Step 3: Operational metrics
            weekly_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 604800,  # 1 week
                "limit": 200
            })
            weekly_jobs_data = extract_response_data(weekly_jobs)
            assert_no_error_in_response(weekly_jobs_data, "get_jobs_list")
            
            weekly_failures = await client.call_tool("get_failed_jobs", {
                "jobLookupWindow": 604800,
                "limit": 100
            })
            weekly_failures_data = extract_response_data(weekly_failures)
            assert_no_error_in_response(weekly_failures_data, "get_failed_jobs")

    async def test_technical_report_workflow(self, mcp_server):
        """Test workflow: generate detailed technical report."""
        async with Client(mcp_server) as client:
            # Step 1: Infrastructure details
            all_clients = await client.call_tool("get_client_list", {})
            client_groups = await client.call_tool("get_client_group_list", {})
            storage_policies = await client.call_tool("get_storage_policy_list", {})
            storage_pools = await client.call_tool("get_storage_pool_list", {})
            media_agents = await client.call_tool("get_mediaagent_list", {})
            
            # Step 2: Detailed analysis using dynamic IDs
            client_ids = safe_extract_ids(all_clients, "clientId", 2)
            for client_id in client_ids:
                subclients = await client.call_tool("get_subclient_list", {
                    "client_identifier": client_id,
                    "identifier_type": "id"
                })
                client_jobs = await client.call_tool("get_jobs_list", {
                    "client_id": client_id,
                    "jobLookupWindow": 604800,
                    "limit": 50
                })
            
            # Step 3: Storage analysis using dynamic policy IDs
            policy_ids = safe_extract_ids(storage_policies, "storagePolicyId", 2)
            for policy_id in policy_ids:
                policy_props = await client.call_tool("get_storage_policy_properties", {
                    "storage_policy_id": policy_id
                })
                policy_props_data = extract_response_data(policy_props)
                assert_no_error_in_response(policy_props_data, "get_storage_policy_properties")
                
                # Get copy details if available
                if isinstance(policy_props_data, dict) and "storagePolicyCopyInfo" in policy_props_data:
                    copies = policy_props_data["storagePolicyCopyInfo"]
                    if isinstance(copies, list) and len(copies) > 0:
                        copy_id = str(copies[0].get("copyId"))
                        if copy_id:
                            copy_details = await client.call_tool("get_storage_policy_copy_details", {
                                "storage_policy_id": policy_id,
                                "copy_id": copy_id
                            })
                            copy_details_data = extract_response_data(copy_details)
                            assert_no_error_in_response(copy_details_data, "get_storage_policy_copy_details")
            
            # Step 4: User and security analysis
            users_list = await client.call_tool("get_users_list", {})
            user_groups = await client.call_tool("get_user_groups_list", {})
            roles_list = await client.call_tool("get_roles_list", {})
            security_posture = await client.call_tool("get_security_posture", {})

class TestDataCorrelationWorkflows:
    """Test workflows that correlate data across multiple tool categories."""
    
    async def test_backup_to_storage_correlation_workflow(self, mcp_server):
        """Test workflow: correlate backup jobs with storage utilization."""
        async with Client(mcp_server) as client:
            # Step 1: Get backup job data
            backup_jobs = await client.call_tool("get_jobs_list", {
                "job_filter": "Backup",
                "jobLookupWindow": 604800,  # 1 week
                "limit": 100
            })
            backup_jobs_data = extract_response_data(backup_jobs)
            assert_no_error_in_response(backup_jobs_data, "get_jobs_list")
            
            # Step 2: Get storage utilization
            storage_util = await client.call_tool("get_storage_space_utilization", {})
            storage_util_data = extract_response_data(storage_util)
            assert_no_error_in_response(storage_util_data, "get_storage_space_utilization")
            
            # Step 3: Analyze storage policies used
            storage_policies = await client.call_tool("get_storage_policy_list", {})
            storage_policies_data = extract_response_data(storage_policies)
            assert_no_error_in_response(storage_policies_data, "get_storage_policy_list")
            
            # Step 4: Check storage infrastructure
            storage_pools = await client.call_tool("get_storage_pool_list", {})
            storage_pools_data = extract_response_data(storage_pools)
            assert_no_error_in_response(storage_pools_data, "get_storage_pool_list")
            
            media_agents = await client.call_tool("get_mediaagent_list", {})
            media_agents_data = extract_response_data(media_agents)
            assert_no_error_in_response(media_agents_data, "get_mediaagent_list")

    async def test_user_activity_correlation_workflow(self, mcp_server):
        """Test workflow: correlate user activities with system operations."""
        async with Client(mcp_server) as client:
            # Step 1: Get user information
            all_users = await client.call_tool("get_users_list", {})
            all_users_data = extract_response_data(all_users)
            assert_no_error_in_response(all_users_data, "get_users_list")
            
            # Step 2: Analyze user permissions and access using dynamic user IDs
            user_ids = safe_extract_ids(all_users, "userId", 2)
            for user_id in user_ids:
                user_props = await client.call_tool("get_user_properties", {"user_id": user_id})
                user_props_data = extract_response_data(user_props)
                assert_no_error_in_response(user_props_data, "get_user_properties")
                
                user_entities = await client.call_tool("get_associated_entities_for_user_or_user_group", {
                    "id": user_id,
                    "type": "user"
                })
                user_entities_data = extract_response_data(user_entities)
                assert_no_error_in_response(user_entities_data, "get_associated_entities_for_user_or_user_group")
            
            # Step 3: Check recent system activities
            recent_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 86400,
                "limit": 50
            })
            recent_jobs_data = extract_response_data(recent_jobs)
            assert_no_error_in_response(recent_jobs_data, "get_jobs_list")
            
            # Step 4: Look for logs and administrative activities
            admin_jobs = await client.call_tool("get_jobs_list", {
                "job_filter": "SEND_LOGFILE",
                "jobLookupWindow": 86400,
                "limit": 20
            })
            admin_jobs_data = extract_response_data(admin_jobs)
            assert_no_error_in_response(admin_jobs_data, "get_jobs_list")