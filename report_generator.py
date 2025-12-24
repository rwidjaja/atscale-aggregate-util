# report_generator.py
from typing import Dict, List
from api_client import AtScaleAPIClient
from ui_components import SimpleListSelector, confirm_action
from cube_aggregate_reporter import CubeAggregateReporter
from aggregate_statistics import AggregateStatistics
from aggregate_health_checker import AggregateHealthChecker
from aggregate_build_history import AggregateBuildHistory


class ReportGenerator:
    def __init__(self):
        self.api_client = AtScaleAPIClient()
        self.aggregate_reporter = CubeAggregateReporter(self.api_client)
        self.aggregate_stats = AggregateStatistics(self.api_client)
        self.aggregate_health = AggregateHealthChecker(self.api_client)
        self.build_history = AggregateBuildHistory(self.api_client)

    def generate_report(self) -> None:
        """Generate aggregate report with cube selection first"""
        try:
            print("\nLoading published projects and cubes...")
            # USE THE CORRECT API CLIENT METHOD
            projects = self.api_client.get_published_projects()
            
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
                    
                    # Format: Project::Cube
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
                title="Select Cube for Aggregate Report"
            )
            
            selected_cube = selector.select()
            if not selected_cube:
                print("\nNo cube selected.")
                return
            
            print(f"\nSelected: {selected_cube['display']}")
            print(f"Project ID: {selected_cube['project_id']}")
            print(f"Cube ID: {selected_cube['cube_id']}")
            
            # Show report options for the selected cube
            self.show_cube_report_options(selected_cube)
                
        except Exception as e:
            print(f"Error: {e}")

    def show_cube_report_options(self, cube_data: Dict) -> None:
        """Show report options for a specific cube"""
        print(f"\nReport Options for: {cube_data['display']}")
        print("-" * 50)
        
        report_options = [
            "List aggregates with details",
            "Export aggregates to CSV",
            "Show aggregate statistics",
            "Check aggregate health",
            "Aggregate Build history",
            "Back to Main Menu"
        ]
        
        while True:
            selector = SimpleListSelector(report_options, title="Select Report Type")
            selected = selector.select()
            
            if not selected:
                return
            
            if selected == "List aggregates with details":
                self.aggregate_reporter.list_cube_aggregates(cube_data)
            elif selected == "Export aggregates to CSV":
                self.aggregate_reporter.export_cube_aggregates_csv(cube_data)
            elif selected == "Show aggregate statistics":
                self.aggregate_stats.show_cube_aggregate_statistics(cube_data)
            elif selected == "Check aggregate health":
                self.aggregate_health.check_cube_aggregate_health(cube_data)
            elif selected == "Aggregate Build history":
                self.build_history.show_build_history(cube_data)
            elif selected == "Back to Main Menu":
                return
            
            # Ask if user wants to run another report
            if not confirm_action("\nRun another report for this cube?"):
                break