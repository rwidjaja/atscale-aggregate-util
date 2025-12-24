# main.py (updated for command line arguments)
import sys
import argparse
from rebuild_manager import RebuildManager
from report_generator import ReportGenerator
from config import get_jwt, clear_jwt_cache


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='ATSCALE AGGREGATE MANAGEMENT TOOL')
    
    parser.add_argument(
        '--project-id', 
        help='Project/Catalog ID (required for direct export)'
    )
    parser.add_argument(
        '--cube-id', 
        help='Cube/Model ID (required for direct export)'
    )
    parser.add_argument(
        '--export-csv', 
        action='store_true',
        help='Export aggregates to CSV directly (requires --project-id and --cube-id)'
    )
    parser.add_argument(
        '--list-aggregates', 
        action='store_true',
        help='List aggregates with details directly (requires --project-id and --cube-id)'
    )
    parser.add_argument(
        '--list-projects', 
        action='store_true',
        help='List all published projects/catalogs and exit'
    )
    
    return parser.parse_args()


def direct_export_csv(project_id: str, cube_id: str) -> None:
    """Export aggregates to CSV directly without menu interaction"""
    report_generator = ReportGenerator()
    
    try:
        print(f"\nDirect CSV export for project: {project_id}, cube: {cube_id}")
        print("Fetching project information...")
        
        # First, try to get project name from the API
        projects = report_generator.api_client.get_published_projects()
        
        project_name = "Unknown Project"
        cube_name = "Unknown Cube"
        
        for project in projects:
            if project.get("id") == project_id:
                project_name = project.get("name", "Unknown Project")
                for cube in project.get("cubes", []):
                    if cube.get("id") == cube_id:
                        cube_name = cube.get("name", "Unknown Cube")
                        break
                break
        
        cube_data = {
            "display": f"{project_name}::{cube_name}",
            "project_name": project_name,
            "project_id": project_id,
            "cube_name": cube_name,
            "cube_id": cube_id
        }
        
        print(f"Found: {cube_data['display']}")
        print("Exporting to CSV...")
        
        # Call the export function directly
        report_generator.aggregate_reporter.export_cube_aggregates_csv(cube_data)
        
    except Exception as e:
        print(f"Error during direct export: {e}")
        sys.exit(1)


def direct_list_aggregates(project_id: str, cube_id: str) -> None:
    """List aggregates directly without menu interaction"""
    report_generator = ReportGenerator()
    
    try:
        print(f"\nDirect list aggregates for project: {project_id}, cube: {cube_id}")
        print("Fetching project information...")
        
        projects = report_generator.api_client.get_published_projects()
        
        project_name = "Unknown Project"
        cube_name = "Unknown Cube"
        
        for project in projects:
            if project.get("id") == project_id:
                project_name = project.get("name", "Unknown Project")
                for cube in project.get("cubes", []):
                    if cube.get("id") == cube_id:
                        cube_name = cube.get("name", "Unknown Cube")
                        break
                break
        
        cube_data = {
            "display": f"{project_name}::{cube_name}",
            "project_name": project_name,
            "project_id": project_id,
            "cube_name": cube_name,
            "cube_id": cube_id
        }
        
        print(f"Found: {cube_data['display']}")
        print("Fetching aggregates...")
        
        # Call the list function directly
        report_generator.aggregate_reporter.list_cube_aggregates(cube_data)
        
    except Exception as e:
        print(f"Error during direct list: {e}")
        sys.exit(1)


def list_all_projects() -> None:
    """List all published projects/catalogs and their cubes/models"""
    report_generator = ReportGenerator()
    
    try:
        print("\nFetching all published projects/catalogs...")
        projects = report_generator.api_client.get_published_projects()
        
        if not projects:
            print("No published projects found.")
            return
        
        print(f"\nFound {len(projects)} project(s):")
        print("=" * 80)
        
        for i, project in enumerate(projects, 1):
            project_id = project.get("id", "N/A")
            project_name = project.get("name", "Unknown Project")
            cubes = project.get("cubes", [])
            
            print(f"\n{i}. {project_name}")
            print(f"   ID: {project_id}")
            print(f"   Cubes/Models: {len(cubes)}")
            
            for j, cube in enumerate(cubes, 1):
                cube_id = cube.get("id", "N/A")
                cube_name = cube.get("name", "Unknown Cube")
                print(f"   {j}. {cube_name} (ID: {cube_id})")
        
        print("\n" + "=" * 80)
        print("To export directly, use:")
        print(f"  python main.py --project-id PROJECT_ID --cube-id CUBE_ID --export-csv")
        
    except Exception as e:
        print(f"Error listing projects: {e}")
        sys.exit(1)


def main_menu() -> None:
    """Display main menu with simplified options"""
    rebuild_manager = RebuildManager()
    report_generator = ReportGenerator()

    while True:
        print("\n" + "="*50)
        print("ATSCALE AGGREGATE MANAGEMENT")
        print("="*50)
        print("1. Refresh Token")
        print("2. Aggregate Rebuild")
        print("3. Aggregate Report")
        print("4. Exit")
        print("-"*50)

        choice = input("\nSelect option (1-4): ").strip()

        if choice == "1":
            refresh_token_action()
        elif choice == "2":
            rebuild_manager.rebuild_cube()
        elif choice == "3":
            report_generator.generate_report()
        elif choice == "4":
            print("\nExiting...")
            break
        elif choice.lower() == "q":
            print("\nExiting...")
            break
        else:
            print("Invalid choice. Please select 1-4.")


def refresh_token_action() -> None:
    """Refresh JWT token"""
    clear_jwt_cache()
    try:
        token = get_jwt(force_refresh=True)
        print("\n✓ Token refreshed successfully")
        print(f"Token preview: {token[:50]}...")
    except Exception as e:
        print(f"\n✗ Error refreshing token: {e}")


if __name__ == "__main__":
    args = parse_arguments()
    
    # Handle command line arguments
    if args.list_projects:
        list_all_projects()
        sys.exit(0)
    
    elif args.export_csv:
        if not args.project_id or not args.cube_id:
            print("ERROR: --export-csv requires both --project-id and --cube-id")
            print("\nUsage examples:")
            print("  python main.py --export-csv --project-id 39e90725-98d4-5a17-aedd-02568e197062 --cube-id e20faf8b-9939-5fb2-96ee-07cfec79dc35")
            print("\nTo see available projects and cubes:")
            print("  python main.py --list-projects")
            sys.exit(1)
        direct_export_csv(args.project_id, args.cube_id)
        sys.exit(0)
    
    elif args.list_aggregates:
        if not args.project_id or not args.cube_id:
            print("ERROR: --list-aggregates requires both --project-id and --cube-id")
            print("\nUsage examples:")
            print("  python main.py --list-aggregates --project-id 39e90725-98d4-5a17-aedd-02568e197062 --cube-id e20faf8b-9939-5fb2-96ee-07cfec79dc35")
            print("\nTo see available projects and cubes:")
            print("  python main.py --list-projects")
            sys.exit(1)
        direct_list_aggregates(args.project_id, args.cube_id)
        sys.exit(0)
    
    # If no command line arguments, run the interactive menu
    else:
        try:
            main_menu()
        except KeyboardInterrupt:
            print("\n\nProgram terminated by user.")
            sys.exit(0)
        except Exception as e:
            print(f"\nFatal error: {e}")
            sys.exit(1)