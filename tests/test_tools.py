from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe


def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []


def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)


def test_search_size_filter():
    results = search_listings("shirt", size="XL", max_price=None)
    assert all("xl" in item["size"].lower() for item in results)


def test_search_returns_list_on_no_match():
    results = search_listings("xyznonexistentitem12345", size=None, max_price=None)
    assert isinstance(results, list)
    assert results == []


def test_suggest_outfit_with_wardrobe():
    wardrobe = get_example_wardrobe()
    item = search_listings("vintage tee", size=None, max_price=50)
    if item:
        result = suggest_outfit(item[0], wardrobe)
        assert isinstance(result, str)
        assert len(result) > 0


def test_suggest_outfit_empty_wardrobe():
    wardrobe = get_empty_wardrobe()
    item = search_listings("jacket", size=None, max_price=100)
    if item:
        result = suggest_outfit(item[0], wardrobe)
        assert isinstance(result, str)
        assert len(result) > 0


def test_create_fit_card_returns_string():
    item = search_listings("vintage tee", size=None, max_price=50)
    if item:
        wardrobe = get_example_wardrobe()
        outfit = suggest_outfit(item[0], wardrobe)
        card = create_fit_card(outfit, item[0])
        assert isinstance(card, str)
        assert len(card) > 0


def test_create_fit_card_empty_outfit():
    item = search_listings("vintage tee", size=None, max_price=50)
    new_item = item[0] if item else {}
    result = create_fit_card("", new_item)
    assert isinstance(result, str)
    assert "no outfit" in result.lower() or "could not" in result.lower()


def test_create_fit_card_whitespace_outfit():
    item = search_listings("vintage tee", size=None, max_price=50)
    new_item = item[0] if item else {}
    result = create_fit_card("   ", new_item)
    assert isinstance(result, str)
    assert len(result) > 0
