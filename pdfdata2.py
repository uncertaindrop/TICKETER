# mini_invoice_fields_pdfminer.py (updated for new format)
# Outputs: name, surname, phone, invoice, "cst code", material, product, serial

import sys, re, json
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLine

# ---------- helpers ----------
NAME_TOKEN = r"[A-Za-zΑ-Ωα-ωΪΫϊϋΐΰάέήίόύώΆΈΉΊΌΎΏ\.-]+"
NAME_LINE_RE = re.compile(rf"^{NAME_TOKEN}(?:\s+{NAME_TOKEN})+$")
SKU_RE   = re.compile(r"^\d{6,8}$")
MONEY_RE = re.compile(r"-?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})")
SERIAL_RE = re.compile(r"(\d{14,20})")
PHONE8_RE = re.compile(r"(?<!\d)([29]\d{7})(?!\d)")

# Updated invoice regex to handle both formats
INVOICE_OLD_RE = re.compile(r"Αρ\. παραστατικού:\s*([0-9]+ΑΠΔΑ[0-9]+)")
INVOICE_NEW_RE = re.compile(r"^(\d{6}ΑΠΔΑ\d{6})$")

# CST code regex
CST_RE = re.compile(r"[^\s··•]{5,}")

END_TABLE_RE = re.compile(r"(Συνολο|Σχόλια|Πληρωτέο|Καθ\.|Αξιες\s*ΦΠΑ|ΣΚΟΠΟΣ\s+ΔΙΑΚΙΝΗΣΗΣ)", re.IGNORECASE)

# Glyphs that must NEVER be considered a CST code
BAD_GLYPHS = {"·", "•", "·", "․", "‧"}


def is_bad_cst(s: str) -> bool:
    """Reject dot-like junk sequences that pdfminer generates."""
    if not s:
        return True
    if s.strip() in BAD_GLYPHS:
        return True
    if len(s.strip()) < 5:
        return True
    # all chars are punctuation / dots?
    if all(ch in BAD_GLYPHS for ch in s.strip()):
        return True
    return False


def get_lines(pdf_path):
    lines = []
    for page in extract_pages(pdf_path):
        for el in page:
            if isinstance(el, LTTextContainer):
                for tl in el:
                    if isinstance(tl, LTTextLine):
                        s = tl.get_text().strip()
                        if s:
                            lines.append(s)
    return lines


def parse_money(s: str):
    s = s.strip().replace(" ", "")
    if "," in s and "." in s:
        if s.find(".") < s.find(","): s = s.replace(".", "")
        else: s = s.replace(",", "")
    s = s.replace(",", ".")
    m = re.search(r"-?\d+(?:\.\d{2})", s)
    return float(m.group(0)) if m else None


def looks_like_name(s: str) -> bool:
    if ":" in s or "Στοιχεία" in s: return False
    if any(ch.isdigit() for ch in s): return False
    return NAME_LINE_RE.match(s) is not None and len(s) <= 60


def parse_items(lines, phone_to_exclude=""):
    """Parse items from invoice, excluding known phone numbers from SKU detection"""
    items = []
    i = 0
    
    # First, try to find items using the table structure
    while i < len(lines):
        s = lines[i].strip()
        # Don't treat phone numbers as SKUs
        if SKU_RE.match(s) and s != phone_to_exclude:
            sku = s
            block = []
            j = i + 1
            while j < len(lines) and not SKU_RE.match(lines[j].strip()):
                if END_TABLE_RE.search(lines[j]): break
                block.append(lines[j].strip())
                j += 1

            # description
            desc = ""
            for g in block:
                if re.search(r"[A-Za-zΑ-Ωα-ω]", g) and not g.startswith("Σειριακός") and not MONEY_RE.fullmatch(g):
                    # Skip if it's a table header or label
                    if g not in ["Ώρα", "Μ.Μ.", "Περιγραφή", "Ποσότητα", "Τιμή Μονάδος"]:
                        desc = g
                        break

            # money
            amounts = []
            for g in block:
                for m in MONEY_RE.findall(g):
                    t = m.replace(".", "").replace(",", ".")
                    try: amounts.append(float(t))
                    except: pass
            gross = max(amounts) if amounts else None

            # serial
            serial = ""
            for g in block:
                m = SERIAL_RE.search(g.replace(" ", ""))
                if m: serial = m.group(1); break

            items.append({"sku": sku, "desc": desc, "gross": gross, "serial": serial})
            i = j
        else:
            i += 1
    
    # If no items found using table structure, try alternative method for new format
    # Look for "Κωδικός Είδους" followed by SKU and product description
    if not items:
        for i, line in enumerate(lines):
            if "Κωδικός Είδους" in line:
                # SKU should be in the next few lines
                for j in range(i + 1, min(i + 5, len(lines))):
                    candidate_sku = lines[j].strip()
                    if SKU_RE.match(candidate_sku) and candidate_sku != phone_to_exclude:
                        sku = candidate_sku
                        # Product description should be right after SKU
                        desc = ""
                        if j + 1 < len(lines):
                            potential_desc = lines[j + 1].strip()
                            if "APPLE" in potential_desc or "IPHONE" in potential_desc or re.search(r"[A-Za-z]{3,}", potential_desc):
                                desc = potential_desc
                        
                        # Try to find price
                        gross = None
                        for k in range(j, min(j + 30, len(lines))):
                            amounts = []
                            for m in MONEY_RE.findall(lines[k]):
                                t = m.replace(".", "").replace(",", ".")
                                try: amounts.append(float(t))
                                except: pass
                            if amounts:
                                gross = max(amounts)
                                break
                        
                        items.append({"sku": sku, "desc": desc, "gross": gross, "serial": ""})
                        break
                break
    
    return items


# CST PATTERNS
CST_SHORT_RE = re.compile(r"^[A-Za-zΑ-Ωα-ω]{1,2}\d$")          # P2, A7, Δ5
CST_10DIGIT_RE = re.compile(r"^\d{10}$")                       # 10 digits
CST_CB_RE = re.compile(r"^C[ΒB]\d{8}$")                        # CΒ + 8 digits

DATE_RE = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")     # reject dates


def is_valid_cst(candidate: str) -> bool:
    candidate = candidate.strip()

    # Reject obvious junk
    if not candidate or len(candidate) > 12:
        return False
    if "/" in candidate or "-" in candidate:  # dates
        return False
    if DATE_RE.fullmatch(candidate):
        return False

    # Valid formats:
    if CST_SHORT_RE.fullmatch(candidate):   # P2
        return True
    if CST_10DIGIT_RE.fullmatch(candidate): # 10 digits
        return True
    if CST_CB_RE.fullmatch(candidate):      # CΒ12345678
        return True

    return False


def extract_cst(lines, full):
    # Search line-by-line for valid CST candidates
    for ln in lines:
        parts = ln.split()
        for token in parts:
            if is_valid_cst(token):
                return token

    # fallback: full text token scan
    for token in re.split(r"\s+", full):
        if is_valid_cst(token):
            return token

    return ""


def extract_invoice(lines, full):
    """Extract invoice number - handles both old and new formats"""
    # Try old format first (with prefix text)
    m = INVOICE_OLD_RE.search(full)
    if m:
        return m.group(1)
    
    # Try new format (standalone line)
    for line in lines:
        m = INVOICE_NEW_RE.match(line.strip())
        if m:
            return m.group(1)
    
    return ""


def extract_serial(lines, full):
    """Extract serial number - handles both inline and separate line formats"""
    # Pattern 1: "Σειριακός Αριθμός 358107269349057" (OLD format)
    # Pattern 2: "Σειριακός αριθμός: 357488875984664" (NEW format)
    for line in lines:
        if "Σειριακός" in line or "σειριακός" in line.lower():
            m = SERIAL_RE.search(line.replace(" ", ""))
            if m:
                return m.group(1)
    
    return ""


def extract_name_phone_new_format(lines):
    """Extract name and phone from new format"""
    name, surname, phone = "", "", ""
    
    # Look for ΕΠΩΝΥΜΙΑ: label (customer name in new format)
    # In new format, the name appears a few lines BEFORE the "ΕΠΩΝΥΜΙΑ:" label
    for i, line in enumerate(lines):
        if "ΕΠΩΝΥΜΙΑ:" in line:
            # Look backwards for name (check 2-5 lines before)
            for j in range(max(0, i - 5), i):
                if looks_like_name(lines[j]):
                    name_line = lines[j]
                    parts = name_line.split()
                    if len(parts) >= 2:
                        surname = " ".join(parts[:-1])
                        name = parts[-1]
                    elif len(parts) == 1:
                        name = parts[0]
                    break
            if name:  # Found name, stop searching
                break
    
    # Look for phone - scan entire document for 8-digit phone pattern
    for line in lines:
        m = PHONE8_RE.search(line.replace(" ", ""))
        if m:
            phone = m.group(1)
            break
    
    return name, surname, phone


def extract_name_phone_old_format(lines):
    """Extract name and phone from old format"""
    name, surname, phone = "", "", ""
    
    # Find "Στοιχεία Πελάτη" anchor
    anchor = next((i for i, s in enumerate(lines) if "Στοιχεία Πελάτη" in s), None)
    
    if anchor is not None:
        # Look for name line
        for i in range(anchor + 1, min(len(lines), anchor + 12)):
            if looks_like_name(lines[i]):
                name_line = lines[i]
                parts = name_line.split()
                if len(parts) >= 2:
                    surname = " ".join(parts[:-1])
                    name = parts[-1]
                elif len(parts) == 1:
                    name = parts[0]
                break
        
        # Look for phone
        for i in range(anchor, min(len(lines), anchor + 15)):
            if "Τηλέφωνο:" in lines[i]:
                m = PHONE8_RE.search(lines[i].replace(" ", ""))
                if m:
                    phone = m.group(1)
                    break
    
    return name, surname, phone


def extract(pdf_path: str):
    lines = get_lines(pdf_path)
    full = "\n".join(lines)

    # Detect format by checking for old format markers
    is_old_format = any("Στοιχεία Πελάτη" in line for line in lines)
    
    # Extract invoice number
    invoice = extract_invoice(lines, full)
    
    # Extract CST code
    cst = extract_cst(lines, full)
    
    # Extract name and phone based on format (do this FIRST to get phone)
    if is_old_format:
        name, surname, phone = extract_name_phone_old_format(lines)
    else:
        name, surname, phone = extract_name_phone_new_format(lines)
    
    # Fallback: try to find name anywhere if still empty
    if not name:
        name_line = next((s for s in lines if looks_like_name(s)), "")
        if name_line:
            parts = name_line.split()
            if len(parts) >= 2:
                surname = " ".join(parts[:-1])
                name = parts[-1]
            elif len(parts) == 1:
                name = parts[0]
    
    # Fallback: try to find phone anywhere if still empty
    if not phone:
        for line in lines:
            m = PHONE8_RE.search(line.replace(" ", ""))
            if m:
                phone = m.group(1)
                break

    # Extract items → pick highest gross price (pass phone to avoid confusion)
    items = parse_items(lines, phone_to_exclude=phone)
    material = product = ""
    if items:
        best = max(items, key=lambda x: (x["gross"] or 0))
        material, product = best["sku"], best["desc"]
    
    # Extract serial number
    serial = extract_serial(lines, full)

    return {
        "name": name,
        "surname": surname,
        "phone": phone,
        "invoice": invoice,
        "cst code": cst,
        "material": material,
        "product": product,
        "serial": serial
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mini_invoice_fields_pdfminer.py /path/to/invoice.pdf")
        sys.exit(1)
    out = extract(sys.argv[1])
    print(json.dumps(out, ensure_ascii=False, indent=2))
