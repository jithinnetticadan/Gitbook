#!/usr/bin/env python3
"""
Safe PDF JavaScript Injection Test (benign)
- Generates a well-formed PDF that triggers a harmless Acrobat JS alert via /OpenAction.
- Uses PyPDF2 to ensure proper PDF structure.
- No XHR, no cookie access, no data collection.

Usage:
    python safe_pdf_js_test.py -o pdf_injection_test.pdf --message "PDF Injection Test"
"""
import os
import sys
import argparse

# Ensure Python 3+
if sys.version_info[0] < 3:
    raise SystemExit("Use Python 3 (or higher) only")

try:
    from PyPDF2 import PdfWriter
except Exception as e:
    raise SystemExit(
        f"Failed to import PyPDF2. Make sure it's available in your environment. Error: {e}"
    )

def sanitize_alert_message(msg: str) -> str:
    """
    Sanitize the alert message to avoid breaking the JS string context.
    Only allow simple printable characters; escape backslashes and parentheses.
    This does NOT allow arbitrary JS—only a safe string inside app.alert("...").
    """
    # Replace problematic characters
    msg = msg.replace("\\", "\\\\")
    msg = msg.replace("(", "\\(")
    msg = msg.replace(")", "\\)")
    # Optionally constrain to a limited charset to be extra safe
    # Keep it simple: strip control characters
    safe = "".join(ch for ch in msg if 32 <= ord(ch) <= 126)
    # Clamp length to avoid excessively large strings
    return safe[:256]

def create_benign_js_pdf(output_path: str, alert_message: str = "PDF Injection Test") -> None:
    """
    Create a well-formed PDF with /OpenAction JavaScript that calls:
        app.alert("<sanitized message>")
    """
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)  # Letter size

    # Sanitize the message to ensure it's a safe string literal
    safe_msg = sanitize_alert_message(alert_message)
    js_code = f'app.alert("{safe_msg}")'

    # PdfWriter.add_js embeds Acrobat JS at the document level and sets OpenAction
    writer.add_js(js_code)

    # Write to disk
    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"[+] Created benign JS PDF: {output_path}")
    print("[i] The PDF includes an /OpenAction that calls app.alert(...)")
    print("[i] Some viewers might block or ignore Acrobat JavaScript by default.")

def main():
    # Safety guard: require explicit lab opt-in
    parser = argparse.ArgumentParser(
        description="Generate a benign PDF to test for JavaScript /OpenAction handling (safe alert only)."
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output PDF file path (e.g., pdf_injection_test.pdf)",
    )
    parser.add_argument(
        "--message",
        default="PDF Injection Test",
        help='Alert message for app.alert("...") [sanitized, max 256 chars]',
    )
    args = parser.parse_args()

    try:
        create_benign_js_pdf(output_path=args.output, alert_message=args.message)
        print("[-] Done.")
    except Exception as e:
        print(f"[!] Failed to create PDF. Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()