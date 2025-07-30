# --------------------------------------------------------------------------
# Copyright Commvault Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------------------------------------------------

from src.logger import logger


def get_basic_job_details(api_response):
    """
    Extracts minimal, LLM-friendly job details from the API response.
    """
    jobs = api_response.get("jobs", [])
    basic_details = []
    for job in jobs:
        summary = job.get("jobSummary", {})
        basic_details.append({
            "jobId": summary.get("jobId"),
            "status": summary.get("status"),
            "jobType": summary.get("jobType"),
            "backupLevelName": summary.get("backupLevelName"),
            "jobStartTime": summary.get("jobStartTime"),
            "jobEndTime": summary.get("jobEndTime"),
            "clientName": summary.get("destinationClient", {}).get("clientName"),
            "storagePolicyName": summary.get("storagePolicy", {}).get("storagePolicyName"),
        })
    return {
        "totalJobsAvailable": api_response.get("totalRecordsWithoutPaging", 0),
        "jobsInThisResponse": basic_details
    }

def get_basic_client_group_details(api_response):
    """
    Extracts minimal, LLM-friendly client group details from the API response.
    """
    groups = api_response.get("groups", [])
    filtered = []
    for g in groups:
        cg = g.get("clientGroup", {})
        entity = cg.get("entityInfo", {}) if cg else {}
        filtered.append({
            "clientGroupId": cg.get("clientGroupId", g.get("Id")),
            "clientGroupName": g.get("name"),
            "clientCount": g.get("clientCount"),
            "companyName": entity.get("companyName")
        })
    return {"totalClientGroups": len(filtered), "clientGroups": filtered}

def filter_subclient_response(api_response):
    """
    Filters the subclient response to only include relevant fields for each subclient.
    """
    relevant_keys = [
        "clientName", "instanceName", "displayName", "backupsetId",
        "instanceId", "subclientId", "appName", "backupsetName",
        "subclientName"
    ]
    filtered = []
    for subclient in api_response.get("subClientProperties", []):
        entity = subclient.get("subClientEntity", {})
        filtered_entity = {k: entity.get(k) for k in relevant_keys if k in entity}
        filtered.append(filtered_entity)
    return {
        "subClientCount": api_response.get("filterQueryCount", 0),
        "subClients": filtered
    }

def filter_storage_pool_response(api_response):
    """
    Extracts minimal, LLM-friendly storage pool details from the API response.
    """
    pools = api_response.get("storagePoolList", [])
    filtered = []
    for pool in pools:
        pool_entity = pool.get("storagePoolEntity", {})
        region = pool.get("region", {})
        policy = pool.get("storagePolicyEntity", {})
        filtered.append({
            "storagePoolName": pool_entity.get("storagePoolName"),
            "storagePoolId": pool_entity.get("storagePoolId"),
            "totalFreeSpace": pool.get("totalFreeSpace"),
            "sizeOnDisk": pool.get("sizeOnDisk"),
            "status": pool.get("status"),
            "regionDisplayName": region.get("displayName"),
            "regionName": region.get("regionName"),
            "storagePolicyName": policy.get("storagePolicyName"),
            "storagePolicyId": policy.get("storagePolicyId"),
        })
    return {"storagePoolCount": len(filtered), "storagePools": filtered}

def format_report_dataset_response(api_response):
    """
    Formats the report dataset response for LLM consumption.
    Returns a list of dicts, each dict representing a record with column names as keys.
    """
    columns = api_response.get("columns", [])
    records = api_response.get("records", [])
    column_names = [col.get("name") for col in columns]
    formatted_records = []
    for record in records:
        formatted_records.append({column_names[i]: record[i] for i in range(len(column_names))})
    return {
        "totalRecordCount": api_response.get("totalRecordCount", 0),
        "records": formatted_records
    }

def transform_sla_data(api_response):
    """
    Transform SLA Data API response to a simplified format with SLA percentage.
    
    Args:
        api_response (dict): The original API response
        
    Returns:
        dict: Simplified data with SLA percentage
    """
    try:
        result = {}
        records = api_response.get('records', [])
        
        for record in records:
            # Each record is a list where index 2 is the SLA Status and index 3 is the CurrentCount
            sla_status = record[2]
            current_count = record[3]
            
            # Only consider Met SLA and Missed SLA, ignoring the other values for now
            if sla_status in ["Met SLA", "Missed SLA"]:
                result[sla_status] = current_count
        
        met_sla_count = result.get("Met SLA", 0)
        missed_sla_count = result.get("Missed SLA", 0)
        total_count = met_sla_count + missed_sla_count
        
        if total_count > 0:
            sla_percentage = (met_sla_count / total_count) * 100
        else:
            sla_percentage = 0
        
        result["SLA Percentage"] = round(sla_percentage, 2)
        return result
    except Exception as e:
        logger.error(f"Error transforming SLA data: {e}")
        raise Exception("Error transforming SLA data")

def compute_security_score(api_response):
    params = [
        p
        for cat in api_response.get("securityCategories", [])
        for p in cat.get("parameter", [])
    ]
    total = len(params)
    if total == 0:
        raise Exception("Some error occurred. Please try again later.")
    failures = sum(1 for p in params if p.get("status") == 2)
    return round((total - failures) / total * 100)

def filter_client_list_response(response):
    """
    Filters the client list response to return only clientName, clientId, displayName, hostName, clientGUID, and companyId.
    """
    filtered_clients = []
    for item in response.get("clientProperties", []):
        client_entity = item.get("client", {}).get("clientEntity", {})
        entity_info = client_entity.get("entityInfo", {})
        filtered_clients.append({
            "clientName": client_entity.get("clientName"),
            "clientId": client_entity.get("clientId"),
            "hostName": client_entity.get("hostName")
        })
    return {"clients": filtered_clients}

def filter_schedules_response(response):
    """
    Filters the schedules API response to return only relevant information with LLM-friendly key names.
    """
    schedules = []
    for item in response.get("taskDetail", []):
        task = item.get("task", {})
        sub_tasks = item.get("subTasks", [])
        filtered_subtasks = []
        for sub in sub_tasks:
            sub_task = sub.get("subTask", {})
            filtered_subtasks.append({
                "scheduleName": sub_task.get("subTaskName"),
                "scheduleId": sub_task.get("subTaskId"),
                "operationType": sub_task.get("operationType"),
                "nextRunTime": sub.get("nextScheduleTime"),
            })

        # Only add if "policyName" does not contain "System Created"
        policy_name = task.get("taskName", "")
        description = task.get("description", "")
        if "system created" not in policy_name.lower() and "system created" not in description.lower():
            schedules.append({
            "policyName": policy_name,
            "policyId": task.get("taskId"),
            "description": description,
            "schedules": filtered_subtasks,
            })
    return {"totalPolicies": len(schedules), "policies": schedules}
