## 2025-02-28 - [Path Traversal in File Upload]
**Vulnerability:** Raw `file.filename` was directly passed to `save_file_to_project` in `backend/app/api/graph.py` during file uploads.
**Learning:** This is a classic path traversal vulnerability, which allows an attacker to manipulate the file path using `../` characters and overwrite arbitrary files on the system.
**Prevention:** Always sanitize uploaded filenames using Werkzeug's `secure_filename()` before using them in file system operations.
