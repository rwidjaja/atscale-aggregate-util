# simple_ui.py - Alternative with simpler navigation
import os
from typing import List, Dict, Any, Optional


class SimpleListMenu:
    """A simple list menu with number-based selection"""
    
    def __init__(self, items: List[Any], title: str = "", show_index: bool = True):
        self.items = items
        self.title = title
        self.show_index = show_index
    
    def select(self) -> Optional[Any]:
        """Display items and let user select by number"""
        os.system("cls" if os.name == "nt" else "clear")
        
        if self.title:
            print(f"\n{self.title}")
            print("=" * 60)
        
        if not self.items:
            print("No items to select.")
            return None
        
        # Display items
        for i, item in enumerate(self.items, 1):
            display_text = self._format_item(item, i)
            print(f"{display_text}")
        
        print(f"\n{'─'*60}")
        
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
                return f"{index:3d}. {item['display']}"
            elif "name" in item:
                return f"{index:3d}. {item['name']}"
            elif "id" in item:
                return f"{index:3d}. {item['id']}"
        elif isinstance(item, str):
            return f"{index:3d}. {item}"
        return f"{index:3d}. {str(item)}"


def display_menu(options: List[str], title: str = "") -> Optional[int]:
    """Display a simple menu and return selected index"""
    os.system("cls" if os.name == "nt" else "clear")
    
    if title:
        print(f"\n{title}")
        print("=" * 60)
    
    for i, option in enumerate(options, 1):
        print(f"{i:2d}. {option}")
    
    print(f"\n{'─'*60}")
    
    while True:
        try:
            choice = input(f"Select option (1-{len(options)}, or 'q' to quit): ").strip().lower()
            
            if choice == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(options):
                return index
            else:
                print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")
        except KeyboardInterrupt:
            print("\nCancelled.")
            return None


def yes_no_question(prompt: str, default_no: bool = True) -> bool:
    """Ask a yes/no question with optional default"""
    if default_no:
        prompt_suffix = " [y/N]: "
    else:
        prompt_suffix = " [Y/n]: "
    
    while True:
        response = input(prompt + prompt_suffix).strip().lower()
        
        if response == "":
            return not default_no
        elif response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Please answer 'y' or 'n'")