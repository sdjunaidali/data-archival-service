# Data Archival Service

Data Archival Service for relational databases. Archive old rows from a source database into an archive database based on per-table policies, enforce RBAC for viewing archives, and run scheduled archival/purge jobs with APScheduler.

## Features

- Built with FastAPI for high performance.
- Dockerized for easy deployment.
- RBAC-protected REST API: JWT-based auth.
- Create user and assign them permission for specific tables.
- Admin has access to all tables; users can access only tables they’re permitted for.
- Configure when to archive and when to delete archived data. Example: archive after 30 days, delete from archive after 365 days.
- APScheduler: In-process job scheduling for archive-delete job.

## Prerequisites

Before you begin, ensure you have the following installed:
- Docker and Docker Compose
- Python 3.10+
- PostgreSQL (via Docker)

Ports used (defaults):
- API: 8080
- Source DB: 5433
- Archive DB: 5434

## Getting Started

Follow the steps below to get your development environment up and running.

### 1. Clone the Repository
Clone this repository to your local machine using the following command:

```bash```
git clone git@github.com:sdjunaidali/data-archival-service.git
OR
git clone https://github.com/sdjunaidali/data-archival-service.git
cd data-archival-service/

### Quick Start with Docker Compose

1) Build and start:
docker compose -f docker/docker-compose.yml up -d --build

2) Check the status of services
docker ps -a --format "table {{.Names}}\t{{.Status}}"

3) Health checks:
Liveness: curl http://localhost:8080/health

4) Readiness (checks DB connectivity): curl http://localhost:8080/ready

5) Open interactive docs:
http://localhost:8080/docs

6) Check API logs
docker compose -f docker/docker-compose.yml logs -f api

5) Stop:
docker compose -f docker/docker-compose.yml down

### Admin User Add

```bash```
root@sjunaida-vm1:~/FastApi/data-archival-service# docker compose -f docker/docker-compose.yml exec source-db psql -U user -d source_db
psql (14.19 (Debian 14.19-1.pgdg13+1))
Type "help" for help.

source_db=#
source_db=#
source_db=# SELECT id, username, role FROM users WHERE role='admin';
 id | username | role
----+----------+------
(0 rows)

source_db=# INSERT INTO users (username, password_hash, role)
VALUES (
'admin',
'$bcrypt-sha256$v=2,t=2b,r=12$Vxll01UxXpeubgKfh2GNSe$UeQMr.VO1IEjI1TyAdVJRM4TD5slcNe',
'admin'
)
ON CONFLICT (username) DO NOTHING;
INSERT 0 1
source_db=#
source_db=# SELECT id, username, role FROM users WHERE role='admin';
 id | username | role
----+----------+-------
  1 | admin    | admin
(1 row)

source_db=#

source_db=#
source_db=#
source_db=#  UPDATE users SET password_hash = '$2b$12$yeCnFODKILp1zPo3uzU.CeAQmx.RxWTHbJxY5Iw3yQ73BJdJSupum' WHERE username = 'admin';
UPDATE 1
source_db=#
source_db=#
source_db=#
source_db=#
source_db=# exit
root@sjunaida-vm1:~/FastApi/data-archival-service# docker compose -f docker/docker-compose.yml exec source-db sh -lc "psql -U user -d source_db -c "SELECT id, username, role FROM users WHERE username='admin';""
--
(1 row)

root@sjunaida-vm1:~/FastApi/data-archival-service# docker compose -f docker/docker-compose.yml exec source-db psql -U user -d source_db -c "SELECT id, username, role FROM users WHERE username='admin';"
 id | username | role
----+----------+-------
  1 | admin    | admin
(1 row)

root@sjunaida-vm1:~/FastApi/data-archival-service#

root@sjunaida-vm1:~/FastApi/data-archival-service# curl -i -s -X POST http://localhost:8080/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'
HTTP/1.1 200 OK
date: Tue, 09 Sep 2025 14:11:54 GMT
server: uvicorn
content-length: 208
content-type: application/json

{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsInBlcm1pc3Npb25zIjpbXSwiZXhwIjoxNzU3NDU1OTE1fQ.zZgV2EOW3I6uydPGsE3uySLgU6lNWbc-BguLD_3OMBM","token_type":"bearer"}root@sjunaida-vm1:~/FastApi/data-archival-service#
root@sjunaida-vm1:~/FastApi/data-archival-service#

### Signup and User Permissions

```bash```

- Signup Regular User:

root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl -X POST http://localhost:8080/auth/signup -H "Content-Type: application/json" -d '{"username":"junaid","password":"junaid123"}'
{"msg":"User created"}
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

- Login (user):

root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl -s -X POST http://localhost:8080/auth/login -H "Content-Type: application/json" -d '{"username":"junaid","password":"junaid123"}'
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqdW5haWQiLCJyb2xlIjoidXNlciIsInBlcm1pc3Npb25zIjpbXSwiZXhwIjoxNzU3NDc1MDQ5fQ.IxybkgY8hhK8QQ3TIr-4H3gcY9ZfyvncXzZSmPdeK2g","token_type":"bearer"}
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

- Grant table permissions as admin:

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# ADMIN_TOKEN=$(curl -s -X POST http://localhost:8080/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}' | python -c 'import sys,json; d=json.load(sys.stdin); print(d.get("access_token",""))')
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# echo $ADMIN_TOKEN
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsInBlcm1pc3Npb25zIjpbXSwiZXhwIjoxNzU3NDc1MTE4fQ.JE_9NAPoDtNQ4OVeTzy8DcJgcjOBtCWzs6Hpa2sPgmI
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl -X POST http://localhost:8080/admin/permissions -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d '{"username":"junaid","add":["students","teachers"],"remove":[]}'
{"status":"ok"}
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#


### Creating Source Tables and Sample Data

```bash```

- Create tables (id, created_at) in source_db:

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# docker compose -f docker/docker-compose.yml exec source-db psql -U user -d source_db -c "CREATE TABLE IF NOT EXISTS students (id SERIAL PRIMARY KEY, name TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW());"
CREATE TABLE
root@sjunaida-vm1:~/FastApi/git/data-archival-service# docker compose -f docker/docker-compose.yml exec source-db psql -U user -d source_db -c "CREATE TABLE IF NOT EXISTS teachers (id SERIAL PRIMARY KEY, name TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW());"
CREATE TABLE
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

- Insert data (some old, some recent):

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# docker compose -f docker/docker-compose.yml exec source-db psql -U user -d source_db -c "INSERT INTO students (name, created_at) VALUES ('alice_old', NOW()-INTERVAL '45 days'), ('bob_old', NOW()-INTERVAL '90 days'), ('carol_new', NOW()-INTERVAL '5 days');"
INSERT 0 3
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# docker compose -f docker/docker-compose.yml exec source-db psql -U user -d source_db -c "INSERT INTO teachers (name, created_at) VALUES ('t_alice_old', NOW()-INTERVAL '60 days'), ('t_bob_old', NOW()-INTERVAL '120 days'), ('t_carol_new', NOW()-INTERVAL '3 days');"
INSERT 0 3
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

### Creating Archival Policies

```bash```

Only admin can create/update policies.

- Create policy (students):

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl -X POST http://localhost:8080/config/ -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d '{"table_name":"students","archive_after_days":30,"delete_after_days":365,"custom_criteria":null}'
{"table_name":"students","archive_after_days":30,"delete_after_days":365,"custom_criteria":null,"id":1}
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

- Create policy (teachers):

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl -X POST http://localhost:8080/config/ -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d '{"table_name":"teachers","archive_after_days":30,"delete_after_days":365,"custom_criteria":null}'
{"table_name":"teachers","archive_after_days":30,"delete_after_days":365,"custom_criteria":null,"id":2}root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

- Read specific policy:

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl -X GET http://localhost:8080/config/students -H "Authorization: Bearer $ADMIN_TOKEN"
{"table_name":"students","archive_after_days":30,"delete_after_days":365,"custom_criteria":null,"id":1}root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

- List all policies (admin-only):

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl -X GET http://localhost:8080/config/ -H "Authorization: Bearer $ADMIN_TOKEN"
[{"table_name":"students","archive_after_days":30,"delete_after_days":365,"custom_criteria":null,"id":1},{"table_name":"teachers","archive_after_days":30,"delete_after_days":365,"custom_criteria":null,"id":2}]
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

### Scheduler: APScheduler

- Starts automatically on API startup
- archival_tick: interval (e.g., every 5 minutes) to run archive_and_delete_job.
- delete_daily: daily at 02:00 UTC to delete archived rows older than delete_after_days per policy.

```bash```

- List jobs: GET http://localhost:8080/system/scheduler/jobs

root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl http://localhost:8080/system/scheduler/jobs
{"jobs":[{"id":"archival_tick","name":"archive_and_delete_job","trigger":"interval[0:05:00]","next_run_time":"2025-09-09T19:47:13.369878+00:00","func":"app.core.archival.archive_and_delete_job"},{"id":"purge_daily","name":"purge_expired_archives","trigger":"cron[hour='2', minute='0']","next_run_time":"2025-09-10T02:00:00+00:00","func":"app.core.archival.purge_expired_archives"}]}root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

- Trigger test job: POST http://localhost:8080/system/scheduler/test

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl -X POST http://localhost:8080/system/scheduler/test
{"scheduled":true,"job_id":"test_2507a867"}
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

### Manual Scheduler Run

```bash```

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# docker compose -f docker/docker-compose.yml exec api sh -lc "python -c 'from app.core.archival import archive_and_delete_job as j; j(); print(1)'"
1
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

### Viewing Archival data

Users need permission for a table to view its archives. Admin can view all tables.

```bash```

- Login as a permitted user (e.g., junaid) and capture token:

root@sjunaida-vm1:~/FastApi/git/data-archival-service# JUNAID_TOKEN=$(curl -s -X POST http://localhost:8080/auth/login -H "Content-Type: application/json" -d '{"username":"junaid","password":"junaid123"}' | python -c 'import sys,json; d=json.load(sys.stdin); print(d.get("access_token",""))')
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# echo $JUNAID_TOKEN
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqdW5haWQiLCJyb2xlIjoidXNlciIsInBlcm1pc3Npb25zIjpbInN0dWRlbnRzIiwidGVhY2hlcnMiXSwiZXhwIjoxNzU3NDc2MzIzfQ.jvsDpfyRPJhcYzh2brRZRwwa8DTLoTHv4Joxn_C7BMI
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

- List archives for students:

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl -X GET "http://localhost:8080/archives/students?limit=100&offset=0" -H "Authorization: Bearer $JUNAID_TOKEN"
[{"data":"{\"id\": 1, \"name\": \"alice_old\", \"created_at\": \"2025-07-26T19:36:08.503237+00:00\"}","archived_at":"2025-09-09T19:42:13.373089+00:00"},{"data":"{\"id\": 2, \"name\": \"bob_old\", \"created_at\": \"2025-06-11T19:36:08.503237+00:00\"}","archived_at":"2025-09-09T19:42:13.373089+00:00"}]
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

- List archives for teachers:

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl -X GET "http://localhost:8080/archives/teachers?limit=100&offset=0" -H "Authorization: Bearer $JUNAID_TOKEN"
[{"data":"{\"id\": 1, \"name\": \"t_alice_old\", \"created_at\": \"2025-07-11T19:36:23.330984+00:00\"}","archived_at":"2025-09-09T19:42:13.373089+00:00"},{"data":"{\"id\": 2, \"name\": \"t_bob_old\", \"created_at\": \"2025-05-12T19:36:23.330984+00:00\"}","archived_at":"2025-09-09T19:42:13.373089+00:00"}]
root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service#

- Admin can view all the data.

root@sjunaida-vm1:~/FastApi/git/data-archival-service#
root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl -s -H "Authorization: Bearer $ADMIN_TOKEN" http://localhost:8080/archives/teachers | jq
[
  {
    "data": "{\"id\": 1, \"name\": \"t_alice_old\", \"created_at\": \"2025-07-11T19:36:23.330984+00:00\"}",
    "archived_at": "2025-09-09T19:42:13.373089+00:00"
  },
  {
    "data": "{\"id\": 2, \"name\": \"t_bob_old\", \"created_at\": \"2025-05-12T19:36:23.330984+00:00\"}",
    "archived_at": "2025-09-09T19:42:13.373089+00:00"
  }
]
root@sjunaida-vm1:~/FastApi/git/data-archival-service# curl -s -H "Authorization: Bearer $ADMIN_TOKEN" http://localhost:8080/archives/students | jq
[
  {
    "data": "{\"id\": 1, \"name\": \"alice_old\", \"created_at\": \"2025-07-26T19:36:08.503237+00:00\"}",
    "archived_at": "2025-09-09T19:42:13.373089+00:00"
  },
  {
    "data": "{\"id\": 2, \"name\": \"bob_old\", \"created_at\": \"2025-06-11T19:36:08.503237+00:00\"}",
    "archived_at": "2025-09-09T19:42:13.373089+00:00"
  }
]
root@sjunaida-vm1:~/FastApi/git/data-archival-service#