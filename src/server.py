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

from typing import Annotated
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cv_api_client import CommvaultApiClient
from src.wrappers import *
from src.logger import logger
from src.utils import get_env_var

mcp = FastMCP(name="Commvault MCP Server", instructions="You can use this server to interact with Commvault Product")
commvault_api_client = CommvaultApiClient()


@mcp.tool()
def get_job_detail(job_id: Annotated[int, Field(description="The ID of the job to retrieve.")],) -> dict:
    """
    Gets complete details about a job for a given job id.

    Returns:
        A dictionary containing all available information about the specified job.
    """
    try:
        endpoint = f"Job/{job_id}"
        jobs_list = commvault_api_client.get(endpoint).get("jobs", [])
        if not jobs_list:
            raise Exception(f"No job found with ID: {job_id}")
        return jobs_list[0]
    except Exception as e:
        logger.error(f"Error getting job detail: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def suspend_job(job_id: Annotated[int, Field(description="The ID of the job to suspend.")]) -> dict:
    """
    Suspends/pauses the job with the given job id.
    """
    try:
        endpoint = f"Job/{job_id}/Action/pause"
        return commvault_api_client.post(endpoint, data={})
    except Exception as e:
        logger.error(f"Error suspending job: {e}")
        return ToolError({"error": str(e)})
    
@mcp.tool()
def resume_job(job_id: Annotated[int, Field(description="The ID of the job to resume.")]) -> dict:
    """
    Resumes the job with the given job id.
    """
    try:
        endpoint = f"Job/{job_id}/Action/Resume"
        return commvault_api_client.post(endpoint, data={})
    except Exception as e:
        logger.error(f"Error resuming job: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def resubmit_job(job_id: Annotated[int, Field(description="The ID of the job to resubmit.")]) -> dict:
    """
    Resubmits the job with the given job id.
    """
    try:
        endpoint = f"Job/{job_id}/Action/Resubmit"
        return commvault_api_client.post(endpoint, data={})
    except Exception as e:
        logger.error(f"Error resubmitting job: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def kill_job(job_id: Annotated[int, Field(description="The ID of the job to kill.")],) -> dict:
    """
    Kills the job with the given job id.
    """
    try:
        endpoint = f"Job/{job_id}/Action/Kill"
        return commvault_api_client.post(endpoint, data={})
    except Exception as e:
        logger.error(f"Error killing job: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_jobs_list(
    jobLookupWindow: Annotated[int, Field(description="The time window in seconds to look up for jobs jobs. For example, 86400 for the last 24 hours.")]=86400,
    job_filter: Annotated[str, Field(description="The job types to filter by. Multiple types can be provided, comma-separated. If not used, returns backup jobs. Valid values are: MAGLIBMAINTENANCE, SELECTIVEDELETE, ARCHIVERESTORE, MEDIAINIT, SEND_LOGFILE, AUXCOPY, MEDIAINVENTORY, SHELFMANAGEMENT, Backup, MEDIAPREDICTION, SNAPBACKUP, BACKUP3RD, BROWSEANDDELETE, MEDIARECYCLE, SNAPBACKUP3RD, CATALOG_MIGRATION, MEDIAREFRESHING, SNAPRECOVERY, CATALOGUEMEDIA, MEDIAREFRESHING2, SNAPSHOT, CCMCAPTURE, MININGBACKUP, SNAPTOTAPE, CCMMERGE, MININGCONTENTINDEX, SNAPTOTAPEWORKFLOW, COMMCELLSYNC, MOVE_MOUNT_PATH, SNAPVAULTRESTORE, CONTDATAREPLICATION, MOVEDDB, SPACE_RECLAMATION, CONTENT_INDEXING_ENTITY_EXTRACTION, MULTI_NODE_CONTENT_INDEXING, SRMAGENTLESSOPTYPE, CREATECONSISTENCYPOINT, OFFLINE, SRMOPTYPE, CREATERECOVERYPOINT, OFFLINE_MINING_RESTORE, SRMREPORT, CREATEREPLICA, OFFLINECONTENTINDEX, SRSYSTEMRECOVERY, CSDRBKP, ONLINE, STAMPMEDIA, CVEXPORT, Online_Content_Index, STATELESS_BACKUP, DATA_ANALYTICS, ONLINE_CRAWL, STUBBING, DATA_VERIFICATION, OPENBACKUP, SUBCLIENTCONTENTINDEX, DDBOPS, OTHERADMINOPERATION, SYNTHFULL, DEDUPDBSYNC, PATCHDOWNLOAD, SYSRECOVERYBACKUP, DEDUPDBSYNC_DASH, PATCHUPDATE, SYSSTATEBACKUP, DELAYEDCATALOG, POWERRESTORE, TAPE2TAPECOPY, DELAYEDCATALOGWORKFLOW, POWERSEARCHANDRETRIEVE, TAPEERASE, DMOUTLOOKRST, PRUNE, TAPEIMPORT, DRIVECLEANING, PST_ARCHIVING, TDFSBACKUP, DRIVEVALIDATION, QRCOPYBACK, TURBO_NAS, DRORCHESTRATION, QRROLLBACK, UNINSTALLCLIENT, EXCHANGE_IMPORT, QUICKDMRST, UPDATEREPLICA, EXCHANGE_LIVE_BROWSE_RST, RECOVERY_POINT_CREATION_RST, UPGRADE_CLIENT, FDCCLIENT, REFCOPYPSTARCHIVING, VIRTUALIZEME, FDCOPTYPE, REFERENCECOPY, VM_Management, FDCPREPARATION, REFERENCECOPYWORKFLOW, VSA_BLOCK_REPLICATION, FDCWORKFLOW, REPLICATION, VSA_BLOCK_REPLICATION_DRIVER_INSTALL, FLRCOPYBACK, REPORT, VSA_BLOCK_REPLICATION_DRIVER_UNINSTALL, IMPORT, Restore, VSA_BLOCK_REPLICATION_DRIVER_UPDATE, INDEXFREERESTORE, RESTORE_VALIDATE, W2KFULLBUILDRESTORE, INDEXRESTORE, SCHEDEXPORT, W2KFULLBUILDRESTORE371, INFOMGMT, SCHEDULE, W2KSYSSTRESTORE, INSTALLCLIENT, SEARCHANDRETRIEVE, WORKFLOW, LOG_MONITORING, SECUREERASE, WORKFLOW_MGMT.")]="", 
    job_status: Annotated[str, Field(description="The job status to filter by. Valid values are: Active, Finished, All")] = "All", 
    client_id: Annotated[str, Field(description="The client id to filter jobs by. Not mandatory. If not provided, jobs for all clients will be returned.")] = None,
    limit: Annotated[int, Field(description="The maximum number of jobs to return. Default is 50.")] = 50,
    offset: Annotated[int, Field(description="The offset for pagination.")] = 0) -> dict:
    """
    Gets the list of jobs filtered by job type/status/clientId in a given jobLookupWindow.
    """
    try:
        params = {
            "jobCategory": job_status,
            "completedJobLookupTime": jobLookupWindow,
            "limit": limit
        }
        if job_filter:
            params["jobFilter"] = job_filter
        if client_id:
            params["clientId"] = client_id
        if offset is not None:
            params["offset"] = offset
        response = commvault_api_client.get("Job", params=params)
        return get_basic_job_details(response)
    except Exception as e:
        logger.error(f"Error retrieving jobs by job type: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_job_task_details(job_id: Annotated[int, Field(description="The job id to retrieve task details for.")]) -> dict:
    """
    Gets task details for a given job ID.
    """
    try:
        return commvault_api_client.get(f"Job/{job_id}/taskdetails")
    except Exception as e:
        logger.error(f"Error retrieving job task details: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_retention_info_of_a_job(job_id: Annotated[int, Field(description="The job id to retrieve retention info for.")]) -> dict:
    """
    Gets retention info for a given job ID.
    """
    try:
        return commvault_api_client.get(f"Job/{job_id}/advanceddetails", params={"infoType": 1})
    except Exception as e:
        logger.error(f"Error retrieving retention info: {e}")
        return ToolError({"error": str(e)})

##################################################

######SLA and Security Tools######

@mcp.tool()
def get_sla_status() -> dict:
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

##################################################

###### CLIENT MANAGEMENT TOOLS ######

@mcp.tool()
def get_client_group_list() -> dict:
    """
    Gets the list of client groups.
    """
    try:
        response = commvault_api_client.get("ClientGroup")
        return get_basic_client_group_details(response)
    except Exception as e:
        logger.error(f"Error retrieving client group list: {e}")
        return ToolError({"error": str(e)})
    
@mcp.tool()
def get_client_list() -> dict:
    """
    Gets the list of clients.
    """
    try:
        response = commvault_api_client.get("Client")
        return filter_client_list_response(response)
    except Exception as e:
        logger.error(f"Error retrieving client list: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_client_group_properties(client_group_id: Annotated[str, Field(description="The client group id to retrieve properties for.")]) -> dict:
    """
    Gets properties for a given client group id.
    """
    try:
        return commvault_api_client.get(f"ClientGroup/{client_group_id}")
    except Exception as e:
        logger.error(f"Error retrieving client group properties: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_clientid_from_clientname(client_name: Annotated[str, Field(description="The client name to retrieve client id for.")]) -> dict:
    """
    Gets client id for a given client name.
    """
    try:
        return commvault_api_client.get("getid", params={"clientname": client_name})
    except Exception as e:
        logger.error(f"Error retrieving client id: {e}")
        return ToolError({"error": str(e)})

##################################################

###### SUBCLIENT MANAGEMENT TOOLS ######

@mcp.tool()
def get_subclient_list(client_identifier: Annotated[str, Field(description="The client name or ID to retrieve subclients for.")], identifier_type: Annotated[str, Field(description="Specify 'name' to use client name or 'id' to use client ID.")]) -> dict:
    """
    Gets subclient list for a given client name or client id.
    Args:
        client_identifier: The client name or ID.
        identifier_type: 'name' or 'id'.
    Returns:
        Subclient list for the specified client, filtered for LLM-friendly output.
    """
    try:
        if identifier_type == 'name':
            params = {"clientName": client_identifier}
        elif identifier_type == 'id':
            params = {"clientId": client_identifier}
        else:
            raise ValueError("identifier_type must be 'name' or 'id'")
        response = commvault_api_client.get("subclient", params=params)
        return filter_subclient_response(response)
    except Exception as e:
        logger.error(f"Error getting subclient list for client {identifier_type}: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_subclient_properties(subclient_id: Annotated[str, Field(description="The subclient id to retrieve properties for.")]) -> dict:
    """
    Gets subclient properties for a given subclient id.
    """
    try:
        return commvault_api_client.get(f"subclient/{subclient_id}")
    except Exception as e:
        logger.error(f"Error getting subclient properties: {e}")
        return ToolError({"error": str(e)})

##################################################


###### SCHEDULE POLICY MANAGEMENT TOOLS ######


###### STORAGE POLICY MANAGEMENT TOOLS ######

@mcp.tool()
def get_storage_policy_list() -> dict:
    """
    Gets storage policy list.
    """
    try:
        return commvault_api_client.get("V2/StoragePolicy")
    except Exception as e:
        logger.error(f"Error getting storage policy list: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_storage_policy_properties(storage_policy_id: Annotated[str, Field(description="The storage policy id to retrieve properties for.")]) -> dict:
    """
    Gets storage policy properties for a given storage policy id.
    """
    try:
        return commvault_api_client.get(f"V2/StoragePolicy/{storage_policy_id}?propertyLevel=10")
    except Exception as e:
        logger.error(f"Error getting storage policy properties: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_storage_policy_copy_details(storage_policy_id: Annotated[str, Field(description="The storage policy id to retrieve copy details for.")], copy_id: Annotated[str, Field(description="The copy id to retrieve details for.")]) -> dict:
    """
    Gets storage policy copy details for a given storage policy id and copy id.
    """
    try:
        return commvault_api_client.get(f"V2/StoragePolicy/{storage_policy_id}/Copy/{copy_id}")
    except Exception as e:
        logger.error(f"Error getting storage policy copy details: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_storage_policy_copy_size(storage_policy_id: Annotated[str, Field(description="The storage policy id to retrieve copy size for.")], copy_id: Annotated[str, Field(description="The copy id to retrieve size for.")]) -> dict:
    """
    Gets storage policy copy size for a given storage policy id and copy id.
    """
    try:
        return commvault_api_client.get(f"V2/StoragePolicy/{storage_policy_id}/Copy/{copy_id}/Size")
    except Exception as e:
        logger.error(f"Error getting storage policy copy size: {e}")
        return ToolError({"error": str(e)})
    
###################################################

###### STORAGE MANAGEMENT TOOLS ######

@mcp.tool()
def get_library_list() -> dict:
    """
    Gets the list of libraries.
    """
    try:
        return commvault_api_client.get("V2/Library?propertyLevel=10")
    except Exception as e:
        logger.error(f"Error retrieving library list: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_library_properties(library_id: Annotated[str, Field(description="The library id to retrieve properties for.")]) -> dict:
    """
    Gets properties for a given library id.
    """
    try:
        return commvault_api_client.get(f"V2/Library/{library_id}")
    except Exception as e:
        logger.error(f"Error retrieving library properties: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_mediaagent_list() -> dict:
    """
    Gets the list of media agents.
    """
    try:
        return commvault_api_client.get("MediaAgent")
    except Exception as e:
        logger.error(f"Error retrieving media agent list: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_storage_pool_list() -> dict:
    """
    Gets the list of storage pools, filtered for LLM-friendly output.
    """
    try:
        response = commvault_api_client.get("StoragePool")
        return filter_storage_pool_response(response)
    except Exception as e:
        logger.error(f"Error retrieving storage pool list: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_commcell_details() -> dict:
    """
    Gets the details of the commcell, formatted for LLM consumption.
    """
    try:
        api_response = commvault_api_client.get("cr/reportsplusengine/datasets/a0f077a5-2dfe-4010-a957-57a24cae89a8/data")
        return format_report_dataset_response(api_response)
    except Exception as e:
        logger.error(f"Error retrieving commcell details: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_entity_counts() -> dict:
    """
    Gets the total count of entities, including servers, VMs, laptops, and users, within the CommCell environment.
    """
    try:
        api_response = commvault_api_client.get("/cr/reportsplusengine/datasets/d0a73c45-b06d-4358-8d7e-d55d428ba75c/data?cache=true&parameter.i_dashboardtype=commcell&datasource=2")
        return format_report_dataset_response(api_response)
    except Exception as e:
        logger.error(f"Error retrieving entity counts: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def create_send_logs_job_for_commcell(emailid: Annotated[str, Field(description="The email id to send logs to.")], commcell_name: Annotated[str, Field(description="The commcell name for which to send logs.")]) -> dict:
    """
    Triggers a new send logs job for the specified CommCell and sends logs to the provided email address.
    If successful, returns the job ID of the created send logs job.
    """
    try:
        data = {
            "taskInfo": {
                "task": {
                    "taskType": 1,
                    "initiatedFrom": 1,
                    "policyType": 0,
                    "taskFlags": {"disabled": False}
                },
                "subTasks": [
                    {
                        "subTask": {"subTaskType": 1, "operationType": 5010},
                        "options": {
                            "adminOpts": {
                                "sendLogFilesOption": {
                                    "actionLogsEndJobId": 0,
                                    "emailSelected": True,
                                    "jobid": 0,
                                    "tsDatabase": False,
                                    "galaxyLogs": True,
                                    "getLatestUpdates": False,
                                    "actionLogsStartJobId": 0,
                                    "computersSelected": True,
                                    "csDatabase": False,
                                    "otherDatabases": False,
                                    "crashDump": False,
                                    "isNetworkPath": False,
                                    "saveToFolderSelected": False,
                                    "notifyMe": True,
                                    "includeJobResults": False,
                                    "doNotIncludeLogs": True,
                                    "machineInformation": True,
                                    "scrubLogFiles": False,
                                    "emailSubject": f"Your CommCell Logs",
                                    "osLogs": True,
                                    "allUsersProfile": True,
                                    "splitFileSizeMB": 512,
                                    "actionLogs": False,
                                    "includeIndex": False,
                                    "databaseLogs": True,
                                    "includeDCDB": False,
                                    "collectHyperScale": False,
                                    "logFragments": False,
                                    "uploadLogsSelected": True,
                                    "useDefaultUploadOption": True,
                                    "enableChunking": True,
                                    "collectRFC": False,
                                    "collectUserAppLogs": False,
                                    "impersonateUser": {"useImpersonation": False},
                                    "clients": [
                                        {"clientId": 2, "clientName": commcell_name}
                                    ],
                                    "recipientCc": {
                                        "emailids": [emailid],
                                        "users": [],
                                        "userGroups": []
                                    },
                                    "sendLogsOnJobCompletion": False
                                }
                            }
                        }
                    }
                ]
            }
        }
        return commvault_api_client.post("createtask", data=data)
    except Exception as e:
        logger.error(f"Error creating send logs job for commcell: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def create_send_logs_job_for_a_job(emailid: Annotated[str, Field(description="The email id to send logs to.")], job_id: Annotated[int, Field(description="The job id for which to send logs.")]) -> dict:
    """
    Triggers a new send logs job for the specified job ID and sends logs to the provided email address.
    If successful, returns the job ID of the created send logs job.
    """
    try:
        data = {
            "taskInfo": {
                "task": {
                    "taskType": 1,
                    "initiatedFrom": 1,
                    "policyType": 0,
                    "taskFlags": {"disabled": False}
                },
                "subTasks": [
                    {
                        "subTask": {"subTaskType": 1, "operationType": 5010},
                        "options": {
                            "adminOpts": {
                                "sendLogFilesOption": {
                                    "actionLogsEndJobId": 0,
                                    "emailSelected": True,
                                    "jobid": job_id,
                                    "tsDatabase": False,
                                    "galaxyLogs": True,
                                    "getLatestUpdates": False,
                                    "actionLogsStartJobId": 0,
                                    "computersSelected": False,
                                    "csDatabase": False,
                                    "otherDatabases": False,
                                    "crashDump": False,
                                    "isNetworkPath": False,
                                    "saveToFolderSelected": False,
                                    "notifyMe": True,
                                    "includeJobResults": False,
                                    "doNotIncludeLogs": True,
                                    "machineInformation": True,
                                    "scrubLogFiles": False,
                                    "emailSubject": f"Job {job_id} : Send Logs",
                                    "osLogs": True,
                                    "allUsersProfile": True,
                                    "splitFileSizeMB": 512,
                                    "actionLogs": False,
                                    "includeIndex": False,
                                    "databaseLogs": True,
                                    "includeDCDB": False,
                                    "collectHyperScale": False,
                                    "logFragments": False,
                                    "uploadLogsSelected": True,
                                    "useDefaultUploadOption": True,
                                    "enableChunking": True,
                                    "collectRFC": False,
                                    "collectUserAppLogs": False,
                                    "impersonateUser": {"useImpersonation": False},
                                    "clients": [
                                        {"clientId": 0, "clientName": "null"}
                                    ],
                                    "recipientCc": {
                                        "emailids": [emailid],
                                        "users": [],
                                        "userGroups": []
                                    },
                                    "sendLogsOnJobCompletion": False
                                }
                            }
                        }
                    }
                ]
            }
        }
        return commvault_api_client.post("createtask", data=data)
    except Exception as e:
        logger.error(f"Error creating send logs job for job: {e}")
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