## 2025-02-14 - Fix path traversal vulnerability in Flask file downloads
**Vulnerability:** The API was using Flask's `send_file` with dynamically constructed paths which can lead to path traversal vulnerabilities (e.g. users injecting `../` in requested file names or IDs to access arbitrary files).
**Learning:** Extracting directory bases dynamically or trusting unverified user inputs alongside `send_file` introduces security risks.
**Prevention:** Always use `send_from_directory` with a fixed, trusted base directory and pass the dynamically constructed or user-provided basename as the second argument. This delegates the path traversal checking to Werkzeug securely.
