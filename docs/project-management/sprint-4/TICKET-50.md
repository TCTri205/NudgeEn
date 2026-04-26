# TICKET-50: Database Backup & Recovery Drills

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 4
- **Assignee:** DevOps Engineer
- **Domain:** Data Durability / SRE
- **Priority:** P0 - Critical
- **Assumptions:**
  - Managed Postgres often includes daily backups.
- **Affected areas:** Infrastructure config, Backup policy.

## Current State / Existing System

- **Implemented:** Local DB setup (TICKET-03).
- **Missing:** Any automated backup strategy or verified recovery plan. If a disk fails in production today, all user data is lost.

## Context / Problem

Data is the lifeblood of NudgeEn. We need to guarantee that even in a total disaster, we can recover user messages and profiles with minimal data loss. A backup that isn't tested for recovery is not a backup.

## Why This Is Needed

- **Business Impact:** Total Risk Mitigation. Prevents permanent data loss that would end the project.
- **Architectural Impact:** Defines the "Recovery Point Objective" (RPO) and "Recovery Time Objective" (RTO).

## Scope

### In-scope

- Enable Automated Backups:
  - Daily full snapshots.
  - Point-in-time recovery (PITR) if supported.
- Setup Off-site Backups:
  - Sync snapshots to a secondary cloud region or a separate S3 bucket.
- Documentation:
  - Step-by-step "Disaster Recovery Playbook."
- **The "Drill":**
  - Purposefully delete a test production database.
  - Restore it using the backup.
  - Verify all data integrity.

### Out-of-scope

- Multi-master replication.

## Dependencies / Parallelism

- **Dependencies:** TICKET-44 (Production Deployment).
- **Parallelism:** Can be done immediately after production is live.

## Rules / Constraints

- 30-day minimum retention for backups.
- Backups must be encrypted at rest.

## What Needs To Be Built

1. Automated backup schedule configuration.
2. `RECOVERY.md`: A manual for the dev team.

## Proposal

Use the managed backup service of the hosting provider (e.g., Railway/Supabase daily backups). Supplement this with a weekly manual dump (`pg_dump`) to an external S3 bucket via a GitHub Action for redundancy.

## Implementation Breakdown

1. **Provisioning:** Turn on the "Auto-Backup" toggle.
2. **Automation:** Setup the S3 sync job.
3. **The Drill:** Schedule a 1-hour window to perform a manual restore.
4. **Validation:** Query the restored DB to ensure the `user_memories` count matches the pre-deletion state.

## Acceptance Criteria

- [ ] At least one verified backup exists in an external storage location (e.g., S3).
- [ ] A restore operation has been successfully completed by a human in < 30 minutes.
- [ ] Restore documentation is clear and includes screenshots/commands.

## Test Cases

### Happy Path

- Daily backup runs -> File appears in S3 -> Log confirms Success.

### Failure Path

- Backup fails -> Alert triggers in Slack immediately.

### Regression Tests

- Verify that a restored database preserves all Foreign Key relationships and indexes.
