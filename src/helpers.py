def transform_sla_data(api_response):
    """
    Transform SLA Data API response to a simplified format with SLA percentage.
    
    Args:
        api_response (dict): The original API response
        
    Returns:
        dict: Simplified data with SLA percentage
    """
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

def compute_security_score(api_response):
    params = [
        p
        for cat in api_response["securityCategories"]
        for p in cat["parameter"]
    ]
    total = len(params)
    failures = sum(1 for p in params if p["status"] == 2)
    return round((total - failures) / total * 100)
