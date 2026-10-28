# Backup & Recovery

- RDS (`rds.tf`): encrypted storage, 14-day automated backups (point-in-time recovery) and a read replica.
- Self-hosted: `docker compose exec postgres pg_dump -U onoma onoma > backup.sql`; restore with `psql -U onoma onoma < backup.sql`.
- Test restores regularly. Rotate `JWT_SECRET` after any suspected compromise (invalidates all sessions).
