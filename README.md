# worship-team-rota

## What is it

A simple rota program to help my church build its rosters.

## Stack

Flask + SQLAlchemy + SQLite — the stack I learned during this project.

## How to run

```bash
git clone https://github.com/oiagod/worship-team-rota.git
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app hello run
```

No environment variables needed — the database URI is set directly in
`hello.py`.

## Data modeling

User, Service, Roster

> Roster is an association object between Service and User, because the
> relationship needed to be many-to-many — but with an extra field (`role`),
> so a plain association table wasn't enough.

## Decisions worth explaining

- Roster has its own primary key instead of a composite key (user_id +
  service_id), so the same person can be assigned to a service with two
  different roles at once.
- The roster view is organized by service, not by user — a schedule
  naturally starts from "which service am I building the team for", not
  from a single person's assignments.

## What I learned

- Mixed up naive and aware datetimes early on — `fromisoformat` doesn't
  set a timezone by itself, and it caused inconsistent comparisons. Still
  a known tech debt item to clean up properly.
- Ran into `PendingRollbackError` from leaving a broken session
  uncommitted, and a "database is locked" error from having `flask shell`
  open at the same time as the running app — both taught me that SQLite
  doesn't handle concurrent writers well.

## Next steps

- Admin login (Flask-Login) — restrict edit/delete routes to logged-in
  admins
- Member self-service (mark unavailability for a given date)
- Repertoire per service (song, key, BPM, links)

**Project link:** [worship-team-rota.onrender.com](https://worship-team-rota.onrender.com)
