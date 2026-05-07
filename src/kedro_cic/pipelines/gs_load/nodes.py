import json
from urllib.parse import parse_qs, urlparse
import re

import pandas as pd
from bs4 import BeautifulSoup


def parse_user_id(profile_url: str | None) -> str | None:
    if not profile_url:
        return None
    query = parse_qs(urlparse(profile_url).query)
    users = query.get("user")
    return users[0] if users else None


def parse_cited_by(raw_text: str | None) -> int | None:
    if not raw_text:
        return None
    match = re.search(r"(\d[\d.,]*)", raw_text)
    if not match:
        return None
    digits = re.sub(r"[^\d]", "", match.group(1))
    return int(digits) if digits else None


def extract_author_cards(source_file: str, html_text: str) -> list[dict]:
    soup = BeautifulSoup(html_text, "html.parser")
    rows = []

    for card in soup.select("div.gsc_1usr"):
        name_node = card.select_one("h3.gs_ai_name a")
        affiliation_node = card.select_one("div.gs_ai_aff")
        email_node = card.select_one("div.gs_ai_eml")
        cited_by_node = card.select_one("div.gs_ai_cby")
        interest_nodes = card.select("a.gs_ai_one_int")

        profile_url = name_node.get("href") if name_node else None

        rows.append(
            {
                "source_file": source_file,
                "source_system": "google_scholar",
                "entity_type": "author",
                "name": name_node.get_text(" ", strip=True) if name_node else None,
                "profile_url": profile_url,
                "user": parse_user_id(profile_url),
                "affiliation": (
                    affiliation_node.get_text(" ", strip=True)
                    if affiliation_node
                    else None
                ),
                "verified_email": (
                    email_node.get_text(" ", strip=True) if email_node else None
                ),
                "cited_by": parse_cited_by(
                    cited_by_node.get_text(" ", strip=True) if cited_by_node else None
                ),
                "interests": [
                    node.get_text(" ", strip=True) for node in interest_nodes
                ],
            }
        )

    return rows


def gs_parse_author(html_partitions: dict) -> pd.DataFrame:
    rows = []
    for partition_id, partition_value in sorted(html_partitions.items()):
        html_text = partition_value() if callable(partition_value) else partition_value
        rows.extend(extract_author_cards(f"{partition_id}.html", html_text))

    return pd.DataFrame(rows).convert_dtypes()


def gs_load_author(df_author_raw: pd.DataFrame) -> pd.DataFrame:
    df_author = (
        df_author_raw.sort_values(["user", "source_file"], na_position="last")
        .drop_duplicates(subset=["user"], keep="first")
        .reset_index(drop=True)
        .copy()
    )

    df_author["interests"] = df_author["interests"].apply(
        lambda values: json.dumps(list(values), ensure_ascii=False)
        if hasattr(values, "__iter__") and not isinstance(values, str)
        else values
    )
    df_author["_load_datetime"] = pd.Timestamp.now().floor("s")

    return df_author.convert_dtypes()
