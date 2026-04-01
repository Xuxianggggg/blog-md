import os, re, mimetypes, argparse
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

def main(md_path, status):
    wp_url = env("WP_URL").rstrip("/")
    wp_user = env("WP_USER")
    wp_app_pass = env("WP_APP_PASS").replace(" ", "")
    auth = (wp_user, wp_app_pass)

    base_dir = os.path.dirname(md_path)
    with open(md_path, "r", encoding="utf-8") as f:
        md = f.read()

    # 第一行非空内容作为标题
    lines = md.splitlines()
    title = next((ln.strip() for ln in lines if ln.strip()), os.path.basename(md_path))

    # 正文去掉第一行标题
    title_removed = False
    body_lines = []
    for ln in lines:
        if not title_removed and ln.strip():
            title_removed = True
            continue
        body_lines.append(ln)
    body_md = "\n".join(body_lines).lstrip()

    # 处理 Markdown 里的本地图片
    def repl(match):
        alt_text = match.group(1)
        img_path = match.group(2).strip()

        # 远程图片直接保留
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

    # Markdown 转 HTML
    html = markdown(md2, extensions=["extra", "tables", "fenced_code"])

    # 创建文章
    payload = {
        "title": title,
        "content": html,
        "status": status,
    }

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
