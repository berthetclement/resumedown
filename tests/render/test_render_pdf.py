import re
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from resumedown.conventions import ASSETS_FOLDER_NAME
from resumedown.render import renderer_pdf
from resumedown.render.renderer_pdf import _html_to_pdf, render_pdf
from resumedown.template.markdown_writer import init_resume


# no need ["pdf"] extra lib installed
def test_render_pdf_raise_md_not_found(tmp_path: Path) -> None:
    # given
    md_path = tmp_path / "nothing.md"

    # then
    with pytest.raises(FileNotFoundError, match=re.escape(f"{md_path} does not exist or is not a file")):
        render_pdf(md_path)


def test_render_pdf_import_lib_not_found(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # given
    monkeypatch.setitem(sys.modules, "playwright", None)

    # then
    with pytest.raises(ImportError, match=re.escape("render_pdf needs the [pdf] extra: pip install resumedown[pdf]")):
        render_pdf(tmp_path / "nothing.md")


def test_render_pdf_with_no_asset_folder(tmp_path: Path) -> None:
    # given
    md_file = tmp_path / "empty.md"
    md_file.write_text("empty")

    # then
    with pytest.raises(
        NotADirectoryError,
        match=re.escape(f"{md_file.parent / ASSETS_FOLDER_NAME} not found: run init_resume() first"),
    ):
        render_pdf(md_file)


# test html to pdf processing
@pytest.mark.pdf
def test_html_pdf_without_js(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # given
    monkeypatch.setattr(renderer_pdf, "_PAGED_TIMEOUT_MS", 500)

    # 'throw' raise an error for javascript with type 'Error'
    html_content_test = "<script>throw new Error('test')</script>"
    html_path = tmp_path / "error.html"

    html_path.write_text(html_content_test, encoding="utf-8")

    # then
    with pytest.raises(RuntimeError, match=re.escape("Java Script report 'pageerror': test")):
        _html_to_pdf(html_path)


@pytest.mark.pdf
@pytest.mark.parametrize("as_input", [str, Path])
def test_render_pdf_produce_complete_pdf(tmp_path: Path, as_input: Callable[[Path], str | Path]) -> None:
    # given
    test_path = tmp_path / "test_render_pdf"
    md_path = init_resume(path=test_path)

    # then
    output_pdf_path = render_pdf(as_input(md_path))
    assert output_pdf_path == md_path.with_suffix(".pdf")
    assert output_pdf_path.read_bytes().startswith(b"%PDF")


@pytest.mark.pdf
def test_sidebar_starts_level_with_main_on_page_one(tmp_path: Path) -> None:
    """The sidebar sits at the top of page 1, not pushed below the header (#31)."""
    from playwright.sync_api import sync_playwright

    from resumedown.render.renderer import render_resume
    from resumedown.render.server import local_server

    # given
    md_path = init_resume(path=tmp_path / "sidebar")
    html_path = render_resume(md_path)

    with local_server(html_path.parent) as base_url, sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.add_init_script("window.PagedConfig = { after: () => { window.__pagedDone = true } }")
            page.goto(f"{base_url}/{html_path.name}")
            page.wait_for_function("window.__pagedDone === true")

            # then — a blank page cannot pass: pagination ran
            assert page.eval_on_selector_all(".pagedjs_page", "e => e.length") > 0

            contact_top = page.locator('[data-id="contact"]').first.bounding_box()
            main_top = page.locator('[data-id="main"]').first.bounding_box()
            assert contact_top is not None
            assert main_top is not None

            # same top, within 1 px: the sidebar is at the top of the page
            assert abs(contact_top["y"] - main_top["y"]) < 1
        finally:
            browser.close()
