## 2025-02-12 - Prevent Path Traversal in Flask Downloads
**Vulnerability:** The Flask backend was using `send_file()` to serve dynamically generated temporary files and files constructed using user inputs, introducing path traversal risks if the inputs aren't properly sanitized.
**Learning:** Extracting directory portions from a user-provided path and using `send_file` does not provide robust protection. In Flask applications, file serving must enforce base directories.
**Prevention:** Use Flask's `send_from_directory(directory, filename)` instead of `send_file()` for dynamically requested or generated files. Ensure the `directory` argument is a static, trusted base path (like `tempfile.gettempdir()` or a pre-configured data directory).
