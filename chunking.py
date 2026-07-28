from . import config

def build_chunks(items: list[dict], single_chunk: bool = False) -> list[dict]:
    chunks = []
    current = {"title": "Untitled", "description": "", "elements": {}, "tables": [], "images": []}
    pending_key = None
    seen_title = False

    for item in items:
        item_type = item["type"]

        if item_type == "text":
            content = item["content"].strip()
            label = item["label"]
            if not content:
                continue

            level = item.get("level")
            is_heading = label in config.HEADING_LABELS or (
                label == "text"
                and level == 1
                and len(content) < config.NUMBERED_HEADING_MAX_LEN
                and config.NUMBERED_HEADING_PATTERN.match(content)
            )
            if is_heading and not single_chunk:
                if current["title"] != "Untitled" or current["description"] or current["elements"] or current["tables"] or current["images"]:
                    chunks.append(current)
                current = {"title": content, "description": "", "elements": {}, "tables": [], "images": []}
                pending_key = None
                continue

            if is_heading and single_chunk and not seen_title:
                current["title"] = content
                seen_title = True
                continue

            if item.get("from_image"):
                print(item)
                current["images"].append(f"text in image: {content}")
                continue

            if pending_key is not None:
                current["elements"][pending_key] = content
                pending_key = None
                continue

            if label == "list_item" and ":" in content:
                key, _, value = content.partition(":")
                current["elements"][key.strip()] = value.strip()
            elif content.endswith(":") and len(content) < 80:
                pending_key = content[:-1].strip()
            else:
                current["description"] = (current["description"] + "\n" + content).strip()

        elif item_type == "table":
            current["tables"].append({"data": item["data"], "markdown": item["markdown"]})

        elif item_type == "picture":
            if item["caption"]:
                current["images"].append(item["caption"])

    if current["title"] != "Untitled" or current["description"] or current["elements"] or current["tables"] or current["images"]:
        chunks.append(current)

    return chunks

