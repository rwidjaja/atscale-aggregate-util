# aggregate_build_history.py
import json
from datetime import datetime
from typing import Dict, List
from ui_components import display_table, confirm_action


class AggregateBuildHistory:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def show_build_history(self, cube_data: Dict) -> None:
        """Show aggregate build history for a specific cube"""
        try:
            print("\nFetching build history...")
            response = self.api_client.get_aggregate_build_history(
                cube_data["project_id"], 
                cube_data["cube_id"],
                limit=20
            )
            
            history_data = response.get("response", {}).get("data", [])
            
            if not history_data:
                print(f"No build history found for {cube_data['display']}.")
                return
            
            print(f"\n{'='*70}")
            print(f"AGGREGATE BUILD HISTORY - {cube_data['display']}")
            print('='*70)
            
            # Display in table format
            columns = ["Batch ID", "Start Time", "End Time", "Duration", "Status", "Type", "Estimate", "Total Build"]
            display_data = []
            
            for batch in history_data:
                batch_id = batch.get("id", "N/A")
                
                # Calculate duration
                start_time = batch.get("startTime", "")
                end_time = batch.get("endTime", "")
                duration = self._calculate_duration(start_time, end_time)
                
                # Parse times
                start_display = self._format_time_display(start_time)
                end_display = self._format_time_display(end_time)
                
                # Format estimate time
                estimate = batch.get("estimateTime", 0)
                estimate_str = f"{estimate}ms"
                if estimate > 1000:
                    estimate_str = f"{estimate/1000:.1f}s"
                
                # Format total build time (PT3.232S format)
                total_build = batch.get("sumOfInstanceBuildTimes", "PT0S")
                total_build_str = self._parse_iso_duration(total_build)
                
                display_data.append({
                    "Batch ID": batch_id[:12] + "...",
                    "Start Time": start_display,
                    "End Time": end_display,
                    "Duration": duration,
                    "Status": batch.get("status", "unknown"),
                    "Type": "Full" if batch.get("isFullBuild") else "Incremental",
                    "Estimate": estimate_str,
                    "Total Build": total_build_str
                })
            
            display_table(display_data, columns)
            
            # Show summary statistics
            self._show_build_history_summary(history_data)
            
            # Option to show detailed view
            if confirm_action("\nShow detailed batch information?"):
                self._show_detailed_batch_info(history_data)
                
        except Exception as e:
            print(f"Error: {e}")
    
    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """Calculate duration between two ISO timestamps"""
        if not start_time or not end_time:
            return "N/A"
        
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration_ms = (end - start).total_seconds() * 1000
            return self._format_time(duration_ms)
        except:
            return "N/A"
    
    def _format_time_display(self, time_str: str) -> str:
        """Format time for display"""
        if not time_str:
            return "N/A"
        
        try:
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            return dt.strftime("%m/%d %H:%M")
        except:
            return time_str[:16]
    
    def _parse_iso_duration(self, duration_str: str) -> str:
        """Parse ISO 8601 duration string (e.g., PT3.232S)"""
        if not duration_str or not duration_str.startswith("PT"):
            return "N/A"
        
        try:
            # Remove PT prefix
            duration = duration_str[2:]
            
            if duration.endswith("S"):
                seconds = float(duration[:-1])
                if seconds < 60:
                    return f"{seconds:.1f}s"
                else:
                    minutes = seconds / 60
                    return f"{minutes:.1f}min"
            elif duration.endswith("M"):
                minutes = float(duration[:-1])
                return f"{minutes:.1f}min"
            elif duration.endswith("H"):
                hours = float(duration[:-1])
                return f"{hours:.1f}hr"
            else:
                return duration_str
        except:
            return duration_str
    
    def _show_build_history_summary(self, history_data: List[Dict]) -> None:
        """Show summary statistics for build history"""
        print(f"\n{'='*50}")
        print("BUILD HISTORY SUMMARY")
        print('='*50)
        
        if not history_data:
            print("No build history data available.")
            return
        
        total_batches = len(history_data)
        successful = sum(1 for b in history_data if b.get("status") == "done")
        failed = sum(1 for b in history_data if b.get("status") == "failed")
        running = sum(1 for b in history_data if b.get("status") == "running")
        full_builds = sum(1 for b in history_data if b.get("isFullBuild"))
        
        # Calculate average duration
        durations = []
        for batch in history_data:
            start_time = batch.get("startTime", "")
            end_time = batch.get("endTime", "")
            if start_time and end_time:
                try:
                    start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    duration_ms = (end - start).total_seconds() * 1000
                    durations.append(duration_ms)
                except:
                    pass
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        print(f"\nBatch Statistics:")
        print(f"  Total Batches:      {total_batches}")
        print(f"  Successful:         {successful} ({successful/total_batches*100:.1f}%)")
        print(f"  Failed:             {failed} ({failed/total_batches*100:.1f}%)")
        print(f"  Running:            {running} ({running/total_batches*100:.1f}%)")
        print(f"  Full Builds:        {full_builds} ({full_builds/total_batches*100:.1f}%)")
        
        if durations:
            print(f"\nDuration Statistics:")
            print(f"  Average Duration:   {self._format_time(avg_duration)}")
            if len(durations) > 1:
                min_duration = min(durations)
                max_duration = max(durations)
                print(f"  Minimum Duration:   {self._format_time(min_duration)}")
                print(f"  Maximum Duration:   {self._format_time(max_duration)}")
        
        # Show recent builds timeline
        print(f"\nRecent Build Timeline:")
        recent_builds = history_data[:5]  # Last 5 builds
        for i, batch in enumerate(recent_builds, 1):
            status = batch.get("status", "unknown")
            batch_type = "Full" if batch.get("isFullBuild") else "Incremental"
            batch_id = batch.get("id", "N/A")[:8] + "..."
            
            # Get duration
            start_time = batch.get("startTime", "")
            end_time = batch.get("endTime", "")
            duration = self._calculate_duration(start_time, end_time)
            
            print(f"  {i}. {batch_id} - {status.upper()} ({batch_type}) - {duration}")
    
    def _show_detailed_batch_info(self, history_data: List[Dict]) -> None:
        """Show detailed information for each batch"""
        for i, batch in enumerate(history_data, 1):
            print(f"\n{'─'*60}")
            print(f"BATCH {i}: {batch.get('id', 'N/A')}")
            print('─'*60)
            
            print(f"Status:          {batch.get('status', 'unknown')}")
            print(f"Type:            {'Full Build' if batch.get('isFullBuild') else 'Incremental Build'}")
            print(f"Batch Type:      {batch.get('batchType', 'N/A')}")
            
            # Format times
            create_date = batch.get("createDate", "")
            start_time = batch.get("startTime", "")
            end_time = batch.get("endTime", "")
            
            if create_date:
                try:
                    create_dt = datetime.fromisoformat(create_date.replace('Z', '+00:00'))
                    print(f"Created:         {create_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    print(f"Created:         {create_date}")
            
            if start_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    print(f"Started:         {start_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    print(f"Started:         {start_time}")
            
            if end_time:
                try:
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    print(f"Ended:           {end_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    print(f"Ended:           {end_time}")
            
            # Calculate and display duration
            if start_time and end_time:
                duration = self._calculate_duration(start_time, end_time)
                print(f"Duration:        {duration}")
            
            # Other metrics
            estimate = batch.get("estimateTime", 0)
            if estimate:
                estimate_str = f"{estimate}ms"
                if estimate > 1000:
                    estimate_str = f"{estimate/1000:.1f}s"
                print(f"Estimate:        {estimate_str}")
            
            total_build = batch.get("sumOfInstanceBuildTimes", "")
            if total_build:
                total_build_str = self._parse_iso_duration(total_build)
                print(f"Total Build:     {total_build_str}")
            
            # Check if this was recent (within last 24 hours)
            if start_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    time_since = datetime.now(start_dt.tzinfo) - start_dt
                    if time_since.total_seconds() < 86400:  # 24 hours
                        hours_ago = time_since.total_seconds() / 3600
                        print(f"Recency:         {hours_ago:.1f} hours ago")
                except:
                    pass
    
    def _format_time(self, milliseconds: int) -> str:
        """Format time in milliseconds to human readable format"""
        if milliseconds < 1000:
            return f"{milliseconds:.0f}ms"
        elif milliseconds < 60000:
            return f"{milliseconds/1000:.1f}s"
        else:
            minutes = milliseconds / 60000
            return f"{minutes:.1f}min"