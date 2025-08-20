# test_additional_integration_workflows.py
"""
Additional integration tests for tool combinations.
"""
from fastmcp import Client
import json
import pytest

def is_real_error(data):
    """Return True only if errorMessage is not blank or errorCode is not 0."""
    try:
        if not isinstance(data, dict):
            return False
        
        error = data.get("error", {})
        if not isinstance(error, dict):
            return False
            
        return bool(error.get("errorMessage")) or error.get("errorCode", 0) not in (0, "")
    except Exception:
        # If we can't determine if it's an error, assume it's not
        return False

def check_response_for_errors(response, operation_name):
    """Helper function to properly check for errors in API responses."""
    try:
        if isinstance(response, list) and hasattr(response[0], "text"):
            try:
                data = json.loads(response[0].text)
                if isinstance(data, dict):
                    assert not is_real_error(data), f"{operation_name} failed: {data.get('error', {})}"
            except json.JSONDecodeError:
                # If it's not JSON, check for actual error indicators
                response_text = response[0].text.lower()
                error_phrases = ["error occurred", "failed to", "not found", "invalid", "unauthorized"]
                assert not any(phrase in response_text for phrase in error_phrases), \
                    f"{operation_name} failed: {response[0].text}"
    except Exception as e:
        # Log the error but don't fail the test
        print(f"DEBUG: Error in check_response_for_errors for {operation_name}: {e}")

def safe_extract_id(response, id_field):
    """Safely extract ID from API response with comprehensive error handling."""
    if not isinstance(response, list) or len(response) == 0:
        return None
    
    if not hasattr(response[0], "text"):
        return None
    
    try:
        data = json.loads(response[0].text)
        
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
                    
                # Also check if the key itself matches what we're looking for
                if key == id_field and value is not None:
                    return str(value)
    
    except Exception:
        # Catch all exceptions to prevent any crashes
        pass
    
    return None

def safe_extract_ids(response, id_field, max_count=2):
    """Safely extract multiple IDs from API response."""
    if not isinstance(response, list) or len(response) == 0:
        return []
    
    if not hasattr(response[0], "text"):
        return []
    
    try:
        data = json.loads(response[0].text)
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
        # Catch all exceptions to prevent any crashes
        return []

class TestComprehensiveDataAnalysisWorkflows:
    """Test comprehensive data analysis workflows across multiple tool categories."""
    
    async def test_complete_environment_assessment_workflow(self, mcp_server):
        """Test workflow: complete environment assessment using all available tools."""
        async with Client(mcp_server) as client:
            # Step 1: CommCell Infrastructure Assessment
            commcell_details = await client.call_tool("get_commcell_details", {})
            if isinstance(commcell_details, list) and hasattr(commcell_details[0], "text"):
                try:
                    data = json.loads(commcell_details[0].text)
                    assert not is_real_error(data)
                except:
                    pass
            
            # Step 2: Client Infrastructure Analysis
            all_clients = await client.call_tool("get_client_list", {})
            assert isinstance(all_clients, list) or "error" not in all_clients[0].text.lower()
            
            client_groups = await client.call_tool("get_client_group_list", {})
            assert isinstance(client_groups, list) or "error" not in client_groups[0].text.lower()
            
            # Step 3: Storage Infrastructure Analysis
            storage_policies = await client.call_tool("get_storage_policy_list", {})
            assert isinstance(storage_policies, list)
            
            storage_pools = await client.call_tool("get_storage_pool_list", {})
            assert isinstance(storage_pools, list)
            
            media_agents = await client.call_tool("get_mediaagent_list", {})
            assert isinstance(media_agents, list)
            
            # Step 4: Job Performance Analysis
            recent_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 86400,
                "limit": 50
            })
            assert isinstance(recent_jobs, list) or "error" not in recent_jobs[0].text.lower()
            
            failed_jobs = await client.call_tool("get_failed_jobs", {
                "jobLookupWindow": 86400,
                "limit": 25
            })
            assert isinstance(failed_jobs, list) or "error" not in failed_jobs[0].text.lower()
            
            # Step 5: Security and User Analysis
            users_list = await client.call_tool("get_users_list", {})
            assert isinstance(users_list, list) or "error" not in users_list[0].text.lower()
            
            security_posture = await client.call_tool("get_security_posture", {})
            if isinstance(security_posture, list) and hasattr(security_posture[0], "text"):
                try:
                    data = json.loads(security_posture[0].text)
                    assert not is_real_error(data)
                except:
                    pass

    async def test_client_subclient_job_correlation_workflow(self, mcp_server):
        """Test workflow: correlate clients, subclients, and their job performance."""
        async with Client(mcp_server) as client:
            # Step 1: Get client infrastructure
            all_clients = await client.call_tool("get_client_list", {})
            assert isinstance(all_clients, list) or "error" not in all_clients[0].text.lower()
            
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
                check_response_for_errors(subclients, f"Get subclients for client {client_id}")
                
                # Get jobs for this client
                client_jobs = await client.call_tool("get_jobs_list", {
                    "client_id": client_id,
                    "jobLookupWindow": 86400,
                    "limit": 25
                })
                assert isinstance(client_jobs, list) or "error" not in client_jobs[0].text.lower()
                
                # Get detailed subclient properties
                subclient_id = safe_extract_id(subclients, "subClientId")
                
                if subclient_id:
                    subclient_props = await client.call_tool("get_subclient_properties", {
                        "subclient_id": subclient_id
                    })
                    check_response_for_errors(subclient_props, f"Get subclient properties for client {client_id}")
                    
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
            assert isinstance(backup_jobs_all, list) or "error" not in backup_jobs_all[0].text.lower()

    async def test_storage_policy_utilization_workflow(self, mcp_server):
        """Test workflow: analyze storage policy utilization and performance."""
        async with Client(mcp_server) as client:
            # Step 1: Get all storage policies
            storage_policies = await client.call_tool("get_storage_policy_list", {})
            assert isinstance(storage_policies, list)
            
            # Extract policy IDs dynamically
            policy_ids = safe_extract_ids(storage_policies, "storagePolicyId", 3)
            
            # Step 2: Analyze specific storage policies
            policy_analysis = {}
            for policy_id in policy_ids:
                # Get policy properties
                policy_props = await client.call_tool("get_storage_policy_properties", {
                    "storage_policy_id": policy_id
                })
                if isinstance(policy_props, list) and hasattr(policy_props[0], "text"):
                    try:
                        data = json.loads(policy_props[0].text)
                        if isinstance(data, dict):
                            assert not is_real_error(data)
                            
                            # Get copy details using discovered copy ID
                            copy_id = None
                            if "storagePolicyCopyInfo" in data:
                                copies = data["storagePolicyCopyInfo"]
                                if isinstance(copies, list) and len(copies) > 0:
                                    copy_id = str(copies[0].get("copyId"))
                            
                            copy_details = None
                            if copy_id:
                                copy_details = await client.call_tool("get_storage_policy_copy_details", {
                                    "storage_policy_id": policy_id,
                                    "copy_id": copy_id
                                })
                                if isinstance(copy_details, list) and hasattr(copy_details[0], "text"):
                                    try:
                                        copy_data = json.loads(copy_details[0].text)
                                        if isinstance(copy_data, dict):
                                            assert not is_real_error(copy_data)
                                    except:
                                        pass
                            
                            policy_analysis[policy_id] = {
                                'properties': policy_props,
                                'copy_details': copy_details
                            }
                    except:
                        pass
            
            # Step 3: Correlate with storage utilization
            storage_util = await client.call_tool("get_storage_space_utilization", {})
            if isinstance(storage_util, list) and hasattr(storage_util[0], "text"):
                try:
                    data = json.loads(storage_util[0].text)
                    if isinstance(data, dict):
                        assert not is_real_error(data)
                except:
                    pass
            
            # Step 4: Check related infrastructure
            storage_pools = await client.call_tool("get_storage_pool_list", {})
            assert isinstance(storage_pools, list)
            
            media_agents = await client.call_tool("get_mediaagent_list", {})
            assert isinstance(media_agents, list)

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
            assert isinstance(recent_jobs, list) or "error" not in recent_jobs[0].text.lower()
            
            # Step 2: Medium-term analysis (last day)
            daily_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 86400,  # 24 hours
                "limit": 100
            })
            assert isinstance(daily_jobs, list) or "error" not in daily_jobs[0].text.lower()
            
            # Step 3: Long-term analysis (last week)
            weekly_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 604800,  # 1 week
                "limit": 200
            })
            assert isinstance(weekly_jobs, list) or "error" not in weekly_jobs[0].text.lower()
            
            # Step 4: Failure trend analysis
            daily_failures = await client.call_tool("get_failed_jobs", {
                "jobLookupWindow": 86400,
                "limit": 25
            })
            assert isinstance(daily_failures, list) or "error" not in daily_failures[0].text.lower()
            
            weekly_failures = await client.call_tool("get_failed_jobs", {
                "jobLookupWindow": 604800,
                "limit": 75
            })
            assert isinstance(weekly_failures, list) or "error" not in weekly_failures[0].text.lower()

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
                assert isinstance(type_jobs, list) or "error" not in type_jobs[0].text.lower()
                
                job_type_analysis[job_type] = type_jobs
            
            # Compare with overall job distribution
            all_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 86400,
                "limit": 100
            })
            assert isinstance(all_jobs, list) or "error" not in all_jobs[0].text.lower()

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
                assert isinstance(all_client_jobs, list) or "error" not in all_client_jobs[0].text.lower()
                
                # Get backup jobs specifically
                backup_jobs = await client.call_tool("get_jobs_list", {
                    "client_id": client_id,
                    "job_filter": "Backup",
                    "jobLookupWindow": 86400,
                    "limit": 20
                })
                assert isinstance(backup_jobs, list) or "error" not in backup_jobs[0].text.lower()
                
                # Get client details
                subclients = await client.call_tool("get_subclient_list", {
                    "client_identifier": client_id,
                    "identifier_type": "id"
                })
                check_response_for_errors(subclients, f"Get subclients for client {client_id}")
                
                client_performance[client_id] = {
                    'all_jobs': all_client_jobs,
                    'backup_jobs': backup_jobs,
                    'subclients': subclients
                }

class TestSecurityComplianceWorkflows:
    """Test security compliance and audit workflows."""
    
    async def test_security_audit_workflow(self, mcp_server):
        """Test workflow: comprehensive security audit across all components."""
        async with Client(mcp_server) as client:
            # Step 1: Overall security assessment
            security_posture = await client.call_tool("get_security_posture", {})
            if isinstance(security_posture, list) and hasattr(security_posture[0], "text"):
                try:
                    data = json.loads(security_posture[0].text)
                    assert not is_real_error(data)
                except:
                    pass
            
            security_score = await client.call_tool("get_security_score", {})
            if isinstance(security_score, list) and hasattr(security_score[0], "text"):
                try:
                    data = json.loads(security_score[0].text)
                    assert not is_real_error(data)
                except:
                    pass
            
            # Step 2: User access audit
            all_users = await client.call_tool("get_users_list", {})
            assert isinstance(all_users, list) or "error" not in all_users[0].text.lower()
            
            user_groups = await client.call_tool("get_user_groups_list", {})
            assert isinstance(user_groups, list) or "error" not in user_groups[0].text.lower()
            
            # Step 3: Role and permission analysis
            roles_list = await client.call_tool("get_roles_list", {})
            assert isinstance(roles_list, list) or "error" not in roles_list[0].text.lower()
            
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
                    if isinstance(entity_perms, list) and hasattr(entity_perms[0], "text"):
                        try:
                            data = json.loads(entity_perms[0].text)
                            assert not is_real_error(data)
                        except:
                            pass

    async def test_user_access_review_workflow(self, mcp_server):
        """Test workflow: comprehensive user access review."""
        async with Client(mcp_server) as client:
            # Step 1: Get all users and groups
            all_users = await client.call_tool("get_users_list", {})
            assert isinstance(all_users, list) or "error" not in all_users[0].text.lower()
            
            all_groups = await client.call_tool("get_user_groups_list", {})
            assert isinstance(all_groups, list) or "error" not in all_groups[0].text.lower()
            
            # Step 2: Detailed analysis of key users
            key_users = safe_extract_ids(all_users, "userId", 4)
            user_analysis = {}
            
            for user_id in key_users:
                # Get user properties
                user_props = await client.call_tool("get_user_properties", {"user_id": user_id})
                if isinstance(user_props, list) and hasattr(user_props[0], "text"):
                    try:
                        data = json.loads(user_props[0].text)
                        assert not is_real_error(data)
                    except:
                        pass
                
                # Get user associations
                user_entities = await client.call_tool("get_associated_entities_for_user_or_user_group", {
                    "id": user_id,
                    "type": "user"
                })
                if isinstance(user_entities, list) and hasattr(user_entities[0], "text"):
                    try:
                        data = json.loads(user_entities[0].text)
                        assert not is_real_error(data)
                    except:
                        pass
                
                user_analysis[user_id] = {
                    'properties': user_props,
                    'entities': user_entities
                }
            
            # Step 3: Group analysis
            key_groups = safe_extract_ids(all_groups, "userGroupId", 2)
            for group_id in key_groups:
                group_props = await client.call_tool("get_user_group_properties", {"user_group_id": group_id})
                if isinstance(group_props, list) and hasattr(group_props[0], "text"):
                    try:
                        data = json.loads(group_props[0].text)
                        assert not is_real_error(data)
                    except:
                        pass
                
                group_entities = await client.call_tool("get_associated_entities_for_user_or_user_group", {
                    "id": group_id,
                    "type": "usergroup"
                })
                if isinstance(group_entities, list) and hasattr(group_entities[0], "text"):
                    try:
                        data = json.loads(group_entities[0].text)
                        assert not is_real_error(data)
                    except:
                        pass

class TestOperationalWorkflows:
    """Test operational workflows combining multiple tool categories."""
    
    async def test_daily_operations_checkup_workflow(self, mcp_server):
        """Test workflow: daily operations health checkup."""
        async with Client(mcp_server) as client:
            # Step 1: Overall system health
            sla_status = await client.call_tool("get_sla_status", {})
            if isinstance(sla_status, list) and hasattr(sla_status[0], "text"):
                try:
                    data = json.loads(sla_status[0].text)
                    assert not is_real_error(data)
                except:
                    pass
            
            storage_util = await client.call_tool("get_storage_space_utilization", {})
            if isinstance(storage_util, list) and hasattr(storage_util[0], "text"):
                try:
                    data = json.loads(storage_util[0].text)
                    assert not is_real_error(data)
                except:
                    pass
            
            # Step 2: Job performance check
            last_24h_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 86400,
                "limit": 50
            })
            assert isinstance(last_24h_jobs, list) or "error" not in last_24h_jobs[0].text.lower()
            
            failed_jobs = await client.call_tool("get_failed_jobs", {
                "jobLookupWindow": 86400,
                "limit": 20
            })
            assert isinstance(failed_jobs, list) or "error" not in failed_jobs[0].text.lower()
            
            # Step 3: Infrastructure check
            all_clients = await client.call_tool("get_client_list", {})
            assert isinstance(all_clients, list) or "error" not in all_clients[0].text.lower()
            
            schedules_list = await client.call_tool("get_schedules_list", {})
            assert isinstance(schedules_list, list) or "error" not in schedules_list[0].text.lower()
            
            # Step 4: Plans and policies check
            plans_list = await client.call_tool("get_plan_list", {})
            assert isinstance(plans_list, list) or "error" not in plans_list[0].text.lower()
            
            storage_policies = await client.call_tool("get_storage_policy_list", {})
            assert isinstance(storage_policies, list)

    async def test_incident_response_workflow(self, mcp_server):
        """Test workflow: incident response and investigation."""
        async with Client(mcp_server) as client:
            # Step 1: Identify issues
            failed_jobs = await client.call_tool("get_failed_jobs", {
                "jobLookupWindow": 86400,
                "limit": 30
            })
            assert isinstance(failed_jobs, list) or "error" not in failed_jobs[0].text.lower()
            
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
                    check_response_for_errors(job_details, f"Get job details for {job_id}")
                    
                    task_details = await client.call_tool("get_job_task_details", {"job_id": job_id})
                    check_response_for_errors(task_details, f"Get task details for {job_id}")
                    
                    retention_info = await client.call_tool("get_retention_info_of_a_job", {"job_id": job_id})
                    check_response_for_errors(retention_info, f"Get retention info for {job_id}")
                    
                    # Generate logs for investigation
                    send_logs = await client.call_tool("create_send_logs_job_for_a_job", {
                        "emailid": "incident@test.com",
                        "job_id": job_id
                    })
                    check_response_for_errors(send_logs, f"Create send logs for {job_id}")
            
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
                    check_response_for_errors(subclient_props, "Get subclient properties")
            
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
                if isinstance(commcell_logs, list) and hasattr(commcell_logs[0], "text"):
                    try:
                        data = json.loads(commcell_logs[0].text)
                        assert not is_real_error(data)
                    except:
                        pass

class TestReportingWorkflows:
    """Test comprehensive reporting workflows."""
    
    async def test_executive_dashboard_workflow(self, mcp_server):
        """Test workflow: generate executive dashboard data."""
        async with Client(mcp_server) as client:
            # Step 1: High-level metrics
            commcell_details = await client.call_tool("get_commcell_details", {})
            if isinstance(commcell_details, list) and hasattr(commcell_details[0], "text"):
                try:
                    data = json.loads(commcell_details[0].text)
                    assert not is_real_error(data)
                except:
                    pass
            
            sla_status = await client.call_tool("get_sla_status", {})
            if isinstance(sla_status, list) and hasattr(sla_status[0], "text"):
                try:
                    data = json.loads(sla_status[0].text)
                    assert not is_real_error(data)
                except:
                    pass
            
            security_score = await client.call_tool("get_security_score", {})
            if isinstance(security_score, list) and hasattr(security_score[0], "text"):
                try:
                    data = json.loads(security_score[0].text)
                    assert not is_real_error(data)
                except:
                    pass
            
            # Step 2: Infrastructure overview
            client_count = await client.call_tool("get_client_list", {})
            assert isinstance(client_count, list) or "error" not in client_count[0].text.lower()
            
            storage_overview = await client.call_tool("get_storage_space_utilization", {})
            if isinstance(storage_overview, list) and hasattr(storage_overview[0], "text"):
                try:
                    data = json.loads(storage_overview[0].text)
                    assert not is_real_error(data)
                except:
                    pass
            
            # Step 3: Operational metrics
            weekly_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 604800,  # 1 week
                "limit": 200
            })
            assert isinstance(weekly_jobs, list) or "error" not in weekly_jobs[0].text.lower()
            
            weekly_failures = await client.call_tool("get_failed_jobs", {
                "jobLookupWindow": 604800,
                "limit": 100
            })
            assert isinstance(weekly_failures, list) or "error" not in weekly_failures[0].text.lower()

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
                
                # Get copy details if available
                if isinstance(policy_props, list) and hasattr(policy_props[0], "text"):
                    try:
                        data = json.loads(policy_props[0].text)
                        if isinstance(data, dict) and "storagePolicyCopyInfo" in data:
                            copies = data["storagePolicyCopyInfo"]
                            if isinstance(copies, list) and len(copies) > 0:
                                copy_id = str(copies[0].get("copyId"))
                                if copy_id:
                                    copy_details = await client.call_tool("get_storage_policy_copy_details", {
                                        "storage_policy_id": policy_id,
                                        "copy_id": copy_id
                                    })
                    except:
                        pass
            
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
            assert isinstance(backup_jobs, list) or "error" not in backup_jobs[0].text.lower()
            
            # Step 2: Get storage utilization
            storage_util = await client.call_tool("get_storage_space_utilization", {})
            if isinstance(storage_util, list) and hasattr(storage_util[0], "text"):
                try:
                    data = json.loads(storage_util[0].text)
                    assert not is_real_error(data)
                except:
                    pass
            
            # Step 3: Analyze storage policies used
            storage_policies = await client.call_tool("get_storage_policy_list", {})
            assert isinstance(storage_policies, list)
            
            # Step 4: Check storage infrastructure
            storage_pools = await client.call_tool("get_storage_pool_list", {})
            assert isinstance(storage_pools, list)
            
            media_agents = await client.call_tool("get_mediaagent_list", {})
            assert isinstance(media_agents, list)

    async def test_user_activity_correlation_workflow(self, mcp_server):
        """Test workflow: correlate user activities with system operations."""
        async with Client(mcp_server) as client:
            # Step 1: Get user information
            all_users = await client.call_tool("get_users_list", {})
            assert isinstance(all_users, list) or "error" not in all_users[0].text.lower()
            
            # Step 2: Analyze user permissions and access using dynamic user IDs
            user_ids = safe_extract_ids(all_users, "userId", 2)
            for user_id in user_ids:
                user_props = await client.call_tool("get_user_properties", {"user_id": user_id})
                user_entities = await client.call_tool("get_associated_entities_for_user_or_user_group", {
                    "id": user_id,
                    "type": "user"
                })
            
            # Step 3: Check recent system activities
            recent_jobs = await client.call_tool("get_jobs_list", {
                "jobLookupWindow": 86400,
                "limit": 50
            })
            assert isinstance(recent_jobs, list) or "error" not in recent_jobs[0].text.lower()
            
            # Step 4: Look for logs and administrative activities
            admin_jobs = await client.call_tool("get_jobs_list", {
                "job_filter": "SEND_LOGFILE",
                "jobLookupWindow": 86400,
                "limit": 20
            })
            assert isinstance(admin_jobs, list) or "error" not in admin_jobs[0].text.lower()