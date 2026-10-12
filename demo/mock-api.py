#!/usr/bin/env python3
"""Mock backend for the KSI React (Next.js) frontend demo (runs on 127.0.0.1:3030)."""
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

TASKS = [
    {"id": 2, "title": "Základy", "wave": 1, "prerequisities": []},
    {"id": 1, "title": "Úvod", "wave": 1, "prerequisities": []},
    {"id": 5, "title": "Funkce", "wave": 1, "prerequisities": [1]},
    {"id": 3, "title": "Cykly", "wave": 1, "prerequisities": [1]},
    {"id": 4, "title": "Pole", "wave": 1, "prerequisities": [2]},
    {"id": 8, "title": "Grafy", "wave": 1, "prerequisities": [5, 4]},
    {"id": 6, "title": "Rekurze", "wave": 1, "prerequisities": [3, 5]},
    {"id": 7, "title": "Třídění", "wave": 1, "prerequisities": [4, 3]},
    {"id": 9, "title": "Dynamika", "wave": 1, "prerequisities": [6, 7]},
    {"id": 10, "title": "Finále", "wave": 1, "prerequisities": [8, 9]},
]
for t in TASKS:
    t.update({"author": 1, "co_author": 1, "details": 1, "intro": "",
              "max_score": 10, "time_published": "2026-01-01T00:00:00",
              "time_deadline": "2026-12-31T00:00:00", "state": "base",
              "picture_base": "task", "picture_suffix": ".svg",
              "feedbacks": 0})

WAVES = [{"index": 0, "caption": "Nultá vlna", "garant": 1, "year": 1,
          "id": 1, "_public": True, "sum_points": 100, "tasks_cnt": 10}]

USERS = [
    {"id": 1, "first_name": "Petr", "last_name": "Svoboda", "email": "petr@example.cz", "gender": "male",
     "role": "org", "profile_picture": None, "score": 42, "tasks_num": 5, "achievements": [1],
     "enabled": True, "nick_name": "petr", "seasons": [2026], "successful": False, "cheat": False,
     "tasks": [], "co_tasks": [], "short_info": ""},
    {"id": 2, "first_name": "Eva", "last_name": "Malá", "email": "eva@example.cz", "gender": "female",
     "role": "participant", "profile_picture": None, "score": 30, "tasks_num": 3, "achievements": [],
     "enabled": True, "nick_name": "eva", "seasons": [2026], "successful": False, "cheat": False,
     "tasks": [], "co_tasks": [], "short_info": ""},
    {"id": 3, "first_name": "Jan", "last_name": "Novák", "email": "jan.novak@example.cz", "gender": "male",
     "role": "participant", "profile_picture": None, "score": 25, "tasks_num": 2, "achievements": [],
     "enabled": True, "nick_name": "jan", "seasons": [2026], "successful": False, "cheat": False,
     "tasks": [], "co_tasks": [], "short_info": ""},
]

EXECS = [
    {"id": 101, "module": 7, "user": 3, "code": "print('ahoj')",
     "result": "ok", "time": "2026-10-01T10:00:00", "report": "OK"},
    {"id": 102, "module": 7, "user": 3, "code": "print('svet')",
     "result": "ok", "time": "2026-10-02T11:00:00", "report": "OK"},
    {"id": 103, "module": 7, "user": 3, "code": "print('ksi')",
     "result": "error", "time": "2026-10-03T12:00:00", "report": "SyntaxError"},
]

THREADS = [
    {"id": 1, "title": "Vítejte ve fóru", "wave": 1, "posts_count": 3, "unread": 1},
    {"id": 2, "title": "Dotazy k úlohám", "wave": 1, "posts_count": 2, "unread": 0},
]

POSTS = {
    1: [
        {"id": 11, "thread": 1, "author": 3, "parent": None,
         "body": "<p>Ahoj, jak začít s první úlohou?</p>",
         "published_at": "2026-10-01T10:00:00", "modified_at": "2026-10-01T10:00:00",
         "resolved_at": None, "reaction": [12, 13]},
        {"id": 12, "thread": 1, "author": 1, "parent": 11,
         "body": "<p>Stačí si přečíst zadání a odevzdat řešení.</p>",
         "published_at": "2026-10-01T11:00:00", "modified_at": "2026-10-01T11:00:00",
         "resolved_at": "2026-10-02T09:00:00", "reaction": []},
        {"id": 13, "thread": 1, "author": 3, "parent": 11,
         "body": "<p>Díky, už to mám!</p>",
         "published_at": "2026-10-02T10:00:00", "modified_at": "2026-10-02T10:00:00",
         "resolved_at": None, "reaction": []},
    ],
    2: [
        {"id": 21, "thread": 2, "author": 2, "parent": None,
         "body": "<p>Nerozumím zadání úlohy Grafy.</p>",
         "published_at": "2026-10-03T10:00:00", "modified_at": "2026-10-03T10:00:00",
         "resolved_at": None, "reaction": []},
    ],
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.end_headers()

    def _route(self, method):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        p = u.path

        if p == "/basicProfile":
            return self._send({"basicProfile": {
                "signed_in": True, "id": 1, "role": "admin",
                "first_name": "Demo", "last_name": "Admin",
                "email": "demo@example.cz", "gender": "male"}})
        if p == "/years":
            return self._send({"years": [{"id": 1, "year": "2026"}]})
        if p == "/tasks":
            return self._send({"tasks": TASKS})
        m = re.match(r"^/tasks/(\d+)$", p)
        if m and method == "GET":
            task_id = int(m.group(1))
            task = next((t for t in TASKS if t["id"] == task_id), None)
            if task:
                return self._send({"task": task})
            return self._send({}, 404)
        if p == "/waves":
            return self._send({"waves": WAVES})
        if p == "/users":
            return self._send({"users": USERS})
        if p == "/articles":
            return self._send({"articles": []})
        if p == "/threads":
            return self._send({"threads": THREADS})
        m = re.match(r"^/threadDetails/(\d+)$", p)
        if m and method == "GET":
            tid = int(m.group(1))
            posts = POSTS.get(tid, [])
            root = [post["id"] for post in posts if post["parent"] is None]
            return self._send({
                "threadDetails": {"id": tid, "root_posts": root},
                "posts": posts,
            })
        m = re.match(r"^/taskDetails/(\d+)$", p)
        if m and method == "GET":
            task_id = int(m.group(1))
            task = next((t for t in TASKS if t["id"] == task_id), None)
            title = task["title"] if task else "Úloha"
            return self._send({
                "taskDetails": {
                    "id": task_id,
                    "body": f"<p>Zadání úlohy <b>{title}</b>. Demo obsah.</p>",
                    "thread": 1,
                    "modules": [],
                    "best_scores": [],
                    "comment": None,
                    "solution": "",
                    "achievements": [],
                },
                "achievements": [],
                "posts": [],
                "modules": [],
                "moduleScores": [],
            })
        m = re.match(r"^/threads/(\d+)$", p)
        if m and method == "PUT":
            return self._send({})
        if m and method == "GET":
            tid = int(m.group(1))
            thread = next((t for t in THREADS if t["id"] == tid), None)
            if thread:
                return self._send({"thread": thread})
            return self._send({}, 404)
        m = re.match(r"^/posts/(\d+)/resolve$", p)
        if m:
            pid = int(m.group(1))
            for posts in POSTS.values():
                for post in posts:
                    if post["id"] == pid:
                        if method == "POST":
                            post["resolved_at"] = "2026-10-12T12:00:00"
                        else:
                            post["resolved_at"] = None
                        return self._send({"post": post})
            return self._send({}, 404)
        if p.startswith("/users/"):
            uid = int(p.rsplit("/", 1)[-1])
            user = next((x for x in USERS if x["id"] == uid), None)
            return self._send({"user": user} if user else {}, 200 if user else 404)
        if p == "/admin/execs":
            uid = q.get("user", [None])[0]
            mod = q.get("module", [None])[0]
            execs = [e for e in EXECS
                     if (uid is None or str(e["user"]) == uid)
                     and (mod is None or str(e["module"]) == mod)]
            return self._send({"execs": execs, "meta": {"total": len(execs)}})
        if p.startswith("/task/") and p.endswith(".svg"):
            svg = (b'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">'
                   b'<rect width="64" height="64" rx="14" fill="#e8a13c"/>'
                   b'<text x="32" y="42" font-size="30" text-anchor="middle" fill="#fff">?</text></svg>')
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(svg)))
            self.end_headers()
            self.wfile.write(svg)
            return
        return self._send({})

    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            self.rfile.read(length)
        self._route("POST")

    def do_PUT(self):
        self._route("PUT")

    def do_DELETE(self):
        self._route("DELETE")


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", 3030), Handler)
    print("mock API on :3030", flush=True)
    srv.serve_forever()
