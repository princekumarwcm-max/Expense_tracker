# utils/ocr_utils.py
import streamlit as st
import pytesseract
from PIL import Image
import re
import pandas as pd
import os
from datetime import datetime
import platform


# ============================================================
# CATEGORY AUTO-DETECTION FROM RECEIPT TEXT
# ============================================================
DEBIT_CATEGORY_KEYWORDS = {
    "Today's expense ": [
        'cafe', 'coffee', 'tea', 'snack', 'juice', 'chai', 'bakery',
        'daily', 'canteen', 'lunch', 'dinner', 'breakfast', 'meal',
        'swiggy', 'zomato', 'blinkit', 'zepto', 'instamart'
    ],
    "Weekend expense": [
        'bar', 'pub', 'club', 'lounge', 'weekend', 'party', 'movie',
        'pvr', 'inox', 'bookmyshow', 'bowling', 'arcade', 'amusement'
    ],
    "Shopping": [
        'amazon', 'flipkart', 'myntra', 'ajio', 'meesho', 'nykaa',
        'shopping', 'mall', 'store', 'mart', 'retail', 'cloth', 'fashion',
        'shoes', 'apparel', 'garment', 'boutique'
    ],
    "Petrol": [
        'petrol', 'diesel', 'fuel', 'hp pump', 'ioc', 'bpcl', 'hpcl',
        'indian oil', 'bharat petroleum', 'reliance petro', 'filling station'
    ],
    "Self Care": [
        'gym', 'fitness', 'salon', 'spa', 'haircut', 'parlour', 'parlor',
        'doctor', 'hospital', 'clinic', 'pharmacy', 'medicine', 'chemist',
        'health', 'wellness', 'medical'
    ],
    "Recharge": [
        'recharge', 'jio', 'airtel', 'vi ', 'vodafone', 'bsnl', 'dth',
        'broadband', 'internet', 'wifi', 'tata sky', 'dish tv', 'sun direct'
    ],
    "Veggies,Gas cylinder and Dmart": [
        'vegetable', 'veggies', 'sabzi', 'grocer', 'grocery', 'dmart',
        'big bazaar', 'reliance fresh', 'more supermarket', 'gas', 'cylinder',
        'lpg', 'indane', 'hp gas', 'bharat gas', 'fruits', 'supermarket'
    ],
    "Rent,Maid & Electricity bills": [
        'rent', 'electricity', 'mseb', 'bijli', 'maid', 'bai', 'house',
        'maintenance', 'society', 'water bill', 'property tax', 'flat',
        'housing', 'accommodation', 'pg '
    ],
    "Trips": [
        'hotel', 'resort', 'oyo', 'makemytrip', 'goibibo', 'cleartrip',
        'yatra', 'booking.com', 'airbnb', 'trip', 'tour', 'holiday',
        'vacation', 'travel package', 'tourism'
    ],
    "Travelling expense": [
        'uber', 'ola', 'rapido', 'auto', 'rickshaw', 'taxi', 'cab',
        'train', 'irctc', 'railway', 'bus', 'redbus', 'flight', 'airline',
        'indigo', 'spicejet', 'air india', 'metro', 'toll', 'parking'
    ],
    "Pune & village expense": [
        'pune', 'village', 'gaon', 'native', 'hometown'
    ],
    "Financial Support to Family": [
        'family', 'parents', 'mother', 'father', 'sister', 'brother',
        'home transfer', 'send money', 'support'
    ],
    "SIP": [
        'sip', 'mutual fund', 'zerodha', 'groww', 'coin', 'investment',
        'mf ', 'direct plan', 'nfo'
    ],
}

CREDIT_CATEGORY_KEYWORDS = {
    "Salary": [
        'salary', 'payroll', 'wages', 'ctc', 'stipend', 'employer',
        'company', 'pvt ltd', 'ltd', 'technologies', 'solutions', 'services',
        'corp', 'inc', 'llp'
    ],
    "Side Income": [
        'freelance', 'client', 'project', 'consulting', 'service charge',
        'work', 'contract'
    ],
    "Udemy Income": [
        'udemy', 'course', 'instructor', 'teaching', 'online course'
    ],
    "Youtube Earning": [
        'youtube', 'google adsense', 'adsense', 'content', 'creator',
        'monetization'
    ],
}


def detect_category(text, trans_type):
    text_lower = text.lower()
    keyword_map = CREDIT_CATEGORY_KEYWORDS if trans_type == 'credit' else DEBIT_CATEGORY_KEYWORDS
    for category, keywords in keyword_map.items():
        if any(kw in text_lower for kw in keywords):
            return category
    return "Salary" if trans_type == 'credit' else "Other"


# ============================================================
# TRANSACTION TYPE DETECTION
# ============================================================
def detect_transaction_type(text):
    text_lower = text.lower()
    credit_keywords = [
        'salary', 'credited', 'credit', 'received', 'payment from',
        'deposited', 'income', 'bonus', 'refund', 'reimbursement',
        'money received', 'amount received', 'transferred to you'
    ]
    debit_keywords = [
        'paid to', 'debited', 'debit', 'transaction successful',
        'payment successful', 'amount paid', 'payment done', 'purchase',
        'expense', 'total', 'bill', 'amount due', 'store', 'restaurant',
        'shopping', 'petrol', 'dmart', 'grocery',
        'swiggy', 'zomato', 'amazon', 'flipkart',
        'debited from', 'sent to'
    ]
    credit_score = sum(1 for kw in credit_keywords if kw in text_lower)
    debit_score  = sum(1 for kw in debit_keywords  if kw in text_lower)
    if credit_score > debit_score:
        return 'credit'
    elif debit_score > credit_score:
        return 'debit'
    else:
        return 'debit'


# ============================================================
# TESSERACT PATH
# ============================================================
def get_tesseract_path():
    system = platform.system()
    if system == "Windows":
        for path in [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        ]:
            if os.path.exists(path):
                return path
    elif system == "Darwin":
        return '/usr/local/bin/tesseract'
    else:
        return '/usr/bin/tesseract'
    return None


tesseract_path = get_tesseract_path()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path


# ============================================================
# OCR IMAGE -> TEXT
# ============================================================
@st.cache_data
def extract_text_from_image(uploaded_file):
    try:
        from PIL import ImageOps, ImageEnhance
        image = Image.open(uploaded_file)

        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')

        w, h = image.size
        if w < 1000 or h < 1000:
            scale = max(1000 / w, 1000 / h)
            image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        image = ImageEnhance.Contrast(image).enhance(2.0)
        image = ImageEnhance.Sharpness(image).enhance(2.0)
        image = ImageOps.grayscale(image)

        return pytesseract.image_to_string(image, config='--oem 3 --psm 6')
    except Exception as e:
        st.error(f"OCR Error: {e}")
        return ""


# ============================================================
# WORD-TO-NUMBER  e.g. "Rupees Twenty Only" -> 20.0
# WHY THIS EXISTS:
#   Paytm/PhonePe render the amount as a large styled font that
#   Tesseract cannot read reliably. But they ALWAYS print a line
#   like "Rupees Twenty Only" in plain text below the amount.
#   This is the single most reliable amount source for UPI receipts.
# ============================================================
_WORD_NUMBERS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
    'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
    'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
    'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
    'eighty': 80, 'ninety': 90, 'hundred': 100,
    'thousand': 1000, 'lakh': 100000, 'lac': 100000, 'crore': 10000000,
}


def _words_to_number(phrase: str):
    words = re.findall(r'[a-zA-Z]+', phrase.lower())
    current = 0
    result = 0
    found_any = False
    for w in words:
        if w in ('rupees', 'rupee', 'only', 'rs', 'inr', 'and', 'paise', 'paisa'):
            continue
        val = _WORD_NUMBERS.get(w)
        if val is None:
            continue
        found_any = True
        if val == 100:
            current = (current or 1) * 100
        elif val >= 1000:
            result += (current or 1) * val
            current = 0
        else:
            current += val
    result += current
    return float(result) if found_any and result > 0 else None


# ============================================================
# SANITIZE TEXT — strip bank account numbers, ref IDs, etc.
# This prevents "Yes Bank - 7849" from being parsed as ₹7849.
# ============================================================
def _sanitize_text(text: str) -> str:
    t = text
    # Bank name + account suffix  e.g. "Paytm Payments Bank - 7849", "A/c - 1234"
    t = re.sub(
        r'\b(?:yes|hdfc|sbi|icici|axis|kotak|paytm\s*payments?|paytm|idfc'
        r'|indusind|bob|pnb|canara|union|federal|rbl|au\s+small'
        r'|\w+)\s*bank\s*[-\u2013A/c:]*\s*\d+\b',
        '', t, flags=re.IGNORECASE
    )
    t = re.sub(r'\ba/c\s*[-\u2013:]*\s*\d+', '', t, flags=re.IGNORECASE)
    # Reference ID / UTR lines
    t = re.sub(
        r'(?:reference\s+id|ref\s*(?:no|id)?|txn\s*(?:no|id)?|utr'
        r'|transaction\s*(?:no|id)?|receipt\s*(?:no|id)?|bill\s*(?:no|id)?)'
        r'\s*[:#]?\s*[\dA-Za-z]+',
        '', t, flags=re.IGNORECASE
    )
    # Long digit strings (phone numbers, UPI ref numbers 9+ digits)
    t = re.sub(r'\b\d{9,}\b', '', t)
    # Years 1990-2099
    t = re.sub(r'\b(?:19|20)\d{2}\b', '', t)
    # 6-digit PIN codes
    t = re.sub(r'\b\d{6}\b', '', t)
    return t


# ============================================================
# AMOUNT HELPERS
# ============================================================
def _clean_number(raw: str):
    try:
        val = float(str(raw).replace(',', '').strip())
        if 1.0 <= val <= 1_000_000.0:
            return val
    except (ValueError, TypeError):
        pass
    return None


def _best_from(candidates: list):
    """Most-frequent value wins; tie -> median."""
    vals = [v for v in candidates if v is not None]
    if not vals:
        return None
    from collections import Counter
    cnt = Counter(vals)
    max_freq = max(cnt.values())
    top = sorted(v for v, f in cnt.items() if f == max_freq)
    return top[len(top) // 2]


# ============================================================
# MAIN PARSER
# Priority 0: "Rupees X Only" word form  <- KEY fix for Paytm/PhonePe
# Priority 1: Keyword-anchored (Total, Amount Paid...)
# Priority 2: Rs symbol (real or OCR misread)
# Priority 3: Rs. / INR prefix
# Priority 4: Indian comma-format number
# Priority 5: Decimal (paise) amount
# NO bare-integer fallback (that was the original bug)
# ============================================================
def parse_receipt_text(text: str) -> dict:
    data = {'merchant': None, 'date': None, 'total': None, 'items': []}

    clean = _sanitize_text(text)
    # Normalize OCR misreads of Rs symbol before digits
    clean = re.sub(r'(?<!\w)[%zZ@~](?=\s*\d)', '\u20b9', clean)

    # Priority 0 — "Rupees Twenty Only" word form
    rupees_match = re.search(r'rupees?\s+(.+?)\s+only', clean, re.IGNORECASE)
    if rupees_match:
        word_amt = _words_to_number(rupees_match.group(0))
        if word_amt and 1.0 <= word_amt <= 1_000_000.0:
            data['total'] = str(word_amt)

    # Priority 1 — keyword-anchored
    if not data['total']:
        kw_pat = re.compile(
            r'(?:total\s*amount|grand\s*total|net\s*payable|net\s*amount'
            r'|amount\s*paid|amount\s*due|bill\s*amount|payable\s*amount'
            r'|total\s*bill|total\s*payable|total\s*paid|total\s*dues'
            r'|total|amount|subtotal|sub\s*total|paid|dues)'
            r'[\s:=\u20b9Rs\.]*([\d,]+(?:\.\d{1,2})?)',
            re.IGNORECASE
        )
        p1 = [_clean_number(m) for m in kw_pat.findall(clean)]
        result = _best_from(p1)
        if result:
            data['total'] = str(result)

    # Priority 2 — Rs symbol
    if not data['total']:
        p2 = [_clean_number(m)
              for m in re.findall(r'[\u20b9\u20b9]([\d,]+(?:\.\d{1,2})?)', clean)]
        result = _best_from(p2)
        if result:
            data['total'] = str(result)

    # Priority 3 — Rs./INR prefix
    if not data['total']:
        p3 = [_clean_number(m)
              for m in re.findall(r'(?:Rs\.?|INR)\s*([\d,]+(?:\.\d{1,2})?)',
                                  clean, re.IGNORECASE)]
        result = _best_from(p3)
        if result:
            data['total'] = str(result)

    # Priority 4 — Indian comma-format
    if not data['total']:
        p4 = [_clean_number(m)
              for m in re.findall(r'\b\d{1,3}(?:,\d{2,3})+(?:\.\d{1,2})?\b', clean)]
        result = _best_from(p4)
        if result:
            data['total'] = str(result)

    # Priority 5 — decimal (paise)
    if not data['total']:
        p5 = [_clean_number(m)
              for m in re.findall(r'\b(\d{1,6}\.\d{2})\b', clean)]
        result = _best_from(p5)
        if result:
            data['total'] = str(result)

    # Priority 6 — Fallback for bare integers (max value wins here since no frequency consensus if missed)
    if not data['total']:
        p6_raw = re.findall(r'\b(\d{1,6}(?:\.\d{1,2})?)\b', clean)
        p6 = [_clean_number(m) for m in p6_raw]
        # Ignore explicitly common low-occurrence non-amounts
        p6 = [v for v in p6 if v is not None and v not in [100.0, 24.0, 7.0, 365.0]]
        
        if p6:
            # First try mode if highly confident, otherwise take largest
            from collections import Counter
            cnt = Counter(p6)
            max_f = max(cnt.values())
            if max_f >= 2:
                data['total'] = str([k for k, v in cnt.items() if v == max_f][-1])
            else:
                data['total'] = str(max(p6))

    # Date
    date_patterns = [
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{2,4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            data['date'] = matches[0].strip()
            break

    # Merchant
    skip_re = re.compile(
        r'^(\d{1,2}[:\-/]\d{2}|T\d{8,}|UTR|powered|upi|ref\b|txn\b'
        r'|transaction\s*id|debited|paid\s*to|phonepe|paytm|google\s*pay'
        r'|gpay|bhim|payment\s*receipt|payment\s*successful|rupees|100%)',
        re.IGNORECASE
    )
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    for line in lines:
        if (len(line) > 4
                and not re.match(r'^[\d\s,%.\u20b9]+$', line)
                and not skip_re.match(line)):
            data['merchant'] = line[:60]
            break

    return data


# ============================================================
# MAIN OCR PAGE
# ============================================================
def show_ocr_page(df, sheet):
    st.subheader("Scan Receipt — Auto Detect & Categorize")
    st.markdown("""
        <style>[data-testid="stFileUploader"] small { display: none !important; }</style>
        <p style='color: #4CAF50; font-size: 14.5px;'>
            PhonePe · Paytm · Google Pay · UPI · Shop Bill — sab supported!
        </p>
    """, unsafe_allow_html=True)

    if not tesseract_path or not os.path.exists(tesseract_path):
        st.error("Tesseract OCR not found. Please install it first.")
        return

    for key in ['ocr_parsed', 'ocr_text', 'ocr_type', 'ocr_file_name']:
        if key not in st.session_state:
            st.session_state[key] = None

    uploaded_file = st.file_uploader(
        "Upload Receipt Image (PhonePe, Paytm, UPI, Bill, etc.)",
        type=['png', 'jpg', 'jpeg']
    )

    if uploaded_file and uploaded_file.name != st.session_state['ocr_file_name']:
        st.session_state['ocr_file_name'] = uploaded_file.name
        st.session_state['ocr_parsed']    = None
        st.session_state['ocr_text']      = None
        st.session_state['ocr_type']      = None
        
        # Clear old widget states so the input boxes update properly
        stale_keys = [k for k in st.session_state.keys() if k.startswith('ocr_') and k not in ['ocr_parsed', 'ocr_text', 'ocr_type', 'ocr_file_name']]
        for k in stale_keys:
            del st.session_state[k]

    if not uploaded_file:
        return

    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(uploaded_file, caption="Uploaded Receipt", use_container_width=True)

    with col2:
        if st.session_state['ocr_parsed'] is None:
            with st.spinner("Receipt scan ho raha hai..."):
                extracted_text = extract_text_from_image(uploaded_file)

            if not extracted_text.strip():
                st.warning("Text extract nahi hua. Clearer image try karo.")
                return

            detected_type = detect_transaction_type(extracted_text)
            parsed_data   = parse_receipt_text(extracted_text)
            auto_category = detect_category(extracted_text, detected_type)

            st.session_state['ocr_text']   = extracted_text
            st.session_state['ocr_type']   = detected_type
            st.session_state['ocr_parsed'] = {**parsed_data, 'auto_category': auto_category}

        parsed        = st.session_state['ocr_parsed']
        detected_type = st.session_state['ocr_type']

        with st.expander("View Extracted Text (debug)"):
            st.text(st.session_state['ocr_text'])

        badge_color = "green" if detected_type == 'credit' else "red"
        st.markdown(
            f"Detected: <span style='color:{badge_color}; font-weight:bold; font-size:15px;'>"
            f"{'INCOME (Credit)' if detected_type == 'credit' else 'EXPENSE (Debit)'}</span>",
            unsafe_allow_html=True
        )

        detected_amt = parsed.get('total')
        if detected_amt:
            st.info(f"Detected Amount: **Rs.{float(detected_amt):,.2f}** — galat ho to niche edit karo")
        else:
            st.warning("Amount auto-detect nahi hua — manually enter karo")

        override_type = st.radio(
            "Correct type if wrong:",
            ["debit", "credit"],
            index=0 if detected_type == 'debit' else 1,
            horizontal=True,
            key="ocr_type_override"
        )

        if override_type != detected_type:
            parsed['auto_category'] = detect_category(
                st.session_state['ocr_text'], override_type
            )
            st.session_state['ocr_type'] = override_type

        try:
            default_amount = float(parsed['total'] or 0.0)
        except (ValueError, TypeError):
            default_amount = 0.0

        try:
            default_date_str = pd.to_datetime(
                parsed['date'] or datetime.now().strftime('%d-%m-%Y'), dayfirst=True
            ).strftime('%d-%m-%Y')
        except Exception:
            default_date_str = datetime.now().strftime('%d-%m-%Y')

        st.markdown("---")
        st.markdown("### Confirm & Edit Details")

        if override_type == 'debit':
            debit_categories = [
                "Today's expense ", "Weekend expense", "Financial Support to Family",
                "Shopping", "Petrol", "Self Care", "Recharge", "SIP",
                "Veggies,Gas cylinder and Dmart", "Rent,Maid & Electricity bills",
                "Pune & village expense", "Travelling expense", "Trips", "Other"
            ]
            auto_cat  = parsed.get('auto_category', 'Other')
            cat_index = (debit_categories.index(auto_cat)
                         if auto_cat in debit_categories else len(debit_categories) - 1)

            merchant = st.text_input("Merchant / Store", parsed['merchant'] or "", key="ocr_merchant")
            date_val = st.text_input("Date (DD-MM-YYYY)", default_date_str, key="ocr_date_d")
            amount   = st.number_input("Amount (Rs.)", min_value=0.0, value=default_amount,
                                       step=1.0, format="%.2f", key="ocr_amount_d")
            category = st.selectbox("Category", debit_categories, index=cat_index, key="ocr_cat_d")
            notes    = st.text_input("Additional Notes", "", key="ocr_notes")

            if st.button("Add Expense", type="primary", use_container_width=True, key="ocr_add_debit"):
                if amount <= 0:
                    st.error("Amount 0 se zyada dalo.")
                else:
                    _save_ocr_entry(
                        df=df, sheet=sheet, date_str=date_val,
                        trans_type='debit', amount=amount, category=category,
                        details=f"{merchant} - {notes}" if notes else (merchant or 'OCR Scan')
                    )

        else:
            credit_categories = ["Salary", "Side Income", "Udemy Income", "Youtube Earning"]
            auto_cat  = parsed.get('auto_category', 'Salary')
            cat_index = (credit_categories.index(auto_cat)
                         if auto_cat in credit_categories else 0)

            source   = st.text_input("Source (Company / Person)", parsed['merchant'] or "", key="ocr_source")
            date_val = st.text_input("Date (DD-MM-YYYY)", default_date_str, key="ocr_date_c")
            amount   = st.number_input("Amount (Rs.)", min_value=0.0, value=default_amount,
                                       step=1.0, format="%.2f", key="ocr_amount_c")
            category = st.selectbox("Income Type", credit_categories, index=cat_index, key="ocr_cat_c")

            if st.button("Add Income", type="primary", use_container_width=True, key="ocr_add_credit"):
                if amount <= 0:
                    st.error("Amount 0 se zyada dalo.")
                else:
                    _save_ocr_entry(
                        df=df, sheet=sheet, date_str=date_val,
                        trans_type='credit', amount=amount, category=category,
                        details=source or 'OCR Scan'
                    )


# ============================================================
# HELPER — save entry
# ============================================================
def _save_ocr_entry(df, sheet, date_str, trans_type, amount, category, details):
    from utils.gsheet_utils import update_data_to_gsheet
    try:
        parsed_date = pd.to_datetime(date_str, dayfirst=True).strftime('%d-%m-%Y')
        month       = pd.to_datetime(parsed_date, dayfirst=True).strftime('%B')
    except Exception:
        parsed_date = datetime.now().strftime('%d-%m-%Y')
        month       = datetime.now().strftime('%B')

    if trans_type == 'credit':
        new_row = {
            'date': parsed_date, 'month': month,
            'credit': amount,    'credit_details': details,
            'debit': 0,          'debit_details': 'NA',
            'category': category
        }
    else:
        new_row = {
            'date': parsed_date, 'month': month,
            'credit': 0,         'credit_details': 'NA',
            'debit': -amount,    'debit_details': details,
            'category': category
        }

    new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    st.session_state['live_df'] = new_df
    update_data_to_gsheet(sheet, new_df)

    for key in ['ocr_parsed', 'ocr_text', 'ocr_type', 'ocr_file_name']:
        st.session_state[key] = None

    label = "income" if trans_type == 'credit' else "expense"
    st.success(f"Rs.{amount:,.0f} {label} added under **{category}**!")
    st.balloons()