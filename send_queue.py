"""Send the best pending apply-queue jobs to Telegram (ones not sent before).

    python send_queue.py            # up to 25 jobs, best score first
    python send_queue.py --limit 10

Jobs that were only "marked as seen" (never messaged) are in apply_queue.json too; this sends
them once and flags each item with "telegram_sent": true so it is never sent twice.
"""

import argparse
import json
import logging
import os
import sys

import yaml

from apply_queue import load_queue, save_queue
from telegram_notifier import build_targets, notify_jobs_telegram

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("send_queue")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()

    if os.environ.get("ALL_SECRETS"):
        for k, v in json.loads(os.environ["ALL_SECRETS"]).items():
            if isinstance(v, str) and v and k not in os.environ:
                os.environ[k] = v

    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    tg_cfg = config.get("telegram", {})
    token = os.environ.get(tg_cfg.get("bot_token_env", "TELEGRAM_BOT_TOKEN"))
    targets = build_targets(tg_cfg) if token else {}
    if not targets:
        sys.exit("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID missing")

    queue = load_queue()
    todo = sorted((i for i in queue if i.get("status") == "pending" and not i.get("telegram_sent")),
                  key=lambda i: i.get("score") or 0, reverse=True)[: args.limit]
    if not todo:
        print("No unsent pending jobs in the apply queue.")
        return

    jobs = [{
        "Job ID": i.get("job_id"),
        "Job Title": i.get("title"),
        "Company": i.get("company"),
        "Location": i.get("location"),
        "Category": i.get("category"),
        "Job Type": i.get("job_type"),
        "Source": i.get("source"),
        "Position Link": i.get("link"),
        "Match Score": i.get("score"),
        "Matched Skills": i.get("matched_skills"),
        "Highlight": True,
    } for i in todo]
    sent = notify_jobs_telegram(token, targets, jobs)

    sent_ids = {i.get("job_id") for i in todo[:sent]}
    for item in queue:
        if item.get("job_id") in sent_ids:
            item["telegram_sent"] = True
    save_queue(queue)
    left = sum(1 for i in queue if i.get("status") == "pending" and not i.get("telegram_sent"))
    print(f"Sent {sent} apply-queue jobs to Telegram ({left} more unsent).")


if __name__ == "__main__":
    main()
