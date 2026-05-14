
## 2025-05-14 - Fix Path Traversal in File Downloads
**Vulnerability:** Used `send_file` with dynamic paths to serve report downloads and simulation scripts/configs, introducing path traversal risks.
**Learning:** Never use `send_file` for dynamically generated paths or temp files in Flask as it can expose the file system. Extracting directories using `os.path.dirname()` from unvalidated paths is insufficient (security theater).
**Prevention:** Always use `send_from_directory` with a fixed, trusted base directory and explicitly validate/sanitize filenames. For temp files, use `send_from_directory(tempfile.gettempdir(), os.path.basename(temp_path))`.
