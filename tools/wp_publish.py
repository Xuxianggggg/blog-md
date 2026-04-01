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
    wp_app_pass = env("WP_APP_PASS").replace(" ", "")  # remove spaces if any
    auth = (wp_user, wp_app_pass)

    base_dir = os.path.dirname(md_path)
    md = open(md_path, "r", encoding="utf-8").read()

    # Title = first non-empty line
    lines = md.splitlines()
    title = next((ln.strip() for ln in lines if ln.strip()), os.path.basename(md_path))
    
    # Remove the title line from body once
    title_removed = False
    body_lines = []
    for ln in lines:
        if not title_removed and ln.strip():
            title_removed = True
            continue
        body_lines.append(ln)
    body_md = "\n".join(body_lines).lstrip()
    
    # Upload local images and replace links
    md2 = IMG_RE.sub(repl, body_md)

    # Convert to HTML for WordPress
    html = markdown(md2, extensions=["extra", "tables", "fenced_code"])

    # Create post
    payload = {
        "title": title,
        "content": html,
        "status": status,   # "draft" or "publish"
    }
    r = requests.post(f"{wp_url}/wp-json/wp/v2/posts", auth=auth, json=payload, timeout=60)
    r.raise_for_status()
    j = r.json()
    print("Created:", j.get("link"))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("md_path")
    ap.add_argument("--status", default="draft", choices=["draft", "publish"])
    args = ap.parse_args()
    main(args.md_path, args.status)
