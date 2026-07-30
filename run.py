"""Launcher script for PyInstaller packaging.

The src package uses relative imports, which PyInstaller can't resolve
when using src.main directly. This thin launcher at the project root
avoids that issue."""

from src.main import main

if __name__ == "__main__":
    main()
