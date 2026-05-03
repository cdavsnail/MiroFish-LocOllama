## 2024-05-18 - Prevent Path Traversal by using send_from_directory
**Vulnerability:** Utilizing `send_file` with dynamic paths allows path traversal attacks. In addition, extracting the directory from a user-provided or potentially tainted path via `os.path.dirname(path)` is an anti-pattern.
**Learning:** Migrating to `send_from_directory` is necessary for mitigating path traversal vulnerabilities in Flask applications. The base directory passed to `send_from_directory` must be a trusted, fixed path.
**Prevention:** Only use `send_from_directory` for file downloads and verify the base path parameter.
