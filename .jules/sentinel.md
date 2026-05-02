## 2025-02-27 - Replace send_file with send_from_directory
**Vulnerability:** Path Traversal via `flask.send_file`
**Learning:** Using `flask.send_file` with variables controlled by user input without proper sanitization can allow path traversal attacks where arbitrary files are retrieved.
**Prevention:** Always use `flask.send_from_directory` with a hardcoded, trusted base directory instead of manually reconstructing paths. Do not try to extract the directory from a user-supplied path to pass to `send_from_directory`.
