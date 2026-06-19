from app.core.slug import slugify_name


def test_slugify_name_lowercases_and_hyphenates() -> None:
    assert slugify_name("Wireless Mouse") == "wireless-mouse"


def test_slugify_name_strips_special_chars() -> None:
    assert slugify_name("Hello, World!") == "hello-world"
