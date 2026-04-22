## 2025-02-27 - Security Hardening (File Uploads & Downloads)
**Vulnerability:** File upload endpoints used `os.path.splitext(original_filename)[1]` directly without sanitizing the original filename. File download endpoints used `send_file` with dynamically constructed paths which can lead to path traversal vulnerabilities.
**Learning:** In Flask, `send_from_directory` must be used instead of `send_file` to ensure the file path is restricted to a safe, trusted directory. `secure_filename` should always be applied to `original_filename` to prevent path traversal when handling uploaded files.
**Prevention:** Always use `send_from_directory(safe_dir, filename)` when serving files. Apply `werkzeug.utils.secure_filename` before extracting the extension or saving an uploaded file.
