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

from fastmcp.exceptions import ToolError
from typing import Annotated
from pydantic import Field

from src.cv_api_client import commvault_api_client
from src.logger import logger


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
    
def get_plan_properties(plan_id: Annotated[str, Field(description="The plan id to retrieve properties for.")]) -> dict:
    """
    Gets properties for a given plan id.
    """
    try:
        return commvault_api_client.get(f"v4/plan/summary/{plan_id}")
    except Exception as e:
        logger.error(f"Error retrieving plan properties: {e}")
        return ToolError({"error": str(e)})
    
PLAN_MANAGEMENT_TOOLS = [
    get_plan_list,
    get_plan_properties
]