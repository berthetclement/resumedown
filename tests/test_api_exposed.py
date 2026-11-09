import resumedown


def test_public_api() -> None:
    # given
    expected = {"__version__", "init_resume", "render_resume", "render_pdf", "preview_resume", "stop_preview"}

    # then
    assert set(resumedown.__all__) == expected
    for name in expected:
        assert hasattr(resumedown, name), f"Make sure all functions ({name}) from '__ALL__' are well imported"
