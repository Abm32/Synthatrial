# How to Remove Filename Footer from PDF

The filename at the bottom of PDF pages is added by the browser's print dialog. Here's how to remove it:

## Method 1: Use Automated Script (Recommended)

The export script automatically removes headers/footers:

```bash
python3 export_pdf.py
```

This creates `patent_drawings.pdf` **without** filename footers.

## Method 2: Manual Export - Disable Headers/Footers

If exporting manually via browser:

1. Open `drawings.html` in Chrome
2. Press `Ctrl+P` (or `Cmd+P` on Mac)
3. In the print dialog:
   - Click **"More settings"** (expand the settings)
   - **UNCHECK** the box labeled **"Headers and footers"**
   - This removes the filename/URL from the bottom of pages
4. Set other settings:
   - Margins: None
   - Background graphics: ON
   - Scale: 100%
5. Click "Save" or "Print"

## Visual Guide (Chrome Print Dialog)

```
┌─────────────────────────────────┐
│ Print                            │
├─────────────────────────────────┤
│ Destination: Save as PDF         │
│                                  │
│ ▼ More settings                  │
│   ☐ Headers and footers  ← UNCHECK THIS!
│   ☑ Background graphics          │
│                                  │
│ Margins: None                    │
│ Scale: 100%                      │
└─────────────────────────────────┘
```

## Why This Happens

Browsers add headers/footers by default when printing to PDF. This includes:
- **Header:** Page title or URL
- **Footer:** Filename or URL

For patent drawings, these must be removed as they're not part of the actual drawing.

## Verification

After export, open the PDF and check:
- ✅ No text at the top of pages
- ✅ No filename/URL at the bottom of pages
- ✅ Only the figure content is visible

---

**Quick Fix:** If you already have a PDF with footers, use the automated script to regenerate it without footers.
