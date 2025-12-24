import requests
from typing import Dict, List, Optional, Any
from config import get_jwt, get_container_jwt, load_config


class AtScaleAPIClient:
    def __init__(self):
        self.config = load_config()
        self.base_url = self._get_base_url()
        
    def _get_base_url(self) -> str:
        """Get base URL based on instance type"""
        host = self.config["host"]
        if self.config.get("instance_type") == "installer":
            org = self.config["organization"]
            return f"https://{host}:10500/{org}"
        else:  # container
            return f"https://{host}"
    
    def _get_public_headers(self) -> Dict[str, str]:
        """Get headers for public API (uses static token)"""
        headers = {
            "Authorization": f"Bearer {get_jwt()}",  # Static token for container
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        return headers
    
    def _get_private_headers(self) -> Optional[Dict[str, str]]:
        """Get headers for private API (uses JWT via OIDC)"""
        if self.config.get("instance_type") != "container":
            return self._get_public_headers()
        
        # For container, get JWT for private API
        container_jwt = get_container_jwt()
        if not container_jwt:
            return None
        
        # For GET requests, don't include Content-Type
        return {
            "Authorization": f"Bearer {container_jwt}"
            # No Content-Type for GET
            # No Accept to match curl exactly
        }

    def get_published_projects(self) -> List[Dict]:
        """Get published catalogs with models - PUBLIC API"""
        if self.config.get("instance_type") == "installer":
            host = self.config["host"]
            org = self.config["organization"]
            url = f"https://{host}:10502/projects/published/orgId/{org}"
            headers = self._get_public_headers()
        else:
            # CONTAINER PUBLIC API ENDPOINT
            url = f"{self.base_url}/v1/catalogs"
            headers = self._get_public_headers()
        
        response = requests.get(
            url, headers=headers, verify=False, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if self.config.get("instance_type") == "installer":
            return data.get("response", [])
        else:
            return self._transform_container_catalogs(data)
    
    def _transform_container_catalogs(self, catalogs_data: List[Dict]) -> List[Dict]:
        """Transform /v1/catalogs response to match installer format"""
        transformed = []
        
        for catalog in catalogs_data:
            catalog_id = catalog.get("id", "")
            catalog_name = catalog.get("name", "Unknown Catalog")
            
            cubes = []
            for model in catalog.get("models", []):
                cubes.append({
                    "id": model.get("id", ""),
                    "name": model.get("name", "Unknown Cube"),
                    "caption": model.get("caption", ""),
                    "type": "model"
                })
            
            transformed.append({
                "id": catalog_id,
                "name": catalog_name,
                "cubes": cubes
            })
        
        return transformed

    def get_aggregates_by_cube(self, catalog_id: str, model_id: str, limit: int = 200) -> Dict:
        """Get aggregates for a specific cube/model - PUBLIC API"""
        if self.config.get("instance_type") == "installer":
            host = self.config["host"]
            org = self.config["organization"]
            url = f"https://{host}:10502/aggregates/orgId/{org}?limit={limit}&projectId={catalog_id}&cubeId={model_id}"
        else:
            # CONTAINER PUBLIC API ENDPOINT
            url = f"{self.base_url}/v1/aggregates/instances?catalogId={catalog_id}&modelId={model_id}"
        
        response = requests.get(
            url, headers=self._get_public_headers(), verify=False, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if self.config.get("instance_type") == "installer":
            return data
        else:
            return self._transform_container_aggregates(data, catalog_id, model_id)
    
    def _transform_container_aggregates(self, container_data: Dict, catalog_id: str, model_id: str) -> Dict:
        """Transform /v1/aggregates/instances response to match installer format"""
        aggregates = container_data.get("data", [])
        
        transformed_aggregates = []
        for agg in aggregates:
            stats = agg.get("stats", {})
            
            transformed = {
                "id": agg.get("definitionId", ""),
                "name": agg.get("definitionId", ""),
                "type": "system_defined",
                "subtype": "prediction_defined",
                "attributes": [],
                "project_id": agg.get("catalogId", catalog_id),
                "cube_id": agg.get("modelId", model_id),
                "connection_id": agg.get("connectionId", ""),
                "incremental": False,
                "stats": {
                    "created_at": "",
                    "average_build_duration": stats.get("buildDuration", 0),
                    "query_utilization": 0,
                    "most_recent_query": ""
                },
                "latest_instance": {
                    "id": agg.get("id", ""),
                    "status": agg.get("status", "unknown"),
                    "message": agg.get("message", ""),
                    "table_name": agg.get("tableName", ""),
                    "table_schema": agg.get("tableSchema", ""),
                    "batch_id": agg.get("buildQueryId", ""),
                    "connection_id": agg.get("connectionId", ""),
                    "stats": {
                        "materialization_start_time": stats.get("materializationStartTime", ""),
                        "materialization_end_time": stats.get("materializationEndTime", ""),
                        "build_duration": stats.get("buildDuration", 0),
                        "number_of_rows": stats.get("numberOfRows", 0)
                    }
                },
                "active_instance": {
                    "id": agg.get("id", ""),
                    "status": agg.get("status", "unknown"),
                    "message": agg.get("message", ""),
                    "table_name": agg.get("tableName", ""),
                    "table_schema": agg.get("tableSchema", ""),
                    "batch_id": agg.get("buildQueryId", ""),
                    "connection_id": agg.get("connectionId", ""),
                    "stats": stats
                }
            }
            transformed_aggregates.append(transformed)
        
        return {
            "response": {
                "data": transformed_aggregates,
                "total": len(aggregates),
                "limit": 200,
                "offset": 0
            }
        }

    def rebuild_cube(self, catalog_id: str, model_id: str, is_full_build: bool = True) -> Dict:
        """Rebuild aggregates for a cube - PUBLIC API"""
        if self.config.get("instance_type") == "installer":
            host = self.config["host"]
            org = self.config["organization"]
            url = f"https://{host}:10502/aggregate-batch/orgId/{org}/projectId/{catalog_id}?cubeId={model_id}&isFullBuild={str(is_full_build).lower()}"
            
            response = requests.post(
                url, headers=self._get_public_headers(), verify=False, timeout=60
            )
        else:
            # CONTAINER PUBLIC API ENDPOINT
            url = f"{self.base_url}/v1/aggregates-batch/catalogs/{catalog_id}/models/{model_id}?isFullBuild={str(is_full_build).lower()}"
            
            data = {"gracePeriodOverrides": {}}
            
            response = requests.post(
                url, headers=self._get_public_headers(), json=data, verify=False, timeout=60
            )
        
        response.raise_for_status()
        return response.json()

    def get_aggregate_build_history(self, catalog_id: str, model_id: str, limit: int = 20) -> Dict:
        """Get aggregate build history - PRIVATE API (requires JWT for container)"""
        if self.config.get("instance_type") == "installer":
            host = self.config["host"]
            org = self.config["organization"]
            url = f"https://{host}:10502/aggregate-batch/orgId/{org}/history?limit={limit}&projectId={catalog_id}&cubeId={model_id}"
            headers = self._get_public_headers()
        else:
            # CONTAINER PRIVATE API ENDPOINT - requires JWT
            url = f"{self.base_url}/wapi/p/aggregate/batch-history?page=1&limit={limit}&catalogId={catalog_id}&modelId={model_id}"
            
            container_jwt = get_container_jwt()
            if not container_jwt:
                print("⚠️  Build history unavailable: Container instance requires client_id and client_secret in config.json for private API access")
                return {
                    "response": {
                        "data": [],
                        "total": 0,
                        "limit": limit,
                        "offset": 0
                    }
                }
            
            # GET requests shouldn't have Content-Type header
            headers = {
                "Authorization": f"Bearer {container_jwt}"
            }
        
        try:
            response = requests.get(
                url, headers=headers, verify=False, timeout=30
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request failed with status {e.response.status_code if e.response else 'N/A'}")
            print(f"URL: {url}")
            if e.response:
                print(f"Response: {e.response.text[:200]}")
            raise
        
        data = response.json()
        
        if self.config.get("instance_type") == "installer":
            return data
        else:
            # Transform container build history response
            return self._transform_container_build_history(data)
    
    def _transform_container_build_history(self, container_data: Dict) -> Dict:
        """Transform container build history response"""
        history_data = container_data.get("data", [])
        total = container_data.get("total", 0)
        
        # The container response already has the right field names
        # We don't need to transform field names, just pass them through
        # But we need to ensure all expected fields are present
        
        transformed_history = []
        for batch in history_data:
            # Create a new dict with all the original fields
            # This ensures we don't have any reference issues
            transformed_batch = dict(batch)
            
            # Add any aliases if needed
            transformed_batch["batchId"] = transformed_batch.get("id", "")
            
            transformed_history.append(transformed_batch)
        
        return {
            "response": {
                "data": transformed_history,
                "total": total,
                "limit": container_data.get("limit", 20),
                "offset": container_data.get("offset", 0)
            }
        }

    # Other methods remain similar but use _get_public_headers() for container
    def get_aggregates(self) -> List[Dict]:
        """Get list of all aggregates - PUBLIC API"""
        if self.config.get("instance_type") == "installer":
            url = f"{self.base_url}/aggregates"
        else:
            url = f"{self.base_url}/v1/aggregates/instances"
        
        response = requests.get(
            url, headers=self._get_public_headers(), verify=False, timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_aggregate_details(self, aggregate_id: str) -> Dict:
        """Get details of a specific aggregate - PUBLIC API"""
        if self.config.get("instance_type") == "installer":
            url = f"{self.base_url}/aggregates/{aggregate_id}"
        else:
            url = f"{self.base_url}/v1/aggregates/instances/{aggregate_id}"
        
        response = requests.get(
            url, headers=self._get_public_headers(), verify=False, timeout=30
        )
        response.raise_for_status()
        return response.json()

    def create_aggregate(self, aggregate_data: Dict[str, Any]) -> Dict:
        """Create a new aggregate - PUBLIC API"""
        if self.config.get("instance_type") == "installer":
            url = f"{self.base_url}/aggregates"
        else:
            url = f"{self.base_url}/v1/aggregates/definitions"
        
        response = requests.post(
            url, headers=self._get_public_headers(), json=aggregate_data, verify=False, timeout=30
        )
        response.raise_for_status()
        return response.json()

    def update_aggregate(self, aggregate_id: str, aggregate_data: Dict[str, Any]) -> Dict:
        """Update an existing aggregate - PUBLIC API"""
        if self.config.get("instance_type") == "installer":
            url = f"{self.base_url}/aggregates/{aggregate_id}"
        else:
            url = f"{self.base_url}/v1/aggregates/definitions/{aggregate_id}"
        
        response = requests.put(
            url, headers=self._get_public_headers(), json=aggregate_data, verify=False, timeout=30
        )
        response.raise_for_status()
        return response.json()

    def delete_aggregate(self, aggregate_id: str) -> bool:
        """Delete an aggregate - PUBLIC API"""
        if self.config.get("instance_type") == "installer":
            url = f"{self.base_url}/aggregates/{aggregate_id}"
        else:
            url = f"{self.base_url}/v1/aggregates/definitions/{aggregate_id}"
        
        response = requests.delete(
            url, headers=self._get_public_headers(), verify=False, timeout=30
        )
        return response.status_code == 200

    def refresh_aggregate(self, aggregate_id: str) -> Dict:
        """Refresh/rebuild a specific aggregate - PUBLIC API"""
        if self.config.get("instance_type") == "installer":
            url = f"{self.base_url}/aggregates/{aggregate_id}/refresh"
        else:
            url = f"{self.base_url}/v1/aggregates/instances/{aggregate_id}/refresh"
        
        response = requests.post(
            url, headers=self._get_public_headers(), verify=False, timeout=30
        )
        response.raise_for_status()
        return response.json()