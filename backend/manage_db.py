import argparse
from datetime import datetime
from sqlalchemy import text, inspect

from app import app, db
from .models import User, SiteSetting


def with_ctx(func):
    def wrapper(*args, **kwargs):
        with app.app_context():
            return func(*args, **kwargs)
    return wrapper


@with_ctx
def list_tables():
    insp = inspect(db.engine)
    tables = insp.get_table_names()
    print("Tables (", len(tables), "):", sep="")
    for t in tables:
        print(" -", t)


@with_ctx
def exec_sql(sql: str):
    try:
        res = db.session.execute(text(sql))
        # If it's a SELECT, show first rows
        if sql.strip().lower().startswith("select"):
            rows = res.fetchmany(20)
            for r in rows:
                print(dict(r._mapping))
        else:
            db.session.commit()
            print("OK (committed)")
    except Exception as e:
        print("ERROR:", e)


@with_ctx
def list_users():
    users = User.query.order_by(User.id.asc()).limit(50).all()
    print(f"Users ({len(users)}):")
    for u in users:
        print({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'email_verified': u.email_verified,
            'created_at': u.created_at,
        })


@with_ctx
def set_password(email: str, password: str):
    u = User.query.filter_by(email=email).first()
    if not u:
        print("User not found")
        return
    u.set_password(password)
    db.session.commit()
    print("Password updated for", email)


@with_ctx
def verify_user(email: str):
    u = User.query.filter_by(email=email).first()
    if not u:
        print("User not found")
        return
    u.email_verified = True
    u.email_verified_at = datetime.utcnow()
    db.session.commit()
    print("Email verified for", email)


@with_ctx
def set_setting(key: str, value: str):
    s = SiteSetting.query.filter_by(key=key).first()
    if not s:
        s = SiteSetting(key=key, value=value)
        db.session.add(s)
    else:
        s.value = value
    db.session.commit()
    print(f"Setting '{key}' = {value}")


def main():
    parser = argparse.ArgumentParser(description="Admissions DB manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-tables")

    p_exec = sub.add_parser("exec-sql")
    p_exec.add_argument("sql", help="SQL to execute, wrap in quotes")

    sub.add_parser("list-users")

    p_setpwd = sub.add_parser("set-password")
    p_setpwd.add_argument("email")
    p_setpwd.add_argument("password")

    p_verify = sub.add_parser("verify-user")
    p_verify.add_argument("email")

    p_setting = sub.add_parser("set-setting")
    p_setting.add_argument("key")
    p_setting.add_argument("value")

    args = parser.parse_args()

    if args.cmd == "list-tables":
        list_tables()
    elif args.cmd == "exec-sql":
        exec_sql(args.sql)
    elif args.cmd == "list-users":
        list_users()
    elif args.cmd == "set-password":
        set_password(args.email, args.password)
    elif args.cmd == "verify-user":
        verify_user(args.email)
    elif args.cmd == "set-setting":
        set_setting(args.key, args.value)


if __name__ == "__main__":
    main()
