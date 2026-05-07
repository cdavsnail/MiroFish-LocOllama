
## 2024-05-07 - Prevent Path Traversal via send_file
**Vulnerability:** Path traversal vulnerabilities due to `send_file` with user-controlled input paths without enforcing a trusted base directory.
**Learning:** Using `os.path.dirname(path)` is an anti-pattern (security theater). The base directory must be explicitly provided and strictly trusted.
**Prevention:** Always use `send_from_directory(trusted_base_dir, safe_filename)` instead of `send_file`.
