#!/usr/bin/env python3
"""
Run script for the University FAQ Assistant backend.
"""
import uvicorn
import os

if __name__ == "__main__":
    # Set PYTHONPATH to current directory
    os.environ.setdefault("PYTHONPATH", os.getcwd())

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        log_level="info"
    )