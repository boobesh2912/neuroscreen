# Database Migration Notes

## Current State

- The backend does not use Alembic/Django migrations yet.
- Required tables are created during startup via `CREATE TABLE IF NOT EXISTS` in `app/core/database.py`.
- This is safe for initial bootstrapping on both SQLite and PostgreSQL.

## Production Change Strategy

Use expand/contract deployment for schema updates:

1. Expand:
   - Add new nullable columns/tables/indexes first.
   - Keep existing columns and application code paths working.
2. Deploy:
   - Release backend that reads/writes both old and new schema when needed.
3. Backfill:
   - Run one-off SQL/data backfill job if required.
4. Contract:
   - Remove deprecated columns/constraints in a later release only after verification.

## Render PostgreSQL Guidance

- Configure `DATABASE_URL` from Render PostgreSQL instance.
- Keep `DATABASE_SSL_MODE=require`.
- Keep pool conservative for starter plans:
  - `DB_POOL_MIN_SIZE=1`
  - `DB_POOL_MAX_SIZE=5`

## Failure Handling

- Startup retries DB connection based on:
  - `DB_CONNECT_MAX_RETRIES`
  - `DB_CONNECT_RETRY_DELAY_SECONDS`
- If DB cannot be reached, startup fails fast with clear logs.
- API returns structured JSON errors for DB failures.

## Recommended Next Step

Introduce Alembic for versioned migrations once schema evolution becomes frequent.
