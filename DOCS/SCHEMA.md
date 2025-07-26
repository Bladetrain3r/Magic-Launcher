# JSON Schemas
- Right now there is only the one file referenced (shortcuts.json)
- Rather than alter that and screw with my backwards compatibility, a new schema will be set up for settings.

## shortcuts.json
- Default shortcuts.json
```json
{
    'Games': {
        'type': 'folder',
        'icon': 'G',
        'items': {
            'Action': {
                'type': 'folder',
                'icon': 'A',
                'items': {}
            },
            'Puzzle': {
                'type': 'folder',
                'icon': 'P',
                'items': {}
            }
        }
    },
    'Tools': {
        'type': 'folder',
        'icon': 'T',
        'items': {
        }
    },
    'Scripts': {
        'type': 'folder',
        'icon': 'S',
        'items': {}
    },
    'Hello World shell': {
        'type': 'shortcut',
        'icon': 'sh',
        'path': 'echo',
        'args': 'Hello, World from Bash!',
    },
    'NGGUU': {
        'type': 'shortcut',
        'icon': 'RR',
        'path': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    }
}
```

### Entry Types

#### Shortcuts
```json
'Name': {
    'type': shortcut,
    'icon': str,
    'path': str,
    'args': str,
}
```

#### Folders
```json
'Name': {
    'type': folder,
    'icon': str,
    'items': dict
}
```

## Draft formal schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "patternProperties": {
    "^.*$": {
      "oneOf": [
        {
          "type": "object",
          "required": ["type", "icon", "items"],
          "properties": {
            "type": { "const": "folder" },
            "icon": { "type": "string" },
            "items": { "$ref": "#" }
          }
        },
        {
          "type": "object",
          "required": ["type", "icon", "path"],
          "properties": {
            "type": { "const": "shortcut" },
            "icon": { "type": "string" },
            "path": { "type": "string" },
            "args": { "type": "string" }
          }
        }
      ]
    }
  }
}
```