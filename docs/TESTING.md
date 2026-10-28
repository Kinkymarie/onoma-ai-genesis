# Testing Guide

```bash
cd backend
python -m pytest -q
```
Fixtures live in `tests/conftest.py` (`client`, `admin`, `member`, `auth_headers`, `workspace`). State is reset
between tests, rate limiting is disabled and no network calls are made (the offline `echo` provider is used).
