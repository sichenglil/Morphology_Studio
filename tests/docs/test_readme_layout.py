from scripts.validation.check_readme_format import check


def test_bilingual_readme_layout_and_modules():
    assert check() == []
