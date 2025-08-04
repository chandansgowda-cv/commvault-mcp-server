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

from cv_api_client import CommvaultApiClient
from wrappers import *
from logger import logger
from utils import get_env_var
from tools.job_tools import JOB_MANAGEMENT_TOOLS

mcp = FastMCP(name="Commvault MCP Server", instructions="You can use this server to interact with Commvault Product")
commvault_api_client = CommvaultApiClient()

for tool in JOB_MANAGEMENT_TOOLS:
    mcp.add_tool(tool)

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

@mcp.tool()
def get_storage_space_utilization():
    """
    Retrieves storage space utilization or the amount of data that is in all disk or cloud libraries, and the percentage of storage space that was saved because of compression and deduplication.
    Returns:
        A dictionary containing information about the storage space utilization.
    """
    try:
        api_response = commvault_api_client.get("cr/reportsplusengine/datasets/2b366703-52e1-4775-8047-1f4cfa13d2db/data?cache=true&parameter.i_dashboardtype=commcell&orderby='date to be full'&datasource=2")
        return format_report_dataset_response(api_response)
    except Exception as e:
        logger.error(f"Error retrieving storage space utilization: {e}")
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

@mcp.tool()
def get_schedules_list() -> dict:
    """
    Gets the list of schedules (filtered for relevant information).
    """
    try:
        response = commvault_api_client.get("Schedules")
        return filter_schedules_response(response)
    except Exception as e:
        logger.error(f"Error retrieving schedule list: {e}")
        return ToolError({"error": str(e)})
    
@mcp.tool()
def get_schedule_properties(schedule_id: Annotated[str, Field(description="The schedule id to retrieve properties for.")]) -> dict:
    """
    Gets properties for a given schedule id.
    """
    try:
        return commvault_api_client.get(f"Schedule/{schedule_id}")
    except Exception as e:
        logger.error(f"Error retrieving schedule properties: {e}")
        return ToolError({"error": str(e)})
    
@mcp.tool()
def enable_schedule(schedule_id: Annotated[str, Field(description="The schedule id to enable.")]) -> dict:
    """
    Enables a schedule with the given schedule id.
    """
    try:
        return commvault_api_client.post(f"/Schedules/task/Action/Enable", data={"taskId": schedule_id})
    except Exception as e:
        logger.error(f"Error enabling schedule: {e}")
        return ToolError({"error": str(e)})
    
@mcp.tool()
def disable_schedule(schedule_id: Annotated[str, Field(description="The schedule id to disable.")]) -> dict:
    """
    Disables a schedule with the given schedule id.
    """
    try:
        return commvault_api_client.post(f"/Schedules/task/Action/Disable", data={"taskId": schedule_id})
    except Exception as e:
        logger.error(f"Error disabling schedule: {e}")
        return ToolError({"error": str(e)})

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
def get_plan_list() -> dict:
    """
    Gets the list of plans.
    """
    try:
        response = commvault_api_client.get("v4/plan/summary")
        return response
    except Exception as e:
        logger.error(f"Error retrieving plan list: {e}")
        return ToolError({"error": str(e)})
    
@mcp.tool()
def get_plan_properties(plan_id: Annotated[str, Field(description="The plan id to retrieve properties for.")]) -> dict:
    """
    Gets properties for a given plan id.
    """
    try:
        return commvault_api_client.get(f"v4/plan/summary/{plan_id}")
    except Exception as e:
        logger.error(f"Error retrieving plan properties: {e}")
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

@mcp.tool()
def get_users_list() -> dict:
    """
    Gets the list of users in the CommCell.
    Returns:
        A dictionary containing the list of users.
    """
    try:
        response = commvault_api_client.get("v4/user")
        return filter_users_response(response)
    except Exception as e:
        logger.error(f"Error retrieving user list: {e}")
        return ToolError({"error": str(e)})
    
@mcp.tool()
def get_user_properties(user_id: Annotated[str, Field(description="The user id to retrieve properties for.")]) -> dict:
    """
    Gets properties for a given user id.
    """
    try:
        return commvault_api_client.get(f"v4/user/{user_id}")
    except Exception as e:
        logger.error(f"Error retrieving user properties: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def set_user_enabled(user_id: Annotated[str, Field(description="The user id to enable or disable.")], enabled: Annotated[bool, Field(description="Set to True to enable the user, False to disable.")]) -> dict:
    """
    Enables or disables a user with the given user id based on the 'enabled' flag.
    """
    try:
        action = "enable" if enabled else "disable"
        response = commvault_api_client.put(f"user/{user_id}/{action}")
        if response["response"][0].get("errorCode", -1) == 0:
            return {"message": f"User {action}d successfully."}
        else:
            error_message = response["response"][0].get("errorMessage", "Unknown error occurred.")
            raise Exception(f"Failed to {action} user: {error_message}")
    except Exception as e:
        logger.error(f"Error {'enabling' if enabled else 'disabling'} user: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_user_groups_list() -> dict:
    """
    Gets the list of user groups in the CommCell.
    Returns:
        A dictionary containing the list of user groups.
    """
    try:
        response = commvault_api_client.get("v4/usergroup")
        return filter_user_groups_response(response)
    except Exception as e:
        logger.error(f"Error retrieving user group list: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def get_user_group_properties(user_group_id: Annotated[str, Field(description="The user group id to retrieve properties for.")]) -> dict:
    """
    Gets properties for a given user group id.
    """
    try:
        return commvault_api_client.get(f"v4/usergroup/{user_group_id}")
    except Exception as e:
        logger.error(f"Error retrieving user group properties: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def set_user_group_assignment(
    user_id: Annotated[str, Field(description="The user id to assign to the user group.")], 
    user_group_id: Annotated[str, Field(description="The user group id to assign the user to.")], 
    assign: Annotated[bool, Field(description="Set to True to assign the user to the group, False to remove the user from the group.")]=True
    ) -> dict:
    """
    Assigns or removes a user from a user group based on the 'assign' flag.
    Set assign=True to add the user to the group, or assign=False to remove the user from the group.
    """
    try:
        operation = "ADD" if assign else "DELETE"
        payload = {
            "userGroupOperation": operation,
            "userGroups": [
                {
                    "id": user_group_id
                }
            ],
        }
        return commvault_api_client.put(f"v4/user/{user_id}", data=payload)
    except Exception as e:
        logger.error(f"Error assigning user {user_id} to user group {user_group_id}: {e}")
        return ToolError({"error": str(e)})
    
@mcp.tool()
def get_associated_entities_for_user_or_user_group(id: Annotated[str, Field(description="The user or user group id to retrieve associated entities for.")], type: Annotated[str, Field(description="Specify 'user' for user id or 'usergroup' for user group id.")]) -> dict:
    """
    Gets the associated entities (roles and permissions for each entity) for a given user or user group id.
    """
    try:
        response = commvault_api_client.get(f"{type.lower()}/{id}/security")
        return filter_security_associations_response(response)
    except Exception as e:
        logger.error(f"Error retrieving associated entities for user {id}: {e}")
        return ToolError({"error": str(e)})
    
@mcp.tool()
def view_entity_permissions(
    entity_type: Annotated[str, Field(description="The type of entity to view permissions for. Valid values are: COMMCELL_ENTITY, CLIENT_ENTITY, INSTANCE_ENTITY, BACKUPSET_ENTITY, SUBCLIENT_ENTITY, CLIENT_GROUP_ENTITY, USER_ENTITY, USERGROUP_ENTITY, LIBRARY_ENTITY, STORAGE_POLICY_ENTITY, STORAGE_POLICY_COPY_ENTITY, SUBCLIENT_POLICY_ENTITY.")],
    entity_id: Annotated[str, Field(description="The ID of the entity to view permissions for.")]
) -> dict:
    """
    Retrieves permissions the user has for a specific entity type and ID.
    """
    try:
        response = commvault_api_client.get(f"Security/{entity_type}/{entity_id}/Permissions")
        return response
    except Exception as e:
        logger.error(f"Error retrieving permissions for entity {entity_type} with ID {entity_id}: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def grant_or_revoke_access_to_entity(
    entity_id: Annotated[str, Field(description="The ID of the entity to grant access to.")],
    entity_type: Annotated[str, Field(description="The type of the entity to grant access to. Valid values: 'client', 'client_group', 'agent', 'instance', 'backup_set', 'subclient', 'storage_policy', 'schedule_policy', 'alert', 'workflow', 'plan'.")],
    role_id: Annotated[int, Field(description="The role ID to assign. You can get the role ID using the get_roles_list tool or ask the user to provide it.")],
    user_id: Annotated[str, Field(description="The user ID to grant access to.")],
    assign: Annotated[bool, Field(description="Set to True to grant access, False to revoke access. Default is True.")]=True
) -> dict:
    """
    Grants or revokes access to an entity for a user with a specific role.
    """
    ENTITY_TYPE_MAP = {
        "client": 3,
        "client_group": 28,
        "agent": 4,
        "instance": 5,
        "backup_set": 6,
        "subclient": 7,
        "storage_policy": 17,
        "schedule_policy": 35,
        "alert": 64,
        "workflow": 83,
        "plan": 158,
    }
    try:
        entity_type_num = ENTITY_TYPE_MAP.get(entity_type.lower())
        if entity_type_num is None:
            raise ValueError(f"Invalid entity_type: {entity_type}")
        payload = {
            "entityAssociated": {
                "entity": [
                    {
                        "entityType": entity_type_num,
                        "_type_": entity_type_num if entity_type.lower() != "plan" else 150, # plan uses a different _type_
                        "entityId":entity_id
                    }
                ]
            },
            "securityAssociations": {
                "associationsOperationType": "ADD" if assign else "DELETE",
                "associations": [
                    {
                        "userOrGroup": [
                            {
                                "userId": user_id
                            }
                        ],
                        "properties": {
                            "role": {
                                "roleId": role_id
                            }
                        }
                    }
                ]
            }
        }
        return commvault_api_client.post("Security", data=payload)
    except Exception as e:
        logger.error(f"Error granting/revoking access to entity {entity_id}: {e}")
        return ToolError({"error": str(e)})
    
@mcp.tool()
def get_roles_list() -> dict:
    """
    Gets the list of roles in the CommCell.
    """
    try:
        response = commvault_api_client.get("v4/role")
        return response
    except Exception as e:
        logger.error(f"Error retrieving roles list: {e}")
        return ToolError({"error": str(e)})

@mcp.tool()
def run_backup_for_subclient(
    subclient_id: Annotated[str, Field(description="The subclient id to run backup for.")],
    backup_type: Annotated[str, Field(description="The type of backup to run. Valid values are 'Full', 'INCREMENTAL', 'SYNTHETIC_FULL'")],
) -> dict:
    """
    Runs a backup job for the specified subclient with the given backup type.
    """
    try:
        params = {
            "backupLevel": backup_type
        }
        return commvault_api_client.post(
            f"subclient/{subclient_id}/action/backup",
            params=params
        )
    except Exception as e:
        logger.error(f"Error running backup for subclient {subclient_id}: {e}")
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