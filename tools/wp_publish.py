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


def parse_category_and_slug(md_path: str):
    # 例：posts/AI/openclaw-notes.md
    rel = os.path.normpath(md_path)
    parts = rel.split(os.sep)

    if len(parts) < 3 or parts[0] != "posts":
        raise SystemExit(f"Invalid post path: {md_path}")

    category_name = parts[1]
    file_stem = os.path.splitext(parts[-1])[0]

    # slug = 分类名 + 文件名，避免不同分类下同名文章冲突
    category_slug = category_name.strip().lower().replace(" ", "-")
    post_slug = file_stem.strip().lower().replace(" ", "-")
    slug = f"{category_slug}-{post_slug}"

    return category_name, slug


def get_or_create_category(wp_url, auth, category_name: str):
    r = requests.get(
        f"{wp_url}/wp-json/wp/v2/categories",
        auth=auth,
        params={"search": category_name, "per_page": 100},
        timeout=60,
    )
    r.raise_for_status()
    items = r.json()

    for item in items:
        if item.get("name") == category_name:
            return item["id"]

    payload = {
        "name": category_name,
        "slug": category_name.strip().lower().replace(" ", "-"),
    }
    r = requests.post(
        f"{wp_url}/wp-json/wp/v2/categories",
        auth=auth,
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["id"]


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
    title = next((ln.strip().lstrip("#").strip() for ln in lines if ln.strip()), os.path.basename(md_path))

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

    category_name, slug = parse_category_and_slug(md_path)
    category_id = get_or_create_category(wp_url, auth, category_name)

    payload = {
        "title": title,
        "content": html,
        "status": status,
        "slug": slug,
        "categories": [category_id],
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
        print("Updated:", r.json().get("link"))
    else:
        r = requests.post(
            f"{wp_url}/wp-json/wp/v2/posts",
            auth=auth,
            json=payload,
            timeout=60,
        )
        r.raise_for_status()
        print("Created:", r.json().get("link"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("md_path")
    ap.add_argument("--status", default="draft", choices=["draft", "publish"])
    args = ap.parse_args()
    main(args.md_path, args.status)
