## 2025-02-28 - [Path Traversal Prevention in Flask]
**Vulnerability:** Path traversal vulnerabilities can exist when user-provided filenames or paths are passed directly to `send_file`.
**Learning:** `send_file` does not intrinsically validate the base directory. If a path string is concatenated directly, users may use `../` to access unauthorized files.
**Prevention:** Use `flask.send_from_directory(directory, filename)` to serve files. `send_from_directory` automatically verifies that the requested file resolves within the specified base directory. Also, use `werkzeug.utils.secure_filename` to sanitize user-provided file names.
