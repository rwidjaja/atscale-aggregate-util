# aggregate_statistics.py
from datetime import datetime
from typing import Dict, List


class AggregateStatistics:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def show_cube_aggregate_statistics(self, cube_data: Dict) -> None:
        """Show aggregate statistics for a specific cube"""
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
            
            print(f"\n{'='*60}")
            print(f"AGGREGATE STATISTICS - {cube_data['display']}")
            print('='*60)
            print(f"Total Aggregates: {total_aggregates}")
            print(f"Fetched in this batch: {len(aggregates_data)}")
            
            # Type breakdown
            type_count = {}
            subtype_count = {}
            status_count = {}
            total_rows = 0
            total_build_time = 0
            total_query_utilization = 0
            active_count = 0
            
            for agg in aggregates_data:
                agg_type = agg.get("type", "unknown")
                agg_subtype = agg.get("subtype", "unknown")
                status = agg.get("latest_instance", {}).get("status", "unknown")
                rows = agg.get("latest_instance", {}).get("stats", {}).get("number_of_rows", 0)
                build_time = agg.get("latest_instance", {}).get("stats", {}).get("build_duration", 0)
                query_util = agg.get("stats", {}).get("query_utilization", 0)
                
                type_count[agg_type] = type_count.get(agg_type, 0) + 1
                subtype_count[agg_subtype] = subtype_count.get(agg_subtype, 0) + 1
                status_count[status] = status_count.get(status, 0) + 1
                total_rows += rows
                total_build_time += build_time
                total_query_utilization += query_util
                
                if status.lower() == "active":
                    active_count += 1
            
            print(f"\nType Breakdown:")
            for agg_type, count in sorted(type_count.items()):
                percentage = (count / len(aggregates_data)) * 100
                print(f"  {agg_type.replace('_', ' ').title():25} {count:3d} ({percentage:.1f}%)")
            
            print(f"\nSubtype Breakdown:")
            for subtype, count in sorted(subtype_count.items()):
                percentage = (count / len(aggregates_data)) * 100
                print(f"  {subtype.replace('_', ' ').title():25} {count:3d} ({percentage:.1f}%)")
            
            print(f"\nStatus Breakdown:")
            for status, count in sorted(status_count.items()):
                percentage = (count / len(aggregates_data)) * 100
                print(f"  {status.title():15} {count:3d} ({percentage:.1f}%)")
            
            print(f"\nBuild Statistics:")
            avg_build_time = total_build_time / len(aggregates_data) if aggregates_data else 0
            print(f"  Total Build Time:     {self._format_time(total_build_time)}")
            print(f"  Average Build Time:   {self._format_time(avg_build_time)}")
            
            print(f"\nRow Statistics:")
            print(f"  Total Rows:          {total_rows:,}")
            if aggregates_data:
                avg_rows = total_rows / len(aggregates_data)
                print(f"  Average Rows/Agg:    {avg_rows:,.0f}")
            
            print(f"\nQuery Utilization:")
            avg_query_util = total_query_utilization / len(aggregates_data) if aggregates_data else 0
            print(f"  Average Utilization:  {avg_query_util:.1f}")
            
            # Find aggregates with extremes
            if aggregates_data:
                fastest = min(aggregates_data, key=lambda x: x.get("latest_instance", {}).get("stats", {}).get("build_duration", 0))
                slowest = max(aggregates_data, key=lambda x: x.get("latest_instance", {}).get("stats", {}).get("build_duration", 0))
                largest = max(aggregates_data, key=lambda x: x.get("latest_instance", {}).get("stats", {}).get("number_of_rows", 0))
                smallest = min(aggregates_data, key=lambda x: x.get("latest_instance", {}).get("stats", {}).get("number_of_rows", 0))
                
                print(f"\nFastest Build:")
                print(f"  ID:     {fastest.get('id', 'N/A')[:15]}...")
                print(f"  Time:   {self._format_time(fastest.get('latest_instance', {}).get('stats', {}).get('build_duration', 0))}")
                
                print(f"\nSlowest Build:")
                print(f"  ID:     {slowest.get('id', 'N/A')[:15]}...")
                print(f"  Time:   {self._format_time(slowest.get('latest_instance', {}).get('stats', {}).get('build_duration', 0))}")
                
                print(f"\nLargest Aggregate:")
                print(f"  ID:     {largest.get('id', 'N/A')[:15]}...")
                print(f"  Rows:   {largest.get('latest_instance', {}).get('stats', {}).get('number_of_rows', 0):,}")
                
                print(f"\nSmallest Aggregate:")
                print(f"  ID:     {smallest.get('id', 'N/A')[:15]}...")
                print(f"  Rows:   {smallest.get('latest_instance', {}).get('stats', {}).get('number_of_rows', 0):,}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    def _format_time(self, milliseconds: int) -> str:
        """Format time in milliseconds to human readable format"""
        if milliseconds < 1000:
            return f"{milliseconds:.0f}ms"
        elif milliseconds < 60000:
            return f"{milliseconds/1000:.1f}s"
        else:
            minutes = milliseconds / 60000
            return f"{minutes:.1f}min"