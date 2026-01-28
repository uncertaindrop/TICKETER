# -*- coding: utf-8 -*-
"""
TICKETER CLOUD VERSION - Optimized for cloud deployment
"""

import os
import json
import random
import traceback
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Any
from flask import Flask, request, jsonify, send_from_directory

# ---------- LOGGING SETUP ----------
import logging

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

log_filename = os.path.join(LOGS_DIR, f"ticketer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] [%(funcName)s:%(lineno)d] %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("="*80)
logger.info("TICKETER CLOUD VERSION - Starting")
logger.info("="*80)

# ---------- PDF PARSING ----------
try:
    from pdfdata2 import extract as pdfdata2_extract
    logger.info("✓ pdfdata2 module loaded")
except ImportError:
    pdfdata2_extract = None
    logger.warning("⚠ pdfdata2 module not found")

from PyPDF2 import PdfReader

PDF_UPLOAD_DIR = "uploads"
os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)

SCREENSHOTS_DIR = "screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def ensure_dot(value: Any) -> str:
    v = ("" if value is None else str(value)).strip()
    return v if v else "."


def parse_pdf(path: str) -> Dict[str, str]:
    logger.info(f"Parsing PDF: {path}")
    
    if pdfdata2_extract is not None:
        try:
            raw = pdfdata2_extract(path)
            logger.debug(f"PDF parse result: {raw}")
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            raw = {}
    else:
        raw = {}

    result = {
        "name": ensure_dot(raw.get("name")),
        "surname": ensure_dot(raw.get("surname")),
        "phone": ensure_dot(raw.get("phone")),
        "invoice": ensure_dot(raw.get("invoice")),
        "cstcode": ensure_dot(raw.get("cst code")),
        "material": ensure_dot(raw.get("material")),
        "product": ensure_dot(raw.get("product")),
        "serial": ensure_dot(raw.get("serial")),
    }
    
    logger.info(f"✓ PDF parsed: {result}")
    return result


# ---------- SELENIUM IMPORTS ----------
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException
)

PMM_BASE_URL = "https://pmm.irepair.gr"
COOKIES_FILE = "pmm_cookies.json"

# [Previous constants remain the same - VISIBLE_DAMAGE_OPTIONS, etc.]
VISIBLE_DAMAGE_OPTIONS = ["light signs of use", "brand new", "some scratches", "hits on frame"]
ITEMS_LEFT_OPTIONS = ["only device left with us", "full box device left with us"]
PROMO_OPTIONS = ["promo setup & optimization", "software optimization and account setup", "promo service – data check & configuration", "promo device setup and update"]
PRINTER_PROBLEMS = ["printer not printing", "paper jam randomly", "printer offline on network", "lines / streaks on prints"]
LAPTOP_PROBLEMS = ["slow performance and freezes", "random shutdowns while in use", "blue screen errors", "overheating under light usage"]
TABLET_PROBLEMS = ["touchscreen not responsive", "battery drains quickly", "tablet not charging", "apps crashing frequently"]
APPLIANCE_PROBLEMS = ["device not powering on", "random error codes displayed", "unusual noise during operation", "device stops mid-cycle"]
PHONE_PROBLEMS = ["screen flickering and ghost touches", "device restarting randomly", "battery drains very fast", "no sound on calls", "camera not focusing"]
ETA_OPTIONS = ["ETA: same day service if possible.", "ETA: 1 business day.", "ETA: 2–3 business days."]
PROMO_RESOLUTION_OPTIONS = ["setup done", "ready", "setup finished", "finished setting up", "cst informed"]
NORMAL_RESOLUTION_OPTIONS = ["device works fine", "device ok cst informed", "no issues", "no problem", "works fine"]


@dataclass
class ParsedInvoice:
    id: str
    filename: str
    path: str
    fields: Dict[str, str]


parsed_files: Dict[str, ParsedInvoice] = {}


def save_screenshot(driver: webdriver.Chrome, prefix: str) -> str:
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{prefix}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        driver.save_screenshot(filepath)
        logger.info(f"📸 Screenshot: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        return ""


def build_repair_description(ticket_type: str, items_left_text: str) -> str:
    ticket_type = ticket_type.upper().strip()
    
    if ticket_type == "PROMO":
        problem = random.choice(PROMO_OPTIONS)
    elif ticket_type == "QUICK REPAIR PRINTER":
        problem = random.choice(PRINTER_PROBLEMS)
    elif ticket_type == "QUICK REPAIR LAPTOP":
        problem = random.choice(LAPTOP_PROBLEMS)
    elif ticket_type == "QUICK REPAIR TABLET":
        problem = random.choice(TABLET_PROBLEMS)
    elif ticket_type == "QUICK REPAIR APPLIANCE":
        problem = random.choice(APPLIANCE_PROBLEMS)
    else:
        problem = random.choice(PHONE_PROBLEMS)

    eta = random.choice(ETA_OPTIONS)
    return f"{items_left_text}. {problem}. {eta}"


def save_cookies(driver: webdriver.Chrome) -> None:
    try:
        cookies = driver.get_cookies()
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ Cookies saved")
    except Exception as e:
        logger.error(f"Cookie save failed: {e}")


def load_cookies(driver: webdriver.Chrome) -> None:
    if not os.path.exists(COOKIES_FILE):
        return
    
    try:
        with open(COOKIES_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        
        driver.get(PMM_BASE_URL)
        
        for c in cookies:
            c.pop('sameSite', None)
            try:
                driver.add_cookie(c)
            except:
                continue
        
        logger.info("✓ Cookies loaded")
    except Exception as e:
        logger.error(f"Cookie load failed: {e}")


def get_driver() -> webdriver.Chrome:
    """Initialize Chrome WebDriver - cloud optimized"""
    logger.info("Initializing Chrome WebDriver (cloud mode)...")
    
    chrome_options = ChromeOptions()
    
    # Cloud-optimized settings
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.set_page_load_timeout(120)
    
    logger.info("✓ Chrome WebDriver initialized (headless)")
    return driver


def wait_for_element(driver: webdriver.Chrome, by: By, value: str, 
                     timeout: int = 30, condition="presence") -> Any:
    logger.debug(f"Waiting for: {by}={value} ({condition})")
    
    wait = WebDriverWait(driver, timeout)
    
    try:
        if condition == "presence":
            element = wait.until(EC.presence_of_element_located((by, value)))
        elif condition == "visible":
            element = wait.until(EC.visibility_of_element_located((by, value)))
        elif condition == "clickable":
            element = wait.until(EC.element_to_be_clickable((by, value)))
        else:
            raise ValueError(f"Unknown condition: {condition}")
        
        logger.debug(f"✓ Element found")
        return element
    
    except TimeoutException:
        logger.error(f"✗ Timeout: {by}={value}")
        save_screenshot(driver, f"timeout_{value[:30]}")
        raise


def safe_click(driver: webdriver.Chrome, element, description: str = "element") -> bool:
    logger.debug(f"Clicking: {description}")
    
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        time.sleep(0.3)
        
        try:
            element.click()
            logger.debug(f"✓ Clicked (regular)")
            return True
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", element)
            logger.debug(f"✓ Clicked (JS)")
            return True
            
    except Exception as e:
        logger.error(f"✗ Click failed: {e}")
        save_screenshot(driver, f"click_failed")
        return False


def login_if_needed(driver: webdriver.Chrome, username: str, password: str) -> None:
    logger.info("="*60)
    logger.info("LOGIN PROCESS")
    logger.info("="*60)
    
    wait = WebDriverWait(driver, 600)

    logger.info("Trying existing cookies...")
    load_cookies(driver)
    driver.get(PMM_BASE_URL + "/users/dashboard")
    
    if "/users/dashboard" in driver.current_url:
        logger.info("✓ Logged in via cookies")
        return

    logger.info("Full login required...")
    driver.get(PMM_BASE_URL + "/")
    
    username_field = wait_for_element(driver, By.CSS_SELECTOR, "#username", timeout=30)
    username_field.clear()
    username_field.send_keys(username)
    logger.info(f"✓ Username: {username}")

    password_field = wait_for_element(driver, By.CSS_SELECTOR, "#password-field", timeout=30)
    password_field.clear()
    password_field.send_keys(password)
    logger.info("✓ Password entered")

    try:
        email_radio = driver.find_element(By.CSS_SELECTOR, "#authenticator_type_2")
        if not email_radio.is_selected():
            email_radio.click()
            logger.info("✓ Email authenticator selected")
    except:
        pass

    login_clicked = False
    for locator in [
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//button[contains(.,'Login') or contains(.,'Sign In')]"),
        (By.XPATH, "//input[@type='submit']"),
    ]:
        try:
            btn = driver.find_element(*locator)
            btn.click()
            login_clicked = True
            logger.info(f"✓ Login button clicked")
            break
        except:
            continue

    if not login_clicked:
        raise RuntimeError("Login button not found")

    logger.info("⏳ Waiting for CAPTCHA/OTP (manual user action required)...")
    
    try:
        wait.until(EC.url_contains("/otp-authentication"))
        logger.info("✓ OTP page reached")
    except:
        pass

    wait.until(EC.url_contains("/users/dashboard"))
    logger.info("✓ Dashboard reached")
    save_cookies(driver)
    logger.info("="*60)


# [Rest of the functions from TICKETER_IMPROVED.py - truncated for brevity]
# Including: select2_by_visible_text, assign_technician_robust, fill_resolution_field,
# progress_status_robust, update_status_and_resolution, create_single_ticket, run_ticket_batch

# NOTE: Copy all the robust functions from TICKETER_IMPROVED.py here
# I'm keeping this shorter to focus on cloud deployment specifics


def run_ticket_batch(crm_username: str, crm_password: str, 
                     tickets_payload: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    logger.info(f"Starting batch of {len(tickets_payload)} tickets")
    results = []
    driver = None
    
    try:
        driver = get_driver()
        login_if_needed(driver, crm_username, crm_password)

        for idx, t in enumerate(tickets_payload, start=1):
            # Process each ticket (implementation from TICKETER_IMPROVED.py)
            pass
            
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
    
    return results


# ========== FLASK API ==========

app = Flask(__name__)

# Enable CORS for cloud deployment
from flask_cors import CORS
CORS(app)


@app.route("/")
def index():
    return send_from_directory('.', "TICKETHELPER.html")


@app.route("/parse_pdfs", methods=["POST"])
def api_parse_pdfs():
    global parsed_files
    parsed_files = {}

    files = request.files.getlist("pdfs")
    logger.info(f"Parsing {len(files)} PDFs")
    
    out = []

    for idx, f in enumerate(files):
        if not f.filename.lower().endswith(".pdf"):
            continue
            
        safe_name = f.filename
        path = os.path.join(PDF_UPLOAD_DIR, safe_name)
        f.save(path)

        fields = parse_pdf(path)
        
        normalized = {
            "name": ensure_dot(fields.get("name")),
            "surname": ensure_dot(fields.get("surname")),
            "phone": ensure_dot(fields.get("phone")),
            "invoice": ensure_dot(fields.get("invoice")),
            "cstcode": ensure_dot(fields.get("cstcode")),
            "material": ensure_dot(fields.get("material")),
            "product": ensure_dot(fields.get("product")),
            "serial": ensure_dot(fields.get("serial")),
        }

        file_id = str(idx + 1)
        parsed = ParsedInvoice(
            id=file_id,
            filename=safe_name,
            path=path,
            fields=normalized,
        )
        parsed_files[file_id] = parsed
        out.append({
            "id": file_id,
            "filename": safe_name,
            "fields": normalized,
        })

    return jsonify({"files": out})


@app.route("/create_tickets", methods=["POST"])
def api_create_tickets():
    data = request.get_json(force=True)
    crm_username = data.get("crm_username", "").strip()
    crm_password = data.get("crm_password", "").strip()
    tickets_payload = data.get("tickets", [])

    if not crm_username or not crm_password:
        return jsonify({"error": "Missing credentials"}), 400

    try:
        results = run_ticket_batch(crm_username, crm_password, tickets_payload)
        return jsonify({"results": results})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


if __name__ == "__main__":
    # Cloud deployment: bind to 0.0.0.0 and use PORT env var
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=False)
