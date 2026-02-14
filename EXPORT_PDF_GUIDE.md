# Exporting Patent Drawings to PDF

This guide explains how to export `drawings.html` to a high-quality PDF suitable for patent submission.

## Method 1: Automated Script (Recommended)

Run the export script:

```bash
python3 export_pdf.py
```

This will create `patent_drawings.pdf` in the same directory.

**Note:** The script requires Chrome/Chromium to be installed. If it fails, use Method 2.

## Method 2: Manual Browser Export (Most Reliable)

This method gives you full control and is recommended for patent submissions.

### Steps:

1. **Open the HTML file in Chrome/Chromium:**
   ```bash
   google-chrome drawings.html
   # OR
   chromium drawings.html
   ```

2. **Wait for diagrams to render** (Mermaid diagrams need a few seconds to load)

3. **Open Print Dialog:**
   - Press `Ctrl+P` (Linux/Windows) or `Cmd+P` (Mac)
   - Or: Menu → Print

4. **Configure Print Settings:**
   - **Destination:** Select "Save as PDF"
   - **Layout:** Portrait
   - **Paper size:** A4 or Letter (check patent office requirements)
   - **Margins:** None (important for patent drawings)
   - **Scale:** 100%
   - **Background graphics:** ✅ Enable (ON)
   - **Headers and footers:** ❌ **MUST BE DISABLED (OFF)** - This removes filename/URL from bottom of pages

   **IMPORTANT:** In Chrome's print dialog, click "More settings" and ensure "Headers and footers" is **UNCHECKED**. This is critical for patent submissions.

5. **Preview:**
   - Check that both figures are visible
   - Verify text is readable
   - Ensure diagrams are not cut off

6. **Save:**
   - Click "Save" or "Print"
   - Choose filename: `patent_drawings.pdf`
   - Save location: Project directory

### Quality Checklist:

- [ ] Both Figure 1 and Figure 2 are on separate pages
- [ ] All text is readable (not blurry)
- [ ] Diagrams render completely (no cut-off)
- [ ] No headers/footers visible
- [ ] Margins are minimal/zero
- [ ] Background graphics are visible
- [ ] File size is reasonable (< 5 MB typically)

## Method 3: Using Playwright (Alternative)

If you have Playwright installed:

```bash
pip install playwright
playwright install chromium
python3 -c "
from playwright.sync_api import sync_playwright
import os

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f'file://{os.path.abspath(\"drawings.html\")}')
    page.wait_for_timeout(3000)  # Wait for Mermaid
    page.pdf(path='patent_drawings.pdf', format='A4', print_background=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
    browser.close()
"
```

## Patent Office Requirements

Most patent offices require:

- **Format:** PDF
- **Page size:** A4 or Letter
- **Margins:** Minimal (0.5-1 inch typically acceptable)
- **Resolution:** High quality (300 DPI recommended)
- **Figures:** Each figure on separate page (already configured)
- **Text:** Clear and readable

## Troubleshooting

### Diagrams not rendering:
- Wait 5-10 seconds after opening the HTML file
- Check browser console for errors (F12)
- Ensure internet connection (Mermaid loads from CDN)

### PDF quality issues:
- Use Chrome/Chromium (best Mermaid support)
- Enable "Background graphics" in print settings
- Set scale to 100% (not "Fit to page")
- Use "Save as PDF" not "Print to PDF" if available

### File too large:
- Reduce image quality (if any embedded images)
- Check if Mermaid is rendering correctly (should be vector graphics)

## Verification

After export, verify the PDF:

1. Open `patent_drawings.pdf` in a PDF viewer
2. Check page count (should be 2 pages: one per figure)
3. Zoom in to verify text clarity
4. Print a test page to verify print quality

---

**For patent submission:** Ensure the PDF meets your patent office's specific requirements for drawings (format, size, margins, etc.).
