# rebuild_manager.py - UPDATED TO USE API CLIENT
from typing import List, Dict, Optional
from api_client import AtScaleAPIClient
from ui_components import SimpleListSelector, confirm_action


class RebuildManager:
    def __init__(self):
        # USE API CLIENT INSTEAD OF DIRECT REQUESTS
        self.api_client = AtScaleAPIClient()
    
    def get_published_projects(self) -> List[Dict]:
        """Get list of published projects with cubes - USE API CLIENT"""
        # DELEGATE TO THE CORRECT API CLIENT METHOD
        return self.api_client.get_published_projects()

    def rebuild_cube(self) -> None:
        """Interactive flow to select and rebuild a cube"""
        try:
            print("\nLoading published projects and cubes...")
            projects = self.get_published_projects()
            
            if not projects:
                print("No published projects found.")
                return
            
            # Create list of project::cube options
            cube_options = []
            
            for project in projects:
                project_name = project.get("name", "Unknown Project")
                project_id = project.get("id", "")
                
                cubes = project.get("cubes", [])
                for cube in cubes:
                    cube_name = cube.get("name", "Unknown Cube")
                    cube_id = cube.get("id", "")
                    
                    display_name = f"{project_name}::{cube_name}"
                    cube_options.append({
                        "display": display_name,
                        "project_name": project_name,
                        "project_id": project_id,
                        "cube_name": cube_name,
                        "cube_id": cube_id
                    })
            
            if not cube_options:
                print("No cubes found in published projects.")
                return
            
            # Create simple selector for cubes
            selector = SimpleListSelector(
                cube_options,
                title="Select Cube to Rebuild"
            )
            
            selected_cube = selector.select()
            if not selected_cube:
                print("\nNo cube selected.")
                return
            
            print(f"\nSelected: {selected_cube['display']}")
            print(f"Project ID: {selected_cube['project_id']}")
            print(f"Cube ID: {selected_cube['cube_id']}")
            
            # Ask for confirmation
            if confirm_action(f"Rebuild cube '{selected_cube['display']}'? (Full build)"):
                # USE API CLIENT INSTEAD OF DIRECT CALL
                self.execute_rebuild(
                    selected_cube["project_id"], 
                    selected_cube["cube_id"]
                )
                
        except Exception as e:
            print(f"Error: {e}")

    def execute_rebuild(self, project_id: str, cube_id: str) -> None:
        """Execute the rebuild API call - USE API CLIENT"""
        try:
            print(f"\nSending rebuild request for project {project_id}, cube {cube_id}...")
            
            # USE THE API CLIENT METHOD WITH CORRECT ENDPOINTS
            result = self.api_client.rebuild_cube(project_id, cube_id, is_full_build=True)
            
            print("\n✓ Rebuild request successful!")
            print(f"Response: {result}")
                
        except Exception as e:
            print(f"\n✗ Rebuild request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status code: {e.response.status_code}")
                print(f"Response: {e.response.text[:200]}...")