# aggregate_health_checker.py
from datetime import datetime
from typing import Dict, List


class AggregateHealthChecker:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def check_cube_aggregate_health(self, cube_data: Dict) -> None:
        """Check aggregate health for a specific cube"""
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
            
            print(f"\n{'='*60}")
            print(f"AGGREGATE HEALTH CHECK - {cube_data['display']}")
            print('='*60)
            
            issues = []
            warnings = []
            
            for agg in aggregates_data:
                agg_id = agg.get("id", "Unknown")[:12] + "..."
                status = agg.get("latest_instance", {}).get("status", "").lower()
                rows = agg.get("latest_instance", {}).get("stats", {}).get("number_of_rows", 0)
                build_time = agg.get("latest_instance", {}).get("stats", {}).get("build_duration", 0)
                query_util = agg.get("stats", {}).get("query_utilization", 0)
                last_query = agg.get("stats", {}).get("most_recent_query", "")
                
                # Check for inactive aggregates
                if status != "active":
                    issues.append(f"✗ {agg_id}: Status is '{status}'")
                
                # Check for aggregates with 0 rows
                if rows == 0:
                    warnings.append(f"⚠ {agg_id}: Has 0 rows")
                
                # Check for very slow builds (> 30 seconds)
                if build_time > 30000:  # 30 seconds in milliseconds
                    warnings.append(f"⚠ {agg_id}: Slow build ({self._format_time(build_time)})")
                
                # Check for aggregates with no queries
                if query_util == 0 and last_query == "":
                    warnings.append(f"⚠ {agg_id}: No query utilization")
                
                # Check for old queries (older than 30 days)
                if last_query and last_query != "never":
                    try:
                        query_date = datetime.fromisoformat(last_query.replace('Z', '+00:00'))
                        days_old = (datetime.now(query_date.tzinfo) - query_date).days
                        if days_old > 30:
                            warnings.append(f"⚠ {agg_id}: Last query {days_old} days ago")
                    except:
                        pass
            
            print(f"\nIssues Found ({len(issues)}):")
            if issues:
                for issue in issues[:10]:  # Show first 10 issues
                    print(f"  {issue}")
                if len(issues) > 10:
                    print(f"  ... and {len(issues) - 10} more issues")
            else:
                print("  ✓ No critical issues found")
            
            print(f"\nWarnings ({len(warnings)}):")
            if warnings:
                for warning in warnings[:10]:  # Show first 10 warnings
                    print(f"  {warning}")
                if len(warnings) > 10:
                    print(f"  ... and {len(warnings) - 10} more warnings")
            else:
                print("  ✓ No warnings")
            
            print(f"\nSummary:")
            print(f"  Total Aggregates: {len(aggregates_data)}")
            print(f"  Issues:           {len(issues)}")
            print(f"  Warnings:         {len(warnings)}")
            
            # Health score
            health_score = 100
            if len(aggregates_data) > 0:
                issue_penalty = (len(issues) / len(aggregates_data)) * 50
                warning_penalty = (len(warnings) / len(aggregates_data)) * 25
                health_score = max(0, 100 - issue_penalty - warning_penalty)
            
            print(f"  Health Score:      {health_score:.1f}/100")
            
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