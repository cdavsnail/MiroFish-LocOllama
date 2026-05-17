## 2026-05-17 - [Path Traversal Vulnerability in Flask]
**Vulnerability:** The application was using `send_file` in Flask to serve dynamically generated temporary files and existing markdown files, which can lead to path traversal vulnerabilities if user input is somehow incorporated into the file path.
**Learning:** Extracting the directory from a user-provided or potentially tainted path via `os.path.dirname(path)` is an anti-pattern and constitutes 'security theater'.
**Prevention:** To securely serve files in a Flask backend, use `send_from_directory(trusted_base_directory, file_name)` instead of `send_file` to prevent path traversal vulnerabilities while enforcing a trusted base directory.
