# py-forge

A FastAPI/SQLAlchemy/Postgres backend starter, ported from the NestJS "nest-forge" project. Its data model is platform infrastructure — identity, role-based access control, auth credentials, logging, and configuration — with no business domain of its own yet.

## Language

### Identities

**Admin**:
A privileged operator of the platform, authenticated by email and password and governed by role-based access control. A distinct identity from a User — the two never share a record.
_Avoid_: User (for an admin), staff, operator

**User**:
An end consumer of the application, whose primary identity is a phone number (SMS), optionally linked to a Google or Apple account. Not governed by RBAC.
_Avoid_: Customer, account, member, client

### Access Control

**Role**:
A named bundle of Permissions assigned to an Admin. Carries a rank where a lower number means higher privilege (rank 1 = superadmin).
_Avoid_: Group, tier

**Module**:
A feature area of the system that a Permission applies to. Modules form a tree (a Module may have a parent Module).
_Avoid_: Feature, section, resource

**Permission**:
The right to perform one action (create, read, update, or delete) on one Module. Permissions are granted to Roles, never directly to an Admin.
_Avoid_: Grant, privilege, scope

### Auth Credentials

**OTP**:
A short-lived one-time code issued to a User or an Admin for either two-factor authentication or password reset.
_Avoid_: PIN, code, token (for an OTP)

**Refresh Token**:
A long-lived credential held by a User or an Admin, exchanged to mint new short-lived access tokens. Stored only as a hash.
_Avoid_: Session, access token (these are different)

### Observability

**Activity Log**:
An append-only record of a single action taken by a User.
_Avoid_: Audit Log (that is the Admin equivalent), event, history

**Audit Log**:
An append-only record of a single action taken by an Admin, capturing the before and after state of the affected entity.
_Avoid_: Activity Log (that is the User equivalent), change log

### Configuration

**Setting**:
A system-wide configuration entry stored as a key with a JSON value.
_Avoid_: Config, preference, option
