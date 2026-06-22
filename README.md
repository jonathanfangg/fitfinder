# fitfinder

This starter kit contains everything you need to begin Project 2.

## What's Included

```
fitfinder
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

**macOS / Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):

```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:

```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:

```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Tool Inventory

### Tool 1: search_listings

**Inputs:**

- `description` (str): Keywords describing the item the user wants, e.g. "vintage graphic tee"
- `size` (str or None): Size string to filter by, e.g. "M" or "W30 L30". None skips size filtering.
- `max_price` (float or None): Maximum price in dollars, inclusive. None skips price filtering.

**Output:** A list of matching listing dicts sorted by relevance score. Each dict has: id, title, description, category, style_tags, size, condition, price, colors, brand, platform. Returns an empty list if nothing matches.

---

### Tool 2: suggest_outfit

**Inputs:**

- `new_item` (dict): The selected listing dict from search_listings
- `wardrobe` (dict): A wardrobe dict with an "items" key containing a list of wardrobe item dicts. Can be empty.

**Output:** A non-empty string with outfit suggestions. If the wardrobe is empty, returns general styling advice instead of named wardrobe pieces.

---

### Tool 3: create_fit_card

**Inputs:**

- `outfit` (str): The outfit suggestion string returned by suggest_outfit
- `new_item` (dict): The selected listing dict from search_listings

**Output:** A caption string mentioning the item name, price, and platform. Returns an error message string if outfit is empty or blank.

---

## Interaction Walkthrough

**User query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1 -- Tool called: search_listings**

- Input: `description="a vintage graphic tee"`, `size=None`, `max_price=30.0`
- Why this tool: the agent always starts here to find a matching listing before it can suggest anything
- Output: a list of listings under $30 matching "vintage graphic tee". The top result was Y2K Baby Tee (Butterfly Print), $18.00, depop

**Step 2 -- Tool called: suggest_outfit**

- Input: `new_item={"title": "Y2K Baby Tee — Butterfly Print", "price": 18.0, ...}`, `wardrobe=get_example_wardrobe()`
- Why this tool: a listing was found, so the agent now uses the wardrobe to build outfit ideas around it
- Output: two outfit suggestions using the baby tee: one paired with the baggy straight-leg jeans and chunky white sneakers from the wardrobe, one with wide-leg khaki trousers and black combat boots

**Step 3 -- Tool called: create_fit_card**

- Input: `outfit="Based on the Y2K Baby Tee..."`, `new_item={"title": "Y2K Baby Tee...", "price": 18.0, "platform": "depop", ...}`
- Why this tool: outfit suggestion was generated successfully, so the agent creates the final shareable caption
- Output: a 3-sentence caption mentioning the item name, $18.00 price, and depop, summarizing the Y2K-inspired look

**Final output to user:** the listing panel shows the item title, brand, size, condition, price, and platform. The outfit panel shows the two outfit suggestions from the LLM. The fit card panel shows the social caption.

---

## Error Handling and Fail Points

| Tool              | Failure mode                          | Agent response                                                                                                                                                                                                                                                   |
| ----------------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `search_listings` | No results match the query            | Set `session["error"]` to `"No matching listings found for that item, size, and budget. Try broadening the description, removing the size filter, or increasing the max price."` Return the session early without calling `suggest_outfit` or `create_fit_card`. |
| `suggest_outfit`  | Wardrobe is empty                     | Do not stop the agent. Generate general styling advice for the selected item instead of using named wardrobe pieces. Store that advice in `session["outfit_suggestion"]` and continue to `create_fit_card`.                                                      |
| `create_fit_card` | Outfit input is missing or incomplete | Set `session["error"]` to `"I found a listing, but could not create a fit card because the outfit suggestion was missing."` Return the session early instead of generating a fit card.                                                                           |

---

## Spec Reflection

**One way planning.md helped during implementation:**

Having the exact parameter names, types, and return values written out in each tool spec made it easier to review generated code before running it. I could check the spec and see that wardrobe was supposed to be a dict with an "items" key.

**One divergence from your spec, and why:**

The spec said to parse the query into description, size, and max_price but did not say how to do it. The original plan mentioned possibly using the LLM to parse. I used regex instead because the patterns are predictable.

---

## AI Usage

**Instance 1**

I gave Claude the Tool 1 spec from planning.md and it generated the filtering and keyword scoring logic. The one thing I changed was the failure path was returning an error message string instead of an empty list.

**Instance 2**

I gave Claude the Planning Loop section, the State Management section, the Error Handling table, and the Architecture diagram from planning.md. The first version used the pattern `r"\$?(\d+(?:\.\d+)?)"` to find the max price, which matched any number in the query. That meant "90s track jacket" parsed as max_price=90 and "black combat boots size 8" parsed as max_price=8 and size=8 at the same time. I replaced the parser and added a splitter to stop the description from including style notes like "I mostly wear baggy jeans." I used Claude to fix the error.

---

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
