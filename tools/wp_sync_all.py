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
        return j.get("slug", slug)   # 关键：返回 WordPress 实际 slug
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
        return j.get("slug", slug)   # 关键：返回 WordPress 实际 slug
