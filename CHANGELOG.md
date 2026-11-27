# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]
### Added
- The starter resume has a photo slot at the top of the sidebar, with a placeholder
  `photo.svg` in `resumedown_files/` (#31).
- Python 3.14 support, tested on Linux, Windows and macOS (#27).
  - Python 3.15 is not supported yet: [PyYAML](https://pypi.org/project/PyYAML/) has no wheels for it (#28).

### Fixed
- A long skills list no longer pushes the main column to page 2: new resumes
  write `#contact` and `#skills` before `#main`, with a compact skills list.
  A sidebar taller than page 1 is still a known limit (#31).
- Dates such as "Sept. 2021" no longer overflow their column: the
  default `--date-width` is now 18mm (#23).


## [0.1.0] - 2026-11-11
### Added
- `init_resume(path)` creates a resume folder with a starter `.md` and its
  assets (layout `resume.css`, an editable `theme.css`, paged.js).
- `render_resume(md_path)` renders the Markdown to HTML next to the `.md`.
- `preview_resume(md_path)` serves the page locally and opens it in the
  browser for an edit / render / refresh loop; `stop_preview()` stops it.
- `render_pdf(md_path)` produces a paginated PDF through Playwright and
  Chromium.
- Optional YAML frontmatter: `css` adds your own stylesheets after the layout.
