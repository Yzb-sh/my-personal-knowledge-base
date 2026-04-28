"""CLI tool for Knowledge Base search.

Thin wrapper that calls the FastAPI server over HTTP.
Used by QClaw skills via shell exec.

Usage:
    python kb_tool.py search "列存储原理"
    python kb_tool.py search "列存储原理" -k 3
    python kb_tool.py check "Kelly Criterion"
"""

import argparse
import json
import sys

import requests

BASE_URL = "http://127.0.0.1:28790"


def cmd_search(query: str, top_k: int = 5):
    r = requests.post(f"{BASE_URL}/search", json={"query": query, "top_k": top_k})
    r.raise_for_status()
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))


def cmd_check(topic: str):
    r = requests.post(f"{BASE_URL}/check", json={"topic": topic})
    r.raise_for_status()
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Knowledge Base CLI")
    sub = parser.add_subparsers(dest="command")

    search_p = sub.add_parser("search", help="Search the knowledge base")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("-k", "--top-k", type=int, default=5, help="Number of results")

    check_p = sub.add_parser("check", help="Check if a topic exists")
    check_p.add_argument("topic", help="Topic to check")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "search":
            cmd_search(args.query, args.top_k)
        elif args.command == "check":
            cmd_check(args.topic)
    except requests.exceptions.ConnectionError:
        print(
            "Error: Search server not running.",
            "Start with: uvicorn server:app --host 127.0.0.1 --port 28790",
            sep="\n",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
