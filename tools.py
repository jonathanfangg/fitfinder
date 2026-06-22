"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


def _get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set. Add it to a .env file in the project root.")
    return Groq(api_key=api_key)


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    listings = load_listings()

    filtered = []
    for item in listings:
        if max_price is not None and item["price"] > max_price:
            continue
        if size is not None and size.lower() not in item["size"].lower():
            continue
        filtered.append(item)

    keywords = [w.lower() for w in description.split()]

    def score(item):
        searchable = " ".join([
            item.get("title", ""),
            item.get("description", ""),
            item.get("category", ""),
            item.get("brand", "") or "",
            " ".join(item.get("style_tags", [])),
            " ".join(item.get("colors", [])),
        ]).lower()
        return sum(1 for kw in keywords if kw in searchable)

    scored = [(score(item), item) for item in filtered]
    scored = [(s, item) for s, item in scored if s > 0]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored]


def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    client = _get_groq_client()

    item_summary = (
        f"{new_item.get('title', 'item')} — {new_item.get('category', '')}, "
        f"{', '.join(new_item.get('colors', []))}, "
        f"style: {', '.join(new_item.get('style_tags', []))}"
    )

    wardrobe_items = wardrobe.get("items", [])

    if not wardrobe_items:
        prompt = (
            f"A shopper just found this thrifted item: {item_summary}. "
            "They don't have a saved wardrobe yet. Give them 1-2 outfit ideas using this item, "
            "suggesting general wardrobe pieces that would complement it well. "
            "Be specific about silhouettes, colors, and vibe."
        )
    else:
        wardrobe_text = "\n".join(
            f"- {w.get('name', '')} ({w.get('category', '')}, {', '.join(w.get('colors', []))})"
            for w in wardrobe_items
        )
        prompt = (
            f"A shopper is considering buying: {item_summary}.\n\n"
            f"Their current wardrobe includes:\n{wardrobe_text}\n\n"
            "Suggest 1-2 complete outfits using the new item combined with specific pieces "
            "from their wardrobe. Name the wardrobe pieces you're pairing it with and explain the vibe."
        )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    result = (response.choices[0].message.content or "").strip()
    if not result:
        return (
            "I could not generate a personalized outfit from the wardrobe, but this item would "
            "pair well with simple basics, balanced proportions, and shoes that match its style tags."
        )
    return result


def create_fit_card(outfit: str, new_item: dict) -> str:
    if not outfit or not outfit.strip():
        return "Could not create a fit card because no outfit suggestion was provided."

    client = _get_groq_client()

    title = new_item.get("title", "this thrifted find")
    price = new_item.get("price", "")
    platform = new_item.get("platform", "")
    colors = ", ".join(new_item.get("colors", []))
    tags = ", ".join(new_item.get("style_tags", []))

    prompt = (
        f"Write a 2-4 sentence Instagram or TikTok caption for this thrift find.\n\n"
        f"Item: {title}\n"
        f"Price: ${price}\n"
        f"Found on: {platform}\n"
        f"Colors: {colors}\n"
        f"Vibe: {tags}\n\n"
        f"Outfit idea: {outfit}\n\n"
        "The caption should sound like a real person posting their OOTD — casual, specific, and fun. "
        "Mention the item name, price, and platform once each. No hashtags."
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.2,
    )

    result = (response.choices[0].message.content or "").strip()
    if not result:
        return "Could not generate a fit card caption."
    return result
