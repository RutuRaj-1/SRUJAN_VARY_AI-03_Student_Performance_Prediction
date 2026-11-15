import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath("backend"))

from app.db.session import get_engine, check_database_connection
from sqlalchemy import text

ok, msg, lat = check_database_connection()
print(f"DB connection verified: {ok} ({msg}, latency={lat}ms)")
engine = get_engine()
with engine.connect() as conn:
    res = conn.execute(text("SELECT version_num FROM alembic_version;"))
    print("Alembic version:", [r[0] for r in res])
    res_tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"))
    tables = [r[0] for r in res_tables]
    print(f"Total tables ({len(tables)}):")
    for t in tables:
        print(f"  - {t}")

    # Inspect RLS status on public tables
    rls_res = conn.execute(text("SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;"))
    print("\nRow Security Status:")
    for row in rls_res:
        print(f"  {row[0]}: rowsecurity={row[1]}")
