check = {
    "properties": {
        "name": {"type": "string"},
        "tags": {"type": "string"},
        "timeout": {"type": "number", "minimum": 60, "maximum": 29030400},
        "grace": {"type": "number", "minimum": 60, "maximum": 29030400},
        "channels": {"type": "string"}
    }
}
