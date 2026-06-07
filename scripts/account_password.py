#!/usr/bin/env python3
import argparse
import getpass
import hashlib
import json
import secrets
from datetime import datetime
from pathlib import Path


def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create or reset a Yoko CatCut file-backed account password."
    )
    parser.add_argument("--workspace", default="./workspace")
    parser.add_argument("--user", default="default-user")
    parser.add_argument("--password", default="")
    parser.add_argument("--approve", action="store_true")
    args = parser.parse_args()

    password = args.password or getpass.getpass(f"Password for {args.user}: ")
    confirm = args.password or getpass.getpass("Confirm password: ")
    if password != confirm:
        raise SystemExit("Passwords do not match")
    if len(password) < 8:
        raise SystemExit("Password must be at least 8 characters")

    workspace = Path(args.workspace)
    users_file = workspace / ".system" / "accounts" / "users.json"
    users_file.parent.mkdir(parents=True, exist_ok=True)
    account_dir = workspace / args.user
    account_dir.mkdir(parents=True, exist_ok=True)

    users = {}
    if users_file.exists():
        users = json.loads(users_file.read_text(encoding="utf-8"))

    salt = secrets.token_hex(16)
    previous = users.get(args.user, {})
    users[args.user] = {
        **previous,
        "password_hash": hash_password(password, salt),
        "salt": salt,
        "token": previous.get("token") or secrets.token_urlsafe(32),
        "created_at": previous.get("created_at") or datetime.now().isoformat(),
        "password_updated_at": datetime.now().isoformat(),
        "account_dir": str(account_dir),
        "lock_file": "" if args.approve else str(account_dir / "lock.lck"),
    }

    if args.approve:
        lock_file = account_dir / "lock.lck"
        if lock_file.exists():
            lock_file.unlink()
    else:
        (account_dir / "lock.lck").write_text(
            "Account is locked. Delete this file to approve login.\n",
            encoding="utf-8",
        )

    temporary = users_file.with_suffix(".tmp")
    temporary.write_text(json.dumps(users, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(users_file)

    print(f"Updated account: {args.user}")
    print(f"Users file: {users_file}")
    print(f"Approved: {'yes' if args.approve else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
