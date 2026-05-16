## 2025-05-16 - Prevent Path Traversal in File Downloads
**Vulnerability:** File downloads in `flask` were previously implemented using `send_file`, which combined with unsanitized user inputs, opened up a path traversal vulnerability. An attacker could potentially navigate the directory tree using `../` and download sensitive system or configuration files.
**Learning:** For dynamic paths or when handling files built dynamically based on user input, directly using `send_file` can lead to directory traversal if the variable includes malicious characters.
**Prevention:** File downloads must utilize `send_from_directory(directory, filename)` to strictly confine file resolution to the provided trusted `directory`, ignoring any traversal elements in the filename.
