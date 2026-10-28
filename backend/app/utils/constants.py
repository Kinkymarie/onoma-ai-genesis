"""Application-wide constants."""

APP_NAME = "Onoma AI Genesis"
APP_VERSION = "1.0.0"
API_PREFIX = "/api"

ROLE_ADMIN = "admin"
ROLE_MEMBER = "member"
ROLE_VIEWER = "viewer"
ROLES = (ROLE_ADMIN, ROLE_MEMBER, ROLE_VIEWER)

TASK_STATUSES = ("todo", "in_progress", "done", "blocked")
TASK_PRIORITIES = ("low", "medium", "high", "urgent")
PROJECT_STATUSES = ("active", "archived", "completed")

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
