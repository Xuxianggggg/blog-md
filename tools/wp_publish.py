import os
import re
import mimetypes
import argparse
import requests
from markdown import markdown

IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')


def env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise SystemExit(f"Missing env var: {name}")
    return v


def upload_media(wp_url, auth, file_path):
    filename = os.path.basename(file_path)
    mime, _ = mimetypes.guess_type(filename)
    mime = mime or "application/octet-stream"

    with open(file_path, "rb") as f:
        r = requests.post(
            f"{wp_url}/wp-json/wp/v2/media",
            auth=auth,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": mime,
            },
            data=f.read(),
            timeout=60,
        )
    r.raise_for_status()
    return r.json()["source_url"]


def slug_from_md_path(md_path: str) -> str:
    # 例：posts/2026-04-01-my-first-test/2026-04-01-my-first-test.md
    # slug -> 2026-04-01-my-first-test
    return os.path.splitext(os.path.basename(md_path))[0]


def find_existing_post(wp_url, auth, slug: str):
    r = requests.get(
        f"{wp_url}/wp-json/wp/v2/posts",
        auth=auth,
        params={"slug": slug, "per_page": 1},
        timeout=60,
    )
    r.raise_for_status()
    items = r.json()
    return items[0] if items else None


def main(md_path, status):
    wp_url = env("WP_URL").rstrip("/")
    wp_user = env("WP_USER")
    wp_app_pass = env("WP_APP_PASS").replace(" ", "")
    auth = (wp_user, wp_app_pass)

    base_dir = os.path.dirname(md_path)

    with open(md_path, "r", encoding="utf-8") as f:
        md = f.read()

    lines = md.splitlines()
    title = next((ln.strip() for ln in lines if ln.strip()), os.path.basename(md_path))

    # 去掉第一行标题，避免正文重复显示标题
    title_removed = False
    body_lines = []
    for ln in lines:
        if not title_removed and ln.strip():
            title_removed = True
            continue
        body_lines.append(ln)
    body_md = "\n".join(body_lines).lstrip()

    def repl(m):
        alt = m.group(1)
        link = m.group(2).strip()

        if link.startswith("http://") or link.startswith("https://"):
            return m.group(0)

        local_path = os.path.normpath(os.path.join(base_dir, link))
        if not os.path.isfile(local_path):
            return m.group(0)

        url = upload_media(wp_url, auth, local_path)
        return f"![{alt}]({url})"

    md2 = IMG_RE.sub(repl, body_md)
    html = markdown(md2, extensions=["extra", "tables", "fenced_code"])

    slug = slug_from_md_path(md_path)

    payload = {
        "title": title,
        "content": html,
        "status": status,
        "slug": slug,
    }

    old_post = find_existing_post(wp_url, auth, slug)

    if old_post:
        post_id = old_post["id"]
        r = requests.post(
            f"{wp_url}/wp-json/wp/v2/posts/{post_id}",
            auth=auth,
            json=payload,
            timeout=60,
        )
        r.raise_for_status()
        j = r.json()
        print("Updated:", j.get("link"))
    else:
        r = requests.post(
            f"{wp_url}/wp-json/wp/v2/posts",
            auth=auth,
            json=payload,
            timeout=60,
        )
        r.raise_for_status()
        j = r.json()
        print("Created:", j.get("link"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("md_path")
    ap.add_argument("--status", default="draft", choices=["draft", "publish"])
    args = ap.parse_args()
    main(args.md_path, args.status)
