# cube_aggregate_reporter.py
import csv
import os
from datetime import datetime
from typing import Dict, List
from ui_components import display_table


class CubeAggregateReporter:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def list_cube_aggregates(self, cube_data: Dict) -> None:
        """List aggregates for a specific cube"""
        try:
            print("\nFetching aggregates for cube...")
            response = self.api_client.get_aggregates_by_cube(
                cube_data["project_id"], 
                cube_data["cube_id"]
            )
            
            aggregates_data = response.get("response", {}).get("data", [])
            
            if not aggregates_data:
                print(f"No aggregates found for {cube_data['display']}.")
                return
            
            total_aggregates = response.get("response", {}).get("total", 0)
            print(f"\nFound {len(aggregates_data)} aggregates (Total: {total_aggregates})")
            
            # Display in table format
            columns = ["ID (short)", "Name", "Type", "Status", "Rows", "Build Time", "Last Query"]
            display_data = []
            
            for agg in aggregates_data:
                agg_id = agg.get("id", "N/A")
                latest_instance = agg.get("latest_instance", {})
                stats = latest_instance.get("stats", {})
                agg_stats = agg.get("stats", {})
                
                # Calculate build time
                build_duration = stats.get("build_duration", 0)
                build_time_str = f"{build_duration}ms"
                if build_duration > 1000:
                    build_time_str = f"{build_duration/1000:.1f}s"
                
                # Format last query time
                last_query = agg_stats.get("most_recent_query", "Never")
                if last_query != "Never":
                    try:
                        query_date = datetime.fromisoformat(last_query.replace('Z', '+00:00'))
                        last_query = query_date.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                
                display_data.append({
                    "ID (short)": agg_id[:12] + "...",
                    "Name": agg.get("name", "Unnamed")[:30],
                    "Type": agg.get("type", "unknown"),
                    "Status": latest_instance.get("status", "unknown"),
                    "Rows": stats.get("number_of_rows", 0),
                    "Build Time": build_time_str,
                    "Last Query": last_query[:15] + "..." if len(last_query) > 15 else last_query
                })
            
            display_table(display_data, columns)
            
            # Show summary
            self._print_cube_summary(aggregates_data, cube_data["display"])
            
        except Exception as e:
            print(f"Error: {e}")
    
    def export_cube_aggregates_csv(self, cube_data: Dict) -> None:
        """Export cube aggregates to CSV file"""
        try:
            print("\nFetching aggregates for cube...")
            response = self.api_client.get_aggregates_by_cube(
                cube_data["project_id"], 
                cube_data["cube_id"]
            )
            
            aggregates_data = response.get("response", {}).get("data", [])
            
            if not aggregates_data:
                print(f"No aggregates found for {cube_data['display']}.")
                return
            
            # Create filename with timestamp and cube name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_cube_name = "".join(c for c in cube_data['display'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"aggregates_{safe_cube_name}_{timestamp}.csv"
            
            # Define CSV columns
            fieldnames = [
                "aggregate_id", "aggregate_name", "type", "subtype", 
                "status", "rows", "build_duration_ms", "avg_build_duration_ms",
                "query_utilization", "last_query_time", "created_at",
                "table_name", "table_schema", "batch_id", "connection_id",
                "key_count", "measure_count", "dimension_count", "total_attributes"
            ]
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for agg in aggregates_data:
                    latest_instance = agg.get("latest_instance", {})
                    instance_stats = latest_instance.get("stats", {})
                    agg_stats = agg.get("stats", {})
                    
                    # Count attribute types
                    attributes = agg.get("attributes", [])
                    key_count = sum(1 for a in attributes if a.get("type") == "key")
                    measure_count = sum(1 for a in attributes if a.get("type") == "measure")
                    dimension_count = sum(1 for a in attributes if a.get("type") == "dimension")
                    
                    row = {
                        "aggregate_id": agg.get("id", ""),
                        "aggregate_name": agg.get("name", ""),
                        "type": agg.get("type", ""),
                        "subtype": agg.get("subtype", ""),
                        "status": latest_instance.get("status", ""),
                        "rows": instance_stats.get("number_of_rows", 0),
                        "build_duration_ms": instance_stats.get("build_duration", 0),
                        "avg_build_duration_ms": agg_stats.get("average_build_duration", 0),
                        "query_utilization": agg_stats.get("query_utilization", 0),
                        "last_query_time": agg_stats.get("most_recent_query", ""),
                        "created_at": agg_stats.get("created_at", ""),
                        "table_name": latest_instance.get("table_name", ""),
                        "table_schema": latest_instance.get("table_schema", ""),
                        "batch_id": latest_instance.get("batch_id", ""),
                        "connection_id": latest_instance.get("connection_id", ""),
                        "key_count": key_count,
                        "measure_count": measure_count,
                        "dimension_count": dimension_count,
                        "total_attributes": len(attributes)
                    }
                    writer.writerow(row)
            
            print(f"\n✓ Report exported successfully: {filename}")
            print(f"Total aggregates: {len(aggregates_data)}")
            print(f"File size: {os.path.getsize(filename):,} bytes")
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
    
    def _print_cube_summary(self, aggregates: List[Dict], cube_name: str) -> None:
        """Print summary of cube aggregates"""
        total_rows = sum(agg.get("latest_instance", {}).get("stats", {}).get("number_of_rows", 0) for agg in aggregates)
        total_build_time = sum(agg.get("latest_instance", {}).get("stats", {}).get("build_duration", 0) for agg in aggregates)
        active_count = sum(1 for agg in aggregates if agg.get("latest_instance", {}).get("status", "").lower() == "active")
        
        print(f"\nSummary for {cube_name}:")
        print(f"  Total aggregates:    {len(aggregates)}")
        print(f"  Active aggregates:   {active_count}")
        print(f"  Total rows:          {total_rows:,}")
        print(f"  Total build time:    {self._format_time(total_build_time)}")
        if aggregates:
            avg_rows = total_rows / len(aggregates)
            avg_build = total_build_time / len(aggregates)
            print(f"  Average rows:        {avg_rows:,.0f}")
            print(f"  Average build time:  {self._format_time(avg_build)}")
    
    def _format_time(self, milliseconds: int) -> str:
        """Format time in milliseconds to human readable format"""
        if milliseconds < 1000:
            return f"{milliseconds:.0f}ms"
        elif milliseconds < 60000:
            return f"{milliseconds/1000:.1f}s"
        else:
            minutes = milliseconds / 60000
            return f"{minutes:.1f}min"