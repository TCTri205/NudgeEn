# libSQL Usage Guidelines (Zero-Risk Migration Strategy)

This document specifies the design and development standards when using **libSQL** (SQLite dialect) during the MVP phase. The ultimate goal is to ensure that the transition to **PostgreSQL** in the future is smooth, risk-free, and requires no core logic rewrites.

---

## 1. Portable Schema (SQL Standards)

PostgreSQL is very strict about data types, while SQLite is quite "flexible." To avoid errors during migration:

- **Do:**
  - Use only common data types: `INTEGER`, `TEXT`, `REAL`, `BOOLEAN`, `TIMESTAMP`.
  - Always declare `NOT NULL`, `UNIQUE`, and `DEFAULT` explicitly for every column.
  - Set clear Primary Keys (prefer auto-incrementing `INTEGER PRIMARY KEY` or `TEXT` for UUIDs).
  - Design relationships with clear Foreign Key (FK) logic, even if enforcement is not yet enabled in libSQL.
- **Don't:**
  - Rely on SQLite's dynamic typing (do not insert mismatched data types into columns).
  - Use "virtual" or non-standard data types that do not exist in PostgreSQL.

## 2. Timing Discipline (Timestamps)

Differences in time-handling functions are a leading cause of database migration errors.

- **Do:**
  - **UTC Only:** Always store all timestamps in UTC.
  - **App-side Conversion:** Prioritize converting and handling time at the Application Layer (Python/Pydantic) instead of using SQL functions.
  - Use the `ISO8601` standard (`YYYY-MM-DD HH:MM:SS`) if storing as Text.
- **Don't:**
  - Mix multiple time zones.
  - Depend on engine-specific `datetime` functions (e.g., SQLite's `date('now')`).

## 3. JSON Strategy: "Blob" Style

PostgreSQL has very powerful `JSONB`, but the JSON query syntax between the two is completely different.

- **Do:**
  - Treat JSON as a data block (blob): Only Load/Save the entire object from the application code.
  - Validate JSON structures using Pydantic before writing to the database.
- **Don't:**
  - Perform deep queries into JSON using SQL (e.g., `json_extract`). This will "lock" you into SQLite.

## 4. Explicit & Parameterized SQL

- **Do:**
  - Explicitly list column names in `SELECT` statements; do not use `SELECT *` in production code.
  - Handle `NULL` values clearly (using `COALESCE` or `IS NULL` conditions).
  - Always use **Parameterized Queries** (`?` or `:name`) to prevent SQL Injection and ensure driver compatibility.
- **Don't:**
  - Use loose comparisons (Type Coercion) - PostgreSQL will error if you compare a string to a number.

## 5. Abstraction Architecture (Repository Layer)

- **Principle:** Completely decouple the data access layer.
- **Implementation:**
  - All SQL must reside within `Repository` or `DAO` classes.
  - Business Logic should only call methods like `user_repo.get_by_id()` and should not contain SQL strings.
  - **Alembic from Day 1:** All schema changes must go through migration files. Never modify the database manually.

## 6. Handling Specific Features (Caveats)

- **Full-Text Search (FTS):** SQLite uses `FTS5`, while Postgres uses `tsvector`. If searching is required, isolate it behind an Interface so the search module can be replaced later.
- **Concurrency:** SQLite is a single-writer system. Do not design logic based on the assumption that "race conditions will never occur." These logic bugs will surface when moving to Postgres (multi-writer).
- **Avoid Using:** Triggers, engine-specific Pragma, or SQLite Extensions that have no PostgreSQL equivalent.

## 7. Migration & Testing Plan (Exit Plan)

Don't wait until you need to migrate to think about the transition:

1. **Early Cross-Testing:** Set up a small PostgreSQL instance in CI/Workstation to run the test suite for critical queries.
2. **Cut-over Scenarios:**
    - **Export:** Dump libSQL data into a standard format (SQL/CSV/JSON).
    - **Transform:** Prepare scripts for data type or timestamp conversion if necessary.
    - **Load:** Script the data import into Postgres and verify integrity (Check total count, sum, aggregates).
3. **Log & Observe:** Log slow queries and execution times to optimize early.

---

### Developer Quick Checklist (For PR Reviews)

- [ ] Schema uses standard data types with `NOT NULL/DEFAULT`.
- [ ] All database changes have an associated Alembic migration file.
- [ ] No SQLite-specific behavior or extensions used (FTS5, JSON queries).
- [ ] Timestamps are stored in UTC and handled at the Application Layer.
- [ ] SQL is contained entirely within Repositories; no `SELECT *`.
- [ ] Queries are parameterized, with no string concatenation.

**Conclusion:** By following these principles, upgrading to PostgreSQL will take only **1-3 days** instead of requiring a complete system rewrite.
