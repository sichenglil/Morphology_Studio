# Security Policy

Security fixes are provided for the latest `0.1.x` development line. Do not disclose an unpatched vulnerability in a public issue. Use GitHub private vulnerability reporting for this repository; if that feature is unavailable, contact the repository owner privately through their GitHub profile before sharing details.

Reports should include affected version, impact, minimal reproduction, and suggested mitigation without confidential models or credentials. The maintainer aims to acknowledge reports within seven days, validate and prioritize them, coordinate a fix and disclosure, and update affected dependencies.

The security boundary includes imported XML, resource resolution, archive/export paths, workspace writes, local HTTP endpoints, and the pywebview file-selection bridge. The desktop bridge intentionally exposes file selection only; arbitrary command execution is out of scope and must not be added. Local applications cannot protect a user who explicitly opens a malicious file with unrestricted OS permissions.
