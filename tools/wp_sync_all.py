import os
import re
import mimetypes
import argparse
from pathlib import Path

import requests
from markdown import markdown

IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
MANAGED_TAG_NAME = "_git_sync"


def env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise SystemExit(f"Missing env var: {name}")
    return v


def slugify(text: str) -> str:
    text = text.strip().lower().replace(" ", "-")
    text = re.sub(r"-+", "-", text)
    return text


def upload_media(wp_url, auth, file_path):
    filename = os.path.basename(file_path)
    mime, _ = mimetypes.guess_type(filename)
    mime = mime or "application/octet-stream"

    with open(file_path, "rb") as f:
        r = requests.post(
            f"{wp_url}/wp-json/wp/v2/media",
            auth=auth,
            headers={
                "Content-Disposition": f'attachment; filename=\"{filename}\"',
                "Content-Type": mime,
            },
            data=f.read(),
            timeout=60,
        )
    r.raise_for_status()
    return r.json()["source_url"]


def get_or_create_category(wp_url, auth, category_name: str) -> int:
    r = requests.get(
        f"{wp_url}/wp-json/wp/v2/categories",
        auth=auth,
        params={"search": category_name, "per_page": 100},
        timeout=60,
    )
    r.raise_for_status()
    for item in r.json():
        if item.get("name") == category_name:
            return item["id"]

    payload = {
        "name": category_name,
        "slug": slugify(category_name),
    }
    r = requests.post(
        f"{wp_url}/wp-json/wp/v2/categories",
        auth=auth,
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["id"]


def get_or_create_tag(wp_url, auth, tag_name: str) -> int:
    r = requests.get(
        f"{wp_url}/wp-json/wp/v2/tags",
        auth=auth,
        params={"search": tag_name, "per_page": 100},
        timeout=60,
    )
    r.raise_for_status()
    for item in r.json():
        if item.get("name") == tag_name:
            return item["id"]

    payload = {
        "name": tag_name,
        "slug": slugify(tag_name),
    }
    r = requests.post(
        f"{wp_url}/wp-json/wp/v2/tags",
        auth=auth,
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["id"]


def parse_category_and_slug(md_path: str):
    # 规则：posts/分类名/文章.md
    rel = os.path.normpath(md_path)
    parts = rel.split(os.sep)

    if len(parts) < 3 or parts[0] != "posts":
        raise SystemExit(f"Invalid post path: {md_path}")

    category_name = parts[1]
    file_stem = os.path.splitext(parts[-1])[0]

    # slug = 分类 + 文件名，避免不同分类里同名文章冲突
    slug = f"{slugify(category_name)}-{slugify(file_stem)}"
    return category_name, slug


def list_repo_markdowns(root="posts"):
    md_files = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(".md"):
                md_files.append(os.path.join(dirpath, fn))
    md_files.sort()
    return md_files


def find_existing_post_by_slug(wp_url, auth, slug: str):
    r = requests.get(
        f"{wp_url}/wp-json/wp/v2/posts",
        auth=auth,
        params={"slug": slug, "per_page": 1, "status": "publish"},
        timeout=60,
    )
    r.raise_for_status()
    items = r.json()
    return items[0] if items else None


def list_managed_posts(wp_url, auth, managed_tag_id: int):
    posts = []
    page = 1
    while True:
        r = requests.get(
            f"{wp_url}/wp-json/wp/v2/posts",
            auth=auth,
            params={
                "tags": managed_tag_id,
                "status": "publish",
                "per_page": 100,
                "page": page,
            },
            timeout=60,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        posts.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return posts


def delete_post(wp_url, auth, post_id: int, force: bool = False):
    # force=False -> 进回收站；force=True -> 永久删除
    r = requests.delete(
        f"{wp_url}/wp-json/wp/v2/posts/{post_id}",
        auth=auth,
        params={"force": str(force).lower()},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def render_markdown(md_path: str, wp_url: str, auth):
    base_dir = os.path.dirname(md_path)

    with open(md_path, "r", encoding="utf-8") as f:
        md = f.read()

    lines = md.splitlines()

    # 第一行非空内容作为标题；支持 "# 标题"
    title = next(
        (ln.strip().lstrip("#").strip() for ln in lines if ln.strip()),
        os.path.basename(md_path),
    )

    # 正文去掉第一行标题
    title_removed = False
    body_lines = []
    for ln in lines:
        if not title_removed and ln.strip():
            title_removed = True
            continue
        body_lines.append(ln)
    body_md = "\n".join(body_lines).lstrip()

    def repl(match):
        alt_text = match.group(1)
        img_path = match.group(2).strip()

        if img_path.startswith("http://") or img_path.startswith("https://"):
            return match.group(0)

        abs_path = os.path.normpath(os.path.join(base_dir, img_path))
        if not os.path.exists(abs_path):
            print(f"Warning: image not found: {abs_path}")
            return match.group(0)

        try:
            media_url = upload_media(wp_url, auth, abs_path)
            return f"![{alt_text}]({media_url})"
        except Exception as e:
            print(f"Warning: failed to upload image {abs_path}: {e}")
            return match.group(0)

    md2 = IMG_RE.sub(repl, body_md)
    html = markdown(md2, extensions=["extra", "tables", "fenced_code"])
    return title, html


def upsert_post(wp_url, auth, md_path: str, status: str, managed_tag_id: int):
    category_name, slug = parse_category_and_slug(md_path)
    category_id = get_or_create_category(wp_url, auth, category_name)
    title, html = render_markdown(md_path, wp_url, auth)

    payload = {
        "title": title,
        "content": html,
        "status": status,
        "slug": slug,
        "categories": [category_id],
        "tags": [managed_tag_id],
    }

    old_post = find_existing_post_by_slug(wp_url, auth, slug)
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

    return slug


def main(status: str, force_delete: bool):
    wp_url = env("WP_URL").rstrip("/")
    wp_user = env("WP_USER")
    wp_app_pass = env("WP_APP_PASS").replace(" ", "")
    auth = (wp_user, wp_app_pass)

    managed_tag_id = get_or_create_tag(wp_url, auth, MANAGED_TAG_NAME)

    # 1) 先把仓库里当前存在的所有 md 全部同步到 WP
    repo_md_files = list_repo_markdowns("posts")
    desired_slugs = set()

    print("Current markdown files:")
    for md_file in repo_md_files:
        print(" -", md_file)
        slug = upsert_post(wp_url, auth, md_file, status, managed_tag_id)
        desired_slugs.add(slug)

    # 2) 再把 WP 里已不存在于仓库的“受管文章”删掉
    wp_posts = list_managed_posts(wp_url, auth, managed_tag_id)

    print("Checking for deleted posts...")
    for post in wp_posts:
        post_slug = post.get("slug", "")
        post_id = post.get("id")
        if post_slug not in desired_slugs:
            result = delete_post(wp_url, auth, post_id, force=force_delete)
            print("Deleted:", result.get("previous", {}).get("link") or post_slug)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="publish", choices=["draft", "publish"])
    ap.add_argument("--force-delete", action="store_true",
                    help="永久删除；不加这个参数则先进回收站")
    args = ap.parse_args()
    main(args.status, args.force_delete)
