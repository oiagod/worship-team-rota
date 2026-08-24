# worship-team-rota

## What is it

A rota management system to help worship ministries build and share their
service schedules — who's playing, singing, or serving on a given date.

## Stack

Flask + SQLAlchemy + Postgres (prod) / SQLite (local) — session-based
authentication, no third-party auth library.

## How to run

```bash
git clone https://github.com/oiagod/worship-team-rota.git
cd worship-team-rota
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root with:

```env
SECRET_KEY=your-random-secret-here
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-admin-password
```

`SECRET_KEY` should be generated with:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

`ADMIN_EMAIL` / `ADMIN_PASSWORD` define the first admin account, which is
created automatically on startup if no admin exists yet — no manual shell
step required.

```bash
flask --app hello run
```

## Data modeling

`User`, `Service`, `Roster`

- `Roster` is an association object between `Service` and `User`, not a
  plain association table — the relationship is many-to-many, but each
  assignment also carries an extra field (`role`, e.g. "vocal", "guitar"),
  so a plain table wasn't enough.
- Every `User` has an `access_level` (`"admin"` or `"member"`), separate
  from `Roster.role`. `access_level` controls system permissions; `role`
  describes what someone is playing in a specific service. The same
  person can be an admin and still show up in the schedule as a musician.
- `password_hash` is optional — most `User`s are schedulable members who
  never log in; only admins authenticate.

## Decisions worth explaining

- Login uses email, not username — usernames add a field people forget,
  while email is unique by nature and easier to remember.
- The first admin is bootstrapped automatically at startup (from
  `ADMIN_EMAIL`/`ADMIN_PASSWORD`) instead of through a public signup
  route or a manual shell command. This matters specifically because the
  hosting platform doesn't provide shell access on the free tier, so the
  app needs to be able to self-initialize on every deploy.
- `Roster` has its own primary key instead of a composite key (user_id +
  service_id), so the same person can be assigned to a service with two
  different roles at once.

## What I learned

- Mixed up naive and aware datetimes early on — `fromisoformat` doesn't
  set a timezone by itself, and it caused inconsistent comparisons. Still
  a known tech debt item to clean up properly.
- Connecting to Postgres requires a separate driver (`psycopg2-binary`)
  that isn't bundled with Python, unlike SQLite — missing it caused a
  deploy failure that looked unrelated at first glance.
- Session-based auth without a library like Flask-Login means owning
  every edge case yourself — invalid credentials, protected routes,
  logout — which was slower to build but made the mechanics fully clear.

## Next steps

- Automated tests (pytest) for the authentication flow
- Public signup with an admin approval step (currently closed —
  self-registration will reopen once approval is in place)
- Repertoire per service (song, key per worship leader, links)

**Project link:** [worship-team-rota.onrender.com](https://worship-team-rota.onrender.com)
