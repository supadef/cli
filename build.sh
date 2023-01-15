rm -f dist/*
python3 increment_version.py
python3 -m build
