"""Input validation helpers."""
import re

from .exceptions import ValidationFailed

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_password_strength(password: str) -> str:
    problems = []
    if len(password) < 8:
        problems.append("at least 8 characters")
    if not re.search(r"[a-z]", password):
        problems.append("a lowercase letter")
    if not re.search(r"[A-Z]", password):
        problems.append("an uppercase letter")
    if not re.search(r"\d", password):
        problems.append("a digit")
    if problems:
        raise ValidationFailed("Password must contain " + ", ".join(problems))
    return password


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValidationFailed("Cannot derive a slug from the given value")
    return slug


def validate_slug(value: str) -> str:
    if not _SLUG_RE.match(value):
        raise ValidationFailed("Slug must be lowercase alphanumeric words separated by hyphens")
    return value


def validate_choice(value: str, choices: tuple[str, ...], field: str) -> str:
    if value not in choices:
        raise ValidationFailed(f"{field} must be one of: {', '.join(choices)}")
    return value


def sanitize_filename(name: str) -> str:
    name = name.replace("\\", "/").split("/")[-1]
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name).lstrip(".")
    if not name:
        raise ValidationFailed("Invalid filename")
    return name[:255]
