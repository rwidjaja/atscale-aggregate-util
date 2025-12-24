# aggregate_manager.py
import json
from typing import Dict, List, Optional
from api_client import AtScaleAPIClient
from ui_components import ScrollableList, display_table, confirm_action


class AggregateManager:
    def __init__(self):
        self.api_client = AtScaleAPIClient()

    def list_aggregates(self, detailed: bool = False) -> None:
        """List all aggregates"""
        try:
            aggregates = self.api_client.get_aggregates()
            if not aggregates:
                print("No aggregates found.")
                return

            if detailed:
                # Display detailed table view
                columns = ["id", "name", "status", "size", "last_refresh"]
                display_data = []
                for agg in aggregates:
                    display_data.append({
                        "id": agg.get("id", "")[:20] + "...",
                        "name": agg.get("name", ""),
                        "status": agg.get("status", "unknown"),
                        "size": self._format_size(agg.get("size", 0)),
                        "last_refresh": agg.get("last_refresh_time", "never")
                    })
                display_table(display_data, columns)
            else:
                # Simple list for selection
                print(f"\nFound {len(aggregates)} aggregates:")
                for i, agg in enumerate(aggregates, 1):
                    print(f"{i:3d}. {agg.get('name', 'Unnamed')} "
                          f"(ID: {agg.get('id', 'N/A')[:20]}...)")

        except Exception as e:
            print(f"Error fetching aggregates: {e}")

    def select_aggregate(self) -> Optional[Dict]:
        """Select an aggregate from a scrollable list"""
        try:
            aggregates = self.api_client.get_aggregates()
            if not aggregates:
                print("No aggregates found.")
                return None

            # Create scrollable list
            list_ui = ScrollableList(
                aggregates,
                title="Select an Aggregate",
                page_size=15
            )

            selected = list_ui.navigate()
            return selected

        except Exception as e:
            print(f"Error: {e}")
            return None

    def show_aggregate_details(self, aggregate_id: str) -> None:
        """Display detailed information about an aggregate"""
        try:
            details = self.api_client.get_aggregate_details(aggregate_id)
            print("\n" + "="*60)
            print("AGGREGATE DETAILS")
            print("="*60)
            print(json.dumps(details, indent=2, default=str))
        except Exception as e:
            print(f"Error fetching details: {e}")

    def delete_aggregate(self, aggregate_id: str, aggregate_name: str) -> bool:
        """Delete an aggregate with confirmation"""
        if confirm_action(f"Delete aggregate '{aggregate_name}'?"):
            try:
                success = self.api_client.delete_aggregate(aggregate_id)
                if success:
                    print(f"Aggregate '{aggregate_name}' deleted successfully.")
                else:
                    print(f"Failed to delete aggregate '{aggregate_name}'.")
                return success
            except Exception as e:
                print(f"Error deleting aggregate: {e}")
                return False
        return False

    def refresh_aggregate(self, aggregate_id: str, aggregate_name: str) -> None:
        """Refresh/rebuild an aggregate"""
        if confirm_action(f"Refresh aggregate '{aggregate_name}'?"):
            try:
                result = self.api_client.refresh_aggregate(aggregate_id)
                print(f"Aggregate refresh initiated: {result}")
            except Exception as e:
                print(f"Error refreshing aggregate: {e}")

    def create_aggregate(self) -> None:
        """Create a new aggregate (interactive)"""
        print("\nCreate New Aggregate")
        print("-" * 40)

        name = input("Aggregate name: ").strip()
        cube_id = input("Cube ID: ").strip()
        description = input("Description (optional): ").strip()

        print("\nDefine aggregate columns (enter 'done' when finished):")
        columns = []
        while True:
            col = input("Column name (or 'done'): ").strip()
            if col.lower() == "done":
                break
            if col:
                columns.append(col)

        if not columns:
            print("At least one column is required.")
            return

        aggregate_data = {
            "name": name,
            "cube_id": cube_id,
            "columns": columns,
            "description": description,
            "status": "enabled"
        }

        if confirm_action(f"Create aggregate '{name}'?"):
            try:
                result = self.api_client.create_aggregate(aggregate_data)
                print(f"Aggregate created successfully: {result}")
            except Exception as e:
                print(f"Error creating aggregate: {e}")

    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human-readable format"""
        if size_bytes == 0:
            return "0 B"
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {units[i]}"