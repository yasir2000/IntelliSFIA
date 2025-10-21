#!/usr/bin/env python3
"""
IntelliSFIA CLI Entry Point
==========================
"""

import sys
from pathlib import Path

# Add src to path for development
if __name__ == "__main__":
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))

from intellisfia.cli import main

if __name__ == "__main__":
    main()