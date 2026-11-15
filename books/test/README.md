# Test ebook: Hanoi & Hạ Long Bay in 3 Days (#8)

A **test**, not for sale: nothing here is published or submitted to KDP. It exists so the 88eggs book tasks are
designed from a real book.

- `src/chapters/*.md`: the chapters, written by the 88eggs Text Generator task (Claude Sonnet 5.5) from the fact
  pack only. They keep their `[F#]` fact citations, and `build.py` strips them for readers.
- `src/facts-prompt.md`, `src/system-prompt.md`: the exact fact pack and system prompt given to the model.
- `src/runs.txt`: the 88eggs task runs, assets, credits and $ for each chapter.
- `src/sources.md`: the reader-facing sources page. The full source URLs are on #8.
- `images/`: cover + 3 section images (88eggs Image Generator). **Placeholders until the real files are added.**
- `build.py`: the prototype builder (the base of the `book-builder-task`).

## Build

```sh
brew install pandoc epubcheck weasyprint poppler
brew install --cask font-noto-serif font-noto-sans   # SIL OFL fonts, not copied into the repo
cd books/test && python3 build.py                    # writes out/ and out/report.txt
```

Outputs:
- `out/book.epub`: EPUB 3 (pandoc), checked with EPUBCheck.
- `out/interior.pdf`: 6×9 in, KDP margins, fonts embedded (WeasyPrint).
- `out/cover.pdf`: wrap cover, with the spine sized for the page count and paper (KDP: white 0.002252 in/page) and 0.125 in bleed.

`books/` is excluded from the Pages build (`_config.yml`), so none of it is served on thetripnow.com.
