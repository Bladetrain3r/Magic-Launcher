"""Data models for launcher items."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class BaseItem:
    """Base class for launcher items."""
    name: str
    icon: str
    type: str = ""  # Add default
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'type': self.type,
            'icon': self.icon
        }


@dataclass
class Shortcut(BaseItem):
    """A shortcut/launcher item."""
    path: str = ""  # Add default
    args: str = ""
    
    def __post_init__(self):
        self.type = "shortcut"
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'path': self.path,
            'args': self.args
        })
        return data


@dataclass
class Folder(BaseItem):
    """A folder containing other items."""
    items: Dict[str, 'BaseItem'] = field(default_factory=dict)
    
    def __post_init__(self):
        self.type = "folder"
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['items'] = {
            name: item.to_dict() 
            for name, item in self.items.items()
        }
        return data
    
    def add_item(self, item: BaseItem):
        """Add an item to this folder."""
        self.items[item.name] = item
    
    def remove_item(self, name: str):
        """Remove an item from this folder."""
        if name in self.items:
            del self.items[name]
    
    def get_item(self, name: str) -> Optional[BaseItem]:
        """Get an item by name."""
        return self.items.get(name)


def item_from_dict(name: str, data: Dict[str, Any]) -> BaseItem:
    """Create an item from dictionary data."""
    item_type = data.get('type', 'shortcut')
    
    if item_type == 'folder':
        folder = Folder(
            name=name,
            icon=data.get('icon', name[0].upper())
        )
        # Recursively create child items
        for child_name, child_data in data.get('items', {}).items():
            folder.add_item(item_from_dict(child_name, child_data))
        return folder
    else:
        return Shortcut(
            name=name,
            icon=data.get('icon', name[0].upper()),
            path=data.get('path', ''),
            args=data.get('args', '')
        )