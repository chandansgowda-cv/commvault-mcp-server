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
