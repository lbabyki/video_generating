#!/usr/bin/env python3
"""Explicitly bootstrap one local human reviewer identity; performs no review."""
from __future__ import annotations
import argparse
from app.core.config import settings
from app.db.session import SessionLocal
from app.reviewer_identity import bootstrap_reviewer, ROLES

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--display-name",required=True)
    parser.add_argument("--role",required=True,choices=sorted(ROLES))
    args=parser.parse_args()
    with SessionLocal() as db:
        reviewer=bootstrap_reviewer(db,args.display_name,args.role)
        print(reviewer.id)
    return 0

if __name__ == "__main__": raise SystemExit(main())
