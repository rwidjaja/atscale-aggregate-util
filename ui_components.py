# ui_components.py
import os
from typing import List, Dict, Any, Optional


class SimpleListSelector:
    """A simple list selector that works reliably across platforms"""
    
    def __init__(self, items: List[Any], title: str = ""):
        self.items = items
        self.title = title
    
    def select(self) -> Optional[Any]:
        """Display items and let user select by number"""
        os.system("cls" if os.name == "nt" else "clear")
        
        if self.title:
            print(f"\n{self.title}")
            print("=" * 50)
        
        if not self.items:
            print("No items to select.")
            return None
        
        # Display items
        for i, item in enumerate(self.items, 1):
            display_text = self._format_item(item, i)
            print(f"{display_text}")
        
        print(f"\n{'─'*50}")
        
        while True:
            try:
                choice = input(f"Select item (1-{len(self.items)}, or 'q' to quit): ").strip().lower()
                
                if choice == 'q':
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(self.items):
                    return self.items[index]
                else:
                    print(f"Please enter a number between 1 and {len(self.items)}")
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
            except KeyboardInterrupt:
                print("\nCancelled.")
                return None
    
    def _format_item(self, item: Any, index: int) -> str:
        """Format an item for display"""
        if isinstance(item, dict):
            if "display" in item:
                return f"{index:2d}. {item['display']}"
            elif "name" in item:
                return f"{index:2d}. {item['name']}"
            elif "id" in item:
                return f"{index:2d}. {item['id']}"
        elif isinstance(item, str):
            return f"{index:2d}. {item}"
        return f"{index:2d}. {str(item)}"


def display_table(data: List[Dict], columns: List[str]) -> None:
    """Display data in a formatted table"""
    if not data:
        print("No data to display")
        return

    # Calculate column widths
    col_widths = {}
    for col in columns:
        max_len = len(col)
        for row in data:
            if col in row:
                max_len = max(max_len, len(str(row[col])))
        col_widths[col] = max_len + 2  # Add padding

    # Print header
    header = " | ".join([col.ljust(col_widths[col]) for col in columns])
    separator = "-+-".join(["-" * col_widths[col] for col in columns])
    print("\n" + header)
    print(separator)

    # Print rows
    for row in data:
        row_str = " | ".join(
            [str(row.get(col, "")).ljust(col_widths[col]) for col in columns]
        )
        print(row_str)
    print()


def confirm_action(prompt: str) -> bool:
    """Ask for confirmation"""
    response = input(f"\n{prompt} (y/N): ").strip().lower()
    return response in ["y", "yes"]