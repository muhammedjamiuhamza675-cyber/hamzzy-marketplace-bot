#!/usr/bin/env python3
"""
HAMZZY MARKETPLACE BOT V13.0 - COMPLETE WITH FB OPTION
- Complete IG Shop with screenshots
- Facebook account sales
- Email/IG/Bulk stock
- Payment system with admin approval
- Verification code system
- Full admin panel
"""

import telebot
from telebot import types
import sqlite3
import os
import time
import datetime
import json
import random
import re
import logging
import shutil
import threading
from io import BytesIO
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

# =================================================================================
# CONFIGURATION
# =================================================================================

BOT_TOKEN = "8694523853:AAHsmwaN3VEW2oRrDX3YHhCZHakDnb3fp2U"
MASTER_ADMIN_ID = 7443685686
BOT_USERNAME = "hamzzyhacket"
MY_SIGNATURE = "@hamzzyhacket"
CHANNEL_LINK = "https://t.me/hamzzylogs"

# Payment Details
OPAY_ACCOUNT = "9032741650"
OPAY_NAME = "Muhammed Jamiu Hamza"
PALMPAY_ACCOUNT = "9032741650"
PALMPAY_NAME = "Muhammed Jamiu Hamza"
BANK_ACCOUNT = "9032741650"
BANK_NAME = "Muhammed Jamiu Hamza"

# Limits
MIN_DEPOSIT = 500
MIN_WITHDRAWAL = 5000
REFERRAL_BONUS = 200

# Create directories
for dir_name in ["backups", "logs", "payment_images", "ig_screenshots", "fb_screenshots"]:
    Path(dir_name).mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/bot_{datetime.datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =================================================================================
# AUTO POST TO CHANNEL (PURCHASES ONLY)
# =================================================================================

CHANNEL_ID = "@hamzzylogs"  # Your channel username

def post_purchase_to_channel(product_type: str, product_name: str, amount: float):
    """Post only when someone makes a purchase"""
    symbol = get_setting('currency_symbol', '₦')
    bot_username = BOT_USERNAME
    
    # Create message based on product type
    if product_type == "email":
        msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
              📧 EMAIL SOLD! 📧
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 Product: Email Account
📸 Followers: {product_name}
💰 Price: {symbol}{amount:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 <a href="https://t.me/{bot_username}">CLICK HERE TO BUY</a>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 {MY_SIGNATURE}
"""
    elif product_type == "complete_ig":
        msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
              🎁 COMPLETE IG SOLD! 🎁
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 Product: {product_name}
💰 Price: {symbol}{amount:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 <a href="https://t.me/{bot_username}">CLICK HERE TO BUY</a>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 {MY_SIGNATURE}
"""
    elif product_type == "facebook":
        msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
              📘 FACEBOOK SOLD! 📘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 Product: Facebook Account
📂 Category: {product_name}
💰 Price: {symbol}{amount:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 <a href="https://t.me/{bot_username}">CLICK HERE TO BUY</a>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 {MY_SIGNATURE}
"""
    elif product_type == "bulk":
        msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
              📦 BULK EMAILS SOLD! 📦
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 Product: Bulk Email Package
📸 {product_name}
💰 Price: {symbol}{amount:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 <a href="https://t.me/{bot_username}">CLICK HERE TO BUY</a>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 {MY_SIGNATURE}
"""
    else:
        msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
              🛒 NEW PURCHASE! 🛒
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 Product: {product_name}
💰 Price: {symbol}{amount:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 <a href="https://t.me/{bot_username}">CLICK HERE TO BUY</a>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 {MY_SIGNATURE}
"""
    
    try:
        bot.send_message(CHANNEL_ID, msg, parse_mode='HTML', disable_web_page_preview=True)
        return True
    except Exception as e:
        print(f"Failed to post to channel: {e}")
        return False

# =================================================================================
# DAILY STOCK AUTO-POST (7:00 AM AND 7:00 PM)
# =================================================================================

def daily_stock_post():
    """Auto post available stock to channel at 7:00 AM and 7:00 PM every day"""
    last_posted_dates = {}
    
    while True:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")
        
        # Check if auto-post is enabled
        c = db.cursor()
        c.execute("SELECT setting_value FROM bot_settings WHERE setting_key = 'auto_post_enabled'")
        result = c.fetchone()
        auto_post_enabled = result[0] == 'True' if result else True
        
        # Get scheduled times from database
        c.execute("SELECT setting_value FROM bot_settings WHERE setting_key = 'auto_post_time'")
        time1_result = c.fetchone()
        time1 = time1_result[0] if time1_result else "07:00"
        
        c.execute("SELECT setting_value FROM bot_settings WHERE setting_key = 'auto_post_time2'")
        time2_result = c.fetchone()
        time2 = time2_result[0] if time2_result and time2_result[0] else "19:00"
        
        scheduled_times = [time1, time2]
        
        for scheduled_time in scheduled_times:
            if scheduled_time and current_time == scheduled_time and current_date not in last_posted_dates.get(scheduled_time, []):
                if auto_post_enabled:
                    symbol = get_setting('currency_symbol', '₦')
                    
                    # Get email stock
                    c.execute("SELECT followers_count, COUNT(*) as cnt FROM email_stock WHERE status = 'available' GROUP BY followers_count ORDER BY followers_count ASC LIMIT 10")
                    email_stocks = c.fetchall()
                    
                    # Get Complete IG stock
                    c.execute("SELECT COUNT(*) FROM ig_shop_stock WHERE status = 'available'")
                    complete_ig_count = c.fetchone()[0]
                    
                    # Get Facebook stock
                    c.execute("SELECT COUNT(*) FROM fb_stock WHERE status = 'available'")
                    fb_count = c.fetchone()[0]
                    
                    # Get Bulk stock
                    c.execute("SELECT COUNT(*) FROM bulk_stock WHERE status = 'available'")
                    bulk_count = c.fetchone()[0]
                    
                    # Get total users
                    c.execute("SELECT COUNT(*) FROM users")
                    total_users = c.fetchone()[0]
                    
                    # Check if any stock exists
                    has_stock = email_stocks or complete_ig_count > 0 or fb_count > 0 or bulk_count > 0
                    
                    if has_stock:
                        # Format time label
                        hour = int(scheduled_time.split(':')[0])
                        minute = scheduled_time.split(':')[1]
                        am_pm = "AM" if hour < 12 else "PM"
                        hour_12 = hour if hour <= 12 else hour - 12
                        if hour_12 == 0:
                            hour_12 = 12
                        time_label = f"{hour_12}:{minute} {am_pm}"
                        
                        # Build email message
                        if email_stocks:
                            email_msg = ""
                            for stock in email_stocks:
                                email_msg += f"   📧 {stock['followers_count']} followers - {stock['cnt']} in stock\n"
                        else:
                            email_msg = "   📧 No emails in stock\n"
                        
                        msg = f"""
╔══════════════════════════════════════════════════════════╗
║           📦 DAILY STOCK UPDATE - {time_label} 📦           ║
╠══════════════════════════════════════════════════════════╣
║  📧 EMAIL ACCOUNTS:                                      ║
║{email_msg}                                              ║
╠══════════════════════════════════════════════════════════╣
║  🎁 COMPLETE IG: {complete_ig_count} available                    ║
║  📘 FACEBOOK: {fb_count} available                               ║
║  📦 BULK EMAILS: {bulk_count} packages available                  ║
╠══════════════════════════════════════════════════════════╣
║  👥 TOTAL USERS: {total_users}                                   ║
╠══════════════════════════════════════════════════════════╣
║  👉 <a href="https://t.me/{BOT_USERNAME}">CLICK HERE TO BUY</a>                 ║
╠══════════════════════════════════════════════════════════╣
║  💎 {MY_SIGNATURE}                                        ║
╚══════════════════════════════════════════════════════════╝
"""
                        try:
                            bot.send_message(CHANNEL_ID, msg, parse_mode='HTML', disable_web_page_preview=True)
                            print(f"✅ Stock posted at {scheduled_time}")
                        except Exception as e:
                            print(f"❌ Failed to post: {e}")
                    else:
                        print(f"⏸️ No stock available at {scheduled_time} - Skipping")
                
                # Mark as posted for today
                if scheduled_time not in last_posted_dates:
                    last_posted_dates[scheduled_time] = []
                last_posted_dates[scheduled_time].append(current_date)
                time.sleep(60)
                break
        
        # Clean old dates
        for time_slot in list(last_posted_dates.keys()):
            last_posted_dates[time_slot] = [d for d in last_posted_dates[time_slot] if d >= (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")]
        
        time.sleep(30)
        
# =================================================================================
# DATABASE
# ================================================================================= =================================================================================

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.conn = None
        self.init_db()
    
    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect('marketplace.db', check_same_thread=False, timeout=30)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA synchronous = OFF")
            self.conn.execute("PRAGMA journal_mode = WAL")
        return self.conn
    
    def cursor(self):
        return self.connect().cursor()
    
    def commit(self):
        if self.conn:
            self.conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def init_db(self):
        c = self.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            wallet_balance REAL DEFAULT 0,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            total_referrals INTEGER DEFAULT 0,
            referral_earnings REAL DEFAULT 0,
            join_date TEXT,
            last_active TEXT,
            total_spent REAL DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0
        )''')
        
        # Pricing rules table
        c.execute('''CREATE TABLE IF NOT EXISTS pricing_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT,
            rule_type TEXT,
            min_value INTEGER,
            max_value INTEGER,
            price REAL,
            is_active INTEGER DEFAULT 1,
            priority INTEGER DEFAULT 0,
            created_by INTEGER,
            created_date TEXT
        )''')
        
        # IG SHOP PRICING RULES
        c.execute('''CREATE TABLE IF NOT EXISTS ig_shop_pricing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT,
            price REAL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_by INTEGER,
            created_date TEXT
        )''')
        
        # IG SHOP STOCK
        c.execute('''CREATE TABLE IF NOT EXISTS ig_shop_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            username TEXT,
            password TEXT,
            email TEXT,
            email_password TEXT,
            followers_count INTEGER,
            price REAL,
            screenshot_file_id TEXT,
            description TEXT,
            status TEXT DEFAULT 'available',
            added_by INTEGER,
            added_date TEXT,
            sold_date TEXT,
            sold_to INTEGER,
            credentials_released INTEGER DEFAULT 0
        )''')
        
        # IG SHOP ORDERS
        c.execute('''CREATE TABLE IF NOT EXISTS ig_shop_orders (
            order_id TEXT PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            product_name TEXT,
            amount REAL,
            status TEXT DEFAULT 'pending',
            order_date TEXT,
            delivered_date TEXT,
            code_requested INTEGER DEFAULT 0,
            code_provided TEXT
        )''')
        
        # Email stock
        c.execute('''CREATE TABLE IF NOT EXISTS email_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            username TEXT,
            password TEXT,
            has_password INTEGER DEFAULT 0,
            followers_count INTEGER,
            price REAL,
            status TEXT DEFAULT 'available',
            added_by INTEGER,
            added_date TEXT,
            sold_date TEXT,
            sold_to INTEGER
        )''')
        
        # IG stock
        c.execute('''CREATE TABLE IF NOT EXISTS ig_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ig_username TEXT UNIQUE,
            password TEXT,
            has_password INTEGER DEFAULT 0,
            followers_count INTEGER,
            price REAL,
            status TEXT DEFAULT 'available',
            added_by INTEGER,
            added_date TEXT,
            sold_date TEXT,
            sold_to INTEGER
        )''')
        
        # Bulk stock
        c.execute('''CREATE TABLE IF NOT EXISTS bulk_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emails TEXT,
            emails_count INTEGER,
            followers_per_email INTEGER,
            total_followers INTEGER,
            price REAL,
            status TEXT DEFAULT 'available',
            added_by INTEGER,
            added_date TEXT,
            sold_date TEXT,
            sold_to INTEGER
        )''')
        
        # Orders
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_id INTEGER,
            product_type TEXT,
            product_name TEXT,
            quantity INTEGER,
            amount REAL,
            delivery_info TEXT,
            order_date TEXT,
            status TEXT DEFAULT 'completed'
        )''')
        
        # Bulk orders
        c.execute('''CREATE TABLE IF NOT EXISTS bulk_orders (
            order_id TEXT PRIMARY KEY,
            user_id INTEGER,
            followers_per_email INTEGER,
            total_emails INTEGER,
            total_followers INTEGER,
            amount REAL,
            emails TEXT,
            status TEXT DEFAULT 'pending',
            order_date TEXT
        )''')
        
        # Transactions
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
            txn_id TEXT PRIMARY KEY,
            user_id INTEGER,
            amount REAL,
            type TEXT,
            reference TEXT,
            status TEXT,
            timestamp TEXT,
            processed_by INTEGER
        )''')
        
        # Payments
        c.execute('''CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            user_id INTEGER,
            amount REAL,
            method TEXT,
            reference TEXT,
            image_file_id TEXT,
            status TEXT DEFAULT 'pending',
            timestamp TEXT,
            processed_by INTEGER,
            processed_date TEXT
        )''')
        
        # Withdrawals
        c.execute('''CREATE TABLE IF NOT EXISTS withdrawals (
            withdraw_id TEXT PRIMARY KEY,
            user_id INTEGER,
            amount REAL,
            bank_name TEXT,
            account_number TEXT,
            account_name TEXT,
            status TEXT DEFAULT 'pending',
            request_date TEXT,
            processed_date TEXT,
            processed_by INTEGER
        )''')
        
        # Admin wallet
        c.execute('''CREATE TABLE IF NOT EXISTS admin_wallet (
            id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0,
            total_earned REAL DEFAULT 0,
            total_withdrawn REAL DEFAULT 0,
            last_updated TEXT
        )''')
        
        # Notifications
        c.execute('''CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            created_date TEXT
        )''')
        
        # Bot settings
        c.execute('''CREATE TABLE IF NOT EXISTS bot_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT,
            description TEXT,
            updated_date TEXT
        )''')
        
        # CODE REQUESTS
        c.execute('''CREATE TABLE IF NOT EXISTS code_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            order_id TEXT,
            request_date TEXT,
            status TEXT DEFAULT 'pending',
            code TEXT,
            processed_by INTEGER,
            processed_date TEXT
        )''')
        
        # FB CATEGORIES
        c.execute('''CREATE TABLE IF NOT EXISTS fb_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            display_name TEXT,
            price REAL,
            has_page INTEGER DEFAULT 0,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_date TEXT,
            updated_date TEXT
        )''')
        
        # FB STOCK
        c.execute('''CREATE TABLE IF NOT EXISTS fb_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            password TEXT,
            category_id INTEGER,
            account_age TEXT,
            has_screenshot INTEGER DEFAULT 0,
            screenshot_file_ids TEXT,
            price REAL,
            status TEXT DEFAULT 'available',
            added_by INTEGER,
            added_date TEXT,
            sold_date TEXT,
            sold_to INTEGER
        )''')
        
        
                # ========== INSERT DEFAULT DATA ==========
        
        # Insert default pricing rules
        result = c.execute('SELECT COUNT(*) FROM pricing_rules').fetchone()
        if result[0] == 0:
            default_rules = [
                ('30-49', 'range', 30, 49, 1500, 1, 10),
                ('50-80', 'range', 50, 80, 2000, 1, 10),
                ('90-100', 'range', 90, 100, 3000, 1, 10),
                ('200+', 'min', 200, None, 3500, 1, 20),
                ('300+', 'min', 300, None, 4000, 1, 20),
                ('400+', 'min', 400, None, 4500, 1, 20),
                ('500+', 'min', 500, None, 5000, 1, 20),
                ('600+', 'min', 600, None, 5500, 1, 20),
                ('700+', 'min', 700, None, 6000, 1, 20),
                ('800+', 'min', 800, None, 6500, 1, 20),
                ('900+', 'min', 900, None, 7000, 1, 20),
                ('1000+', 'min', 1000, None, 7500, 1, 20),
                ('1500+', 'min', 1500, None, 8500, 1, 20),
                ('2000+', 'min', 2000, None, 9500, 1, 20),
                ('2500+', 'min', 2500, None, 10500, 1, 20),
                ('3000+', 'min', 3000, None, 11500, 1, 20),
                ('3500+', 'min', 3500, None, 12500, 1, 20),
                ('4000+', 'min', 4000, None, 13500, 1, 20),
                ('4500+', 'min', 4500, None, 14500, 1, 20),
                ('5000+', 'min', 5000, None, 15500, 1, 20),
            ]
            for rule in default_rules:
                c.execute('''INSERT INTO pricing_rules (rule_name, rule_type, min_value, max_value, price, is_active, priority, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (rule[0], rule[1], rule[2], rule[3], rule[4], rule[5], rule[6], datetime.datetime.now().isoformat()))
        
        # Insert default IG SHOP pricing rules
        result2 = c.execute('SELECT COUNT(*) FROM ig_shop_pricing').fetchone()
        if result2[0] == 0:
            default_ig_pricing = [
                ('Basic IG Account', 5000, '1000+ followers, email access', 1, 1),
                ('Premium IG Account', 10000, '5000+ followers, email + phone access', 1, 2),
                ('Verified IG Account', 50000, 'Verified badge, high engagement', 1, 3),
                ('Business IG Account', 15000, 'Business profile, 2000+ followers', 1, 4),
            ]
            for rule in default_ig_pricing:
                c.execute('''INSERT INTO ig_shop_pricing 
                            (rule_name, price, description, is_active, sort_order, created_date) 
                            VALUES (?, ?, ?, ?, ?, ?)''',
                          (rule[0], rule[1], rule[2], rule[3], rule[4], datetime.datetime.now().isoformat()))
        
        # Insert default FB categories
        result3 = c.execute('SELECT COUNT(*) FROM fb_categories').fetchone()
        if result3[0] == 0:
            default_fb_categories = [
                ("local_normal", "🇳🇬 Local Nigeria FB", 2000, 0, "Local Nigerian account", 1, 1),
                ("local_with_page", "🇳🇬 Local Nigeria FB + Page", 3500, 1, "Local account with page", 1, 2),
                ("foreign_normal", "🌍 Foreign FB", 3000, 0, "Foreign account", 1, 3),
                ("foreign_with_page", "🌍 Foreign FB + Page", 4500, 1, "Foreign account with page", 1, 4),
            ]
            for name, display, price, has_page, desc, active, order in default_fb_categories:
                c.execute('INSERT OR IGNORE INTO fb_categories (name, display_name, price, has_page, description, is_active, sort_order, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                          (name, display, price, has_page, desc, active, order, datetime.datetime.now().isoformat()))
        
        # Insert default settings
        default_settings = [
            ('bot_name', 'Hamzzy Marketplace', 'Bot display name'),
            ('currency_symbol', '₦', 'Currency symbol'),
            ('min_deposit', '500', 'Minimum deposit'),
            ('min_withdrawal', '1000', 'Minimum withdrawal'),
            ('referral_bonus', '250', 'Referral bonus'),
            ('email_password_extra', '30', 'Extra % for email+password'),
            ('ig_password_extra', '30', 'Extra % for IG+password'),
            ('auto_post_enabled', 'True', 'Enable/disable auto posting to channel'),
            ('auto_post_time', '07:00', 'Time for auto post (24-hour format)'),
            ('auto_post_time2', '19:00', 'Second time for auto post'),
        ]
        for key, value, desc in default_settings:
            c.execute('INSERT OR IGNORE INTO bot_settings (setting_key, setting_value, description, updated_date) VALUES (?, ?, ?, ?)',
                      (key, value, desc, datetime.datetime.now().isoformat()))
        
        # Insert admin wallet
        result4 = c.execute('SELECT COUNT(*) FROM admin_wallet').fetchone()
        if result4[0] == 0:
            c.execute('INSERT INTO admin_wallet (balance, total_earned, total_withdrawn, last_updated) VALUES (0, 0, 0, ?)',
                      (datetime.datetime.now().isoformat(),))
        
        # Make master admin
        c.execute('UPDATE users SET is_admin = 1 WHERE user_id = ?', (MASTER_ADMIN_ID,))
        
        # Create default admin user if not exists
        c.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, referral_code, join_date, last_active, is_admin, wallet_balance) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                  (MASTER_ADMIN_ID, BOT_USERNAME, "Master Admin", f"ADMIN{MASTER_ADMIN_ID}", datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat(), 1, 0))
        
        self.commit()
        logger.info("Database initialized")

db = Database()
bot = telebot.TeleBot(BOT_TOKEN)
user_sessions = {}

# =================================================================================
# HELPER FUNCTIONS
# =================================================================================

def get_setting(key: str, default: str = "") -> str:
    c = db.cursor()
    c.execute("SELECT setting_value FROM bot_settings WHERE setting_key = ?", (key,))
    row = c.fetchone()
    return row[0] if row else default

def get_user(user_id: int) -> Optional[Dict]:
    c = db.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    return dict(row) if row else None

def is_admin(user_id: int) -> bool:
    if user_id == MASTER_ADMIN_ID:
        return True
    user = get_user(user_id)
    return user.get('is_admin', 0) == 1 if user else False

def is_banned(user_id: int) -> bool:
    user = get_user(user_id)
    return user.get('is_banned', 0) == 1 if user else False

def add_user(user_id: int, username: str, first_name: str) -> Dict:
    c = db.cursor()
    existing = get_user(user_id)
    if not existing:
        referral_code = f"HAM{user_id}{random.randint(10000, 99999)}"
        join_date = datetime.datetime.now().isoformat()
        is_admin_val = 1 if user_id == MASTER_ADMIN_ID else 0
        c.execute("INSERT INTO users (user_id, username, first_name, referral_code, join_date, last_active, is_admin) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (user_id, username, first_name, referral_code, join_date, join_date, is_admin_val))
        db.commit()
        return get_user(user_id)
    c.execute("UPDATE users SET last_active = ?, username = ? WHERE user_id = ?", (datetime.datetime.now().isoformat(), username, user_id))
    db.commit()
    return get_user(user_id)

def update_wallet(user_id: int, amount: float) -> float:
    c = db.cursor()
    c.execute("UPDATE users SET wallet_balance = wallet_balance + ? WHERE user_id = ?", (amount, user_id))
    c.execute("SELECT wallet_balance FROM users WHERE user_id = ?", (user_id,))
    balance = c.fetchone()[0]
    db.commit()
    return balance

def get_wallet(user_id: int) -> float:
    user = get_user(user_id)
    return user.get('wallet_balance', 0) if user else 0

def add_transaction(user_id: int, amount: float, txn_type: str, reference: str, status: str = 'completed', processed_by: int = None) -> str:
    c = db.cursor()
    txn_id = f"TXN{user_id}{int(time.time())}{random.randint(1000, 9999)}"
    timestamp = datetime.datetime.now().isoformat()
    c.execute("INSERT INTO transactions (txn_id, user_id, amount, type, reference, status, timestamp, processed_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (txn_id, user_id, amount, txn_type, reference, status, timestamp, processed_by))
    db.commit()
    return txn_id

def add_notification(user_id: int, title: str, message: str):
    c = db.cursor()
    c.execute("INSERT INTO notifications (user_id, title, message, created_date) VALUES (?, ?, ?, ?)",
              (user_id, title, message, datetime.datetime.now().isoformat()))
    db.commit()

def process_referral(user_id: int):
    user = get_user(user_id)
    if not user or not user.get('referred_by'):
        return
    referrer_id = user['referred_by']
    bonus = int(get_setting('referral_bonus', '250'))
    update_wallet(referrer_id, bonus)
    add_transaction(referrer_id, bonus, 'referral_bonus', f'ref_{user_id}', 'completed')
    c = db.cursor()
    c.execute("UPDATE users SET total_referrals = total_referrals + 1, referral_earnings = referral_earnings + ? WHERE user_id = ?", (bonus, referrer_id))
    db.commit()
    try:
        bot.send_message(referrer_id, f"🎉 REFERRAL BONUS!\n\n💰 +₦{bonus:,.2f} added to your wallet.", parse_mode='HTML')
    except:
        pass

def get_admin_wallet():
    c = db.cursor()
    c.execute("SELECT balance, total_earned, total_withdrawn FROM admin_wallet WHERE id = 1")
    row = c.fetchone()
    return {'balance': row[0], 'total_earned': row[1], 'total_withdrawn': row[2]} if row else {'balance': 0, 'total_earned': 0, 'total_withdrawn': 0}

def update_admin_wallet(amount: float, is_earning: bool = True):
    c = db.cursor()
    if is_earning:
        c.execute("UPDATE admin_wallet SET balance = balance + ?, total_earned = total_earned + ?, last_updated = ? WHERE id = 1", (amount, amount, datetime.datetime.now().isoformat()))
    else:
        c.execute("UPDATE admin_wallet SET balance = balance - ?, total_withdrawn = total_withdrawn + ?, last_updated = ? WHERE id = 1", (amount, amount, datetime.datetime.now().isoformat()))
    db.commit()

def create_order(user_id: int, product_type: str, product_name: str, quantity: int, amount: float, delivery_info: str) -> str:
    c = db.cursor()
    order_id = f"ORD{user_id}{int(time.time())}{random.randint(100, 999)}"
    order_date = datetime.datetime.now().isoformat()
    c.execute("INSERT INTO orders (order_id, user_id, product_type, product_name, quantity, amount, delivery_info, order_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (order_id, user_id, product_type, product_name, quantity, amount, delivery_info, order_date))
    c.execute("UPDATE users SET total_spent = total_spent + ?, total_orders = total_orders + 1 WHERE user_id = ?", (amount, user_id))
    db.commit()
    return order_id

def get_user_orders(user_id: int, limit: int = 20) -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT order_id, product_name, quantity, amount, order_date FROM orders WHERE user_id = ? ORDER BY order_date DESC LIMIT ?", (user_id, limit))
    return [dict(row) for row in c.fetchall()]

def get_user_transactions(user_id: int, limit: int = 15) -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT txn_id, amount, type, status, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
    return [dict(row) for row in c.fetchall()]

def get_user_referral_stats(user_id: int) -> Tuple[int, float]:
    user = get_user(user_id)
    if user:
        return user.get('total_referrals', 0), user.get('referral_earnings', 0)
    return 0, 0.0

def get_referral_leaderboard(limit: int = 10) -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT user_id, first_name, total_referrals, referral_earnings FROM users WHERE total_referrals > 0 ORDER BY total_referrals DESC LIMIT ?", (limit,))
    return [dict(row) for row in c.fetchall()]

def get_all_users(limit: int = 100) -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT user_id, username, first_name, wallet_balance, total_spent, total_orders, join_date, is_banned, is_admin FROM users ORDER BY join_date DESC LIMIT ?", (limit,))
    return [dict(row) for row in c.fetchall()]

def get_all_admins() -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT user_id, username, first_name FROM users WHERE is_admin = 1")
    return [dict(row) for row in c.fetchall()]

def ban_user(user_id: int):
    c = db.cursor()
    c.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    db.commit()
    try:
        bot.send_message(user_id, "🚫 YOU HAVE BEEN BANNED!\nContact admin for support.", parse_mode='HTML')
    except:
        pass

def unban_user(user_id: int):
    c = db.cursor()
    c.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    db.commit()
    try:
        bot.send_message(user_id, "✅ YOU HAVE BEEN UNBANNED!\nYou can now use the bot.", parse_mode='HTML')
    except:
        pass

def grant_admin(user_id: int):
    c = db.cursor()
    c.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
    db.commit()

def revoke_admin(user_id: int):
    if user_id == MASTER_ADMIN_ID:
        return False
    c = db.cursor()
    c.execute("UPDATE users SET is_admin = 0 WHERE user_id = ?", (user_id,))
    db.commit()
    return True
def mask_email(email: str) -> str:
    """Hide part of email for privacy"""
    if '@' not in email:
        return email
    local, domain = email.split('@')
    if len(local) <= 2:
        masked_local = local[0] + '*' * (len(local) - 1)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"

def get_bot_stats() -> Dict:
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1")
    banned_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
    admin_users = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(amount), 0) FROM orders")
    total_sales = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders")
    total_orders = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM email_stock WHERE status = 'available'")
    email_stock = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ig_stock WHERE status = 'available'")
    ig_stock = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM bulk_stock WHERE status = 'available'")
    bulk_stock = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ig_shop_stock WHERE status = 'available'")
    ig_shop_stock = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM fb_stock WHERE status = 'available'")
    fb_stock = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM payments WHERE status = 'pending'")
    pending_payments = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM withdrawals WHERE status = 'pending'")
    pending_withdrawals = c.fetchone()[0]
    today = datetime.date.today().isoformat()
    c.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE date(timestamp) = ? AND type = 'deposit' AND status = 'completed'", (today,))
    deposits_today = c.fetchone()[0]
    return {
        'total_users': total_users, 'banned_users': banned_users, 'admin_users': admin_users,
        'total_sales': total_sales, 'total_orders': total_orders,
        'email_stock': email_stock, 'ig_stock': ig_stock, 'bulk_stock': bulk_stock,
        'ig_shop_stock': ig_shop_stock, 'fb_stock': fb_stock,
        'pending_payments': pending_payments, 'pending_withdrawals': pending_withdrawals, 'deposits_today': deposits_today
    }

def create_withdrawal(user_id: int, amount: float, bank: str, account: str, name: str) -> str:
    c = db.cursor()
    withdraw_id = f"WDR{user_id}{int(time.time())}{random.randint(100, 999)}"
    c.execute("INSERT INTO withdrawals (withdraw_id, user_id, amount, bank_name, account_number, account_name, request_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (withdraw_id, user_id, amount, bank, account, name, datetime.datetime.now().isoformat()))
    db.commit()
    return withdraw_id

def get_pending_withdrawals() -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT withdraw_id, user_id, amount, bank_name, account_number, account_name, request_date FROM withdrawals WHERE status = 'pending' ORDER BY request_date DESC")
    return [dict(row) for row in c.fetchall()]

def complete_withdrawal(withdraw_id: str, admin_id: int):
    c = db.cursor()
    c.execute("UPDATE withdrawals SET status = 'completed', processed_date = ?, processed_by = ? WHERE withdraw_id = ?",
              (datetime.datetime.now().isoformat(), admin_id, withdraw_id))
    db.commit()
    c.execute("SELECT user_id FROM withdrawals WHERE withdraw_id = ?", (withdraw_id,))
    row = c.fetchone()
    if row:
        try:
            bot.send_message(row[0], "✅ WITHDRAWAL COMPLETED!\n\nYour withdrawal has been processed.", parse_mode='HTML')
        except:
            pass

def create_payment(user_id: int, amount: float, method: str, reference: str, image_file_id: str = None) -> str:
    c = db.cursor()
    payment_id = f"PAY{user_id}{int(time.time())}{random.randint(1000, 9999)}"
    c.execute("INSERT INTO payments (payment_id, user_id, amount, method, reference, image_file_id, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)",
              (payment_id, user_id, amount, method, reference, image_file_id, datetime.datetime.now().isoformat()))
    db.commit()
    return payment_id

def get_pending_payments() -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT payment_id, user_id, amount, method, reference, image_file_id, timestamp FROM payments WHERE status = 'pending' ORDER BY timestamp ASC")
    return [dict(row) for row in c.fetchall()]

def confirm_payment(payment_id: str, admin_id: int) -> Tuple[bool, int, float]:
    c = db.cursor()
    c.execute("SELECT user_id, amount FROM payments WHERE payment_id = ? AND status = 'pending'", (payment_id,))
    result = c.fetchone()
    if not result:
        return False, None, None
    user_id, amount = result
    c.execute("UPDATE payments SET status = 'completed', processed_by = ?, processed_date = ? WHERE payment_id = ?",
              (admin_id, datetime.datetime.now().isoformat(), payment_id))
    update_wallet(user_id, amount)
    add_transaction(user_id, amount, 'deposit', payment_id, 'completed', admin_id)
    update_admin_wallet(amount, True)
    db.commit()
    return True, user_id, amount

def reject_payment(payment_id: str, admin_id: int):
    c = db.cursor()
    c.execute("UPDATE payments SET status = 'rejected', processed_by = ?, processed_date = ? WHERE payment_id = ?",
              (admin_id, datetime.datetime.now().isoformat(), payment_id))
    db.commit()
    c.execute("SELECT user_id FROM payments WHERE payment_id = ?", (payment_id,))
    row = c.fetchone()
    if row:
        try:
            bot.send_message(row[0], "❌ PAYMENT REJECTED!\n\nYour payment was rejected. Please submit a clear screenshot.", parse_mode='HTML')
        except:
            pass
# =================================================================================
# AUTO-POST COMMANDS
# =================================================================================

@bot.message_handler(commands=['autoposton'])
def cmd_auto_post_on(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "🚫 ADMIN ONLY!", parse_mode='HTML')
        return
    
    c = db.cursor()
    c.execute("UPDATE bot_settings SET setting_value = 'True' WHERE setting_key = 'auto_post_enabled'")
    db.commit()
    bot.reply_to(message, "✅ **AUTO-POST ENABLED!**\n\nBot will post stock updates at scheduled times.", parse_mode='HTML')

@bot.message_handler(commands=['autopostoff'])
def cmd_auto_post_off(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "🚫 ADMIN ONLY!", parse_mode='HTML')
        return
    
    c = db.cursor()
    c.execute("UPDATE bot_settings SET setting_value = 'False' WHERE setting_key = 'auto_post_enabled'")
    db.commit()
    bot.reply_to(message, "❌ **AUTO-POST DISABLED!**\n\nBot will NOT post stock updates.\n\nUse /autoposton to enable again.", parse_mode='HTML')

@bot.message_handler(commands=['setposttime'])
def cmd_set_post_time(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "🚫 ADMIN ONLY!", parse_mode='HTML')
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "📝 **USAGE:**\n\n`/setposttime 07:00` - Post once daily\n`/setposttime 07:00 19:00` - Post twice daily", parse_mode='HTML')
        return
    
    c = db.cursor()
    
    # Validate first time
    if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', parts[1]):
        bot.reply_to(message, "❌ Invalid time! Use 24-hour format: 07:00, 14:30, 19:00", parse_mode='HTML')
        return
    
    c.execute("UPDATE bot_settings SET setting_value = ? WHERE setting_key = 'auto_post_time'", (parts[1],))
    
    if len(parts) >= 3:
        if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', parts[2]):
            bot.reply_to(message, "❌ Invalid second time!", parse_mode='HTML')
            return
        c.execute("UPDATE bot_settings SET setting_value = ? WHERE setting_key = 'auto_post_time2'", (parts[2],))
        db.commit()
        bot.reply_to(message, f"✅ **TIMES SET!**\n\n📅 First post: {parts[1]}\n📅 Second post: {parts[2]}", parse_mode='HTML')
    else:
        c.execute("UPDATE bot_settings SET setting_value = '' WHERE setting_key = 'auto_post_time2'")
        db.commit()
        bot.reply_to(message, f"✅ **TIME SET!**\n\n📅 Daily post at: {parts[1]}", parse_mode='HTML')

@bot.message_handler(commands=['showposttime'])
def cmd_show_post_time(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "🚫 ADMIN ONLY!", parse_mode='HTML')
        return
    
    c = db.cursor()
    c.execute("SELECT setting_value FROM bot_settings WHERE setting_key = 'auto_post_time'")
    time1 = c.fetchone()
    time1 = time1[0] if time1 else "07:00"
    
    c.execute("SELECT setting_value FROM bot_settings WHERE setting_key = 'auto_post_time2'")
    time2 = c.fetchone()
    time2 = time2[0] if time2 and time2[0] else "Not set"
    
    c.execute("SELECT setting_value FROM bot_settings WHERE setting_key = 'auto_post_enabled'")
    enabled = c.fetchone()
    status = "✅ ENABLED" if (enabled and enabled[0] == 'True') else "❌ DISABLED"
    
    bot.reply_to(message, f"⚙️ **AUTO-POST SETTINGS**\n\nStatus: {status}\nFirst post: {time1}\nSecond post: {time2}\n\nCommands:\n/autoposton - Enable\n/autopostoff - Disable\n/setposttime - Change time\n/showposttime - Show settings", parse_mode='HTML')

# =================================================================================
# PRICING ENGINE
# =================================================================================

class PricingEngine:
    @staticmethod
    def get_all_rules(active_only: bool = True) -> List[Dict]:
        c = db.cursor()
        if active_only:
            c.execute("SELECT * FROM pricing_rules WHERE is_active = 1 ORDER BY priority DESC, min_value ASC")
        else:
            c.execute("SELECT * FROM pricing_rules ORDER BY priority DESC, min_value ASC")
        return [dict(row) for row in c.fetchall()]
    
    @staticmethod
    def get_price(followers: int) -> Tuple[float, str]:
        rules = PricingEngine.get_all_rules(active_only=True)
        for rule in rules:
            rule_type = rule['rule_type']
            min_val = rule['min_value']
            max_val = rule.get('max_value')
            price = rule['price']
            if rule_type == 'single' and followers == min_val:
                return price, rule['rule_name']
            elif rule_type == 'range' and min_val <= followers <= (max_val if max_val else followers):
                return price, rule['rule_name']
            elif rule_type == 'min' and followers >= min_val:
                return price, rule['rule_name']
        return followers * 10, "Default"
    
    @staticmethod
    def add_rule(rule_name: str, rule_type: str, min_val: int, max_val: int, price: float, admin_id: int) -> bool:
        c = db.cursor()
        try:
            c.execute('''INSERT INTO pricing_rules 
                        (rule_name, rule_type, min_value, max_value, price, created_by, created_date) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (rule_name, rule_type, min_val, max_val if max_val > 0 else None, price, admin_id, datetime.datetime.now().isoformat()))
            db.commit()
            return True
        except:
            return False
    
    @staticmethod
    def update_rule_price(rule_id: int, new_price: float, admin_id: int) -> bool:
        c = db.cursor()
        c.execute("UPDATE pricing_rules SET price = ? WHERE id = ?", (new_price, rule_id))
        db.commit()
        return True
    
    @staticmethod
    def delete_rule(rule_id: int) -> bool:
        c = db.cursor()
        c.execute("DELETE FROM pricing_rules WHERE id = ?", (rule_id,))
        db.commit()
        return True
    
    @staticmethod
    def delete_all_rules() -> bool:
        c = db.cursor()
        c.execute("DELETE FROM pricing_rules")
        db.commit()
        return True
    
    @staticmethod
    def get_price_for_display() -> str:
        rules = PricingEngine.get_all_rules(active_only=True)
        symbol = get_setting('currency_symbol', '₦')
        range_rules = [r for r in rules if r['rule_type'] == 'range']
        min_rules = [r for r in rules if r['rule_type'] == 'min']
        single_rules = [r for r in rules if r['rule_type'] == 'single']
        lines = []
        if range_rules:
            lines.append("━━━━━━━━━━━━ RANGE PRICES ━━━━━━━━━━━━")
            for r in range_rules:
                if r['max_value'] and r['max_value'] < 9999:
                    lines.append(f"📸 {r['min_value']}-{r['max_value']} followers → {symbol}{r['price']:,.0f}")
                else:
                    lines.append(f"📸 {r['min_value']}+ followers → {symbol}{r['price']:,.0f}")
        if min_rules:
            lines.append("\n━━━━━━━━━━━ MINIMUM PRICES ━━━━━━━━━━━")
            for r in sorted(min_rules, key=lambda x: x['min_value']):
                lines.append(f"📸 {r['min_value']}+ followers → {symbol}{r['price']:,.0f}")
        if single_rules:
            lines.append("\n━━━━━━━━━━━ EXACT PRICES ━━━━━━━━━━━")
            for r in sorted(single_rules, key=lambda x: x['min_value']):
                lines.append(f"📸 {r['min_value']} followers → {symbol}{r['price']:,.0f}")
        return "\n".join(lines)

# =================================================================================
# IG SHOP PRICING
# =================================================================================

class IGShopPricing:
    @staticmethod
    def get_all_prices(active_only: bool = True) -> List[Dict]:
        c = db.cursor()
        if active_only:
            c.execute("SELECT * FROM ig_shop_pricing WHERE is_active = 1 ORDER BY sort_order, price")
        else:
            c.execute("SELECT * FROM ig_shop_pricing ORDER BY sort_order, price")
        return [dict(row) for row in c.fetchall()]
    
    @staticmethod
    def add_price(rule_name: str, price: float, description: str, admin_id: int) -> bool:
        c = db.cursor()
        try:
            c.execute('''INSERT INTO ig_shop_pricing 
                        (rule_name, price, description, created_by, created_date) 
                        VALUES (?, ?, ?, ?, ?)''',
                      (rule_name, price, description, admin_id, datetime.datetime.now().isoformat()))
            db.commit()
            return True
        except:
            return False
    
    @staticmethod
    def update_price(price_id: int, new_price: float, admin_id: int) -> bool:
        c = db.cursor()
        c.execute("UPDATE ig_shop_pricing SET price = ? WHERE id = ?", (new_price, price_id))
        db.commit()
        return True
    
    @staticmethod
    def delete_price(price_id: int) -> bool:
        c = db.cursor()
        c.execute("DELETE FROM ig_shop_pricing WHERE id = ?", (price_id,))
        db.commit()
        return True
    
    @staticmethod
    def delete_all_prices() -> bool:
        c = db.cursor()
        c.execute("DELETE FROM ig_shop_pricing")
        db.commit()
        return True
    
    @staticmethod
    def get_price_for_display() -> str:
        prices = IGShopPricing.get_all_prices(active_only=True)
        symbol = get_setting('currency_symbol', '₦')
        lines = ["━━━━━━━━━ COMPLETE IG ACCOUNTS ━━━━━━━━━"]
        for p in prices:
            lines.append(f"🎁 {p['rule_name']}: {symbol}{p['price']:,.0f}")
            if p['description']:
                lines.append(f"   📝 {p['description']}")
        return "\n".join(lines)

# =================================================================================
# IG SHOP STOCK
# =================================================================================

class IGShopStock:
    @staticmethod
    def add_item(product_name: str, username: str, password: str, email: str, email_password: str, 
                 followers: int, price: float, screenshot_file_id: str, description: str, admin_id: int) -> bool:
        c = db.cursor()
        try:
            c.execute('''INSERT INTO ig_shop_stock 
                        (product_name, username, password, email, email_password, followers_count, price, 
                         screenshot_file_id, description, added_by, added_date, status) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'available')''',
                      (product_name, username, password, email, email_password, followers, price, 
                       screenshot_file_id, description, admin_id, datetime.datetime.now().isoformat()))
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding IG shop item: {e}")
            return False
    
    @staticmethod
    def get_available_items() -> List[Dict]:
        c = db.cursor()
        c.execute("SELECT id, product_name, username, followers_count, price, screenshot_file_id, description FROM ig_shop_stock WHERE status = 'available' ORDER BY id DESC")
        return [dict(row) for row in c.fetchall()]
    
    @staticmethod
    def get_item_by_id(item_id: int) -> Optional[Dict]:
        c = db.cursor()
        c.execute("SELECT * FROM ig_shop_stock WHERE id = ?", (item_id,))
        row = c.fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def mark_sold(item_id: int, user_id: int) -> bool:
        c = db.cursor()
        c.execute("UPDATE ig_shop_stock SET status = 'sold', sold_date = ?, sold_to = ? WHERE id = ?",
                  (datetime.datetime.now().isoformat(), user_id, item_id))
        db.commit()
        return True
    
    @staticmethod
    def get_all_stock() -> List[Dict]:
        c = db.cursor()
        c.execute("SELECT id, product_name, username, followers_count, price, status, sold_to FROM ig_shop_stock ORDER BY id DESC")
        return [dict(row) for row in c.fetchall()]
    
    @staticmethod
    def delete_item(item_id: int) -> bool:
        c = db.cursor()
        c.execute("DELETE FROM ig_shop_stock WHERE id = ?", (item_id,))
        db.commit()
        return True
    
    @staticmethod
    def delete_all_stock() -> bool:
        c = db.cursor()
        c.execute("DELETE FROM ig_shop_stock")
        db.commit()
        return True

# =================================================================================
# IG SHOP ORDERS
# =================================================================================

class IGShopOrder:
    @staticmethod
    def create_order(user_id: int, product_id: int, product_name: str, amount: float) -> str:
        c = db.cursor()
        order_id = f"IGORD{user_id}{int(time.time())}{random.randint(100, 999)}"
        c.execute('''INSERT INTO ig_shop_orders 
                    (order_id, user_id, product_id, product_name, amount, order_date) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                  (order_id, user_id, product_id, product_name, amount, datetime.datetime.now().isoformat()))
        db.commit()
        return order_id
    
    @staticmethod
    def get_user_orders(user_id: int) -> List[Dict]:
        c = db.cursor()
        c.execute("SELECT order_id, product_name, amount, status, order_date FROM ig_shop_orders WHERE user_id = ? ORDER BY order_date DESC", (user_id,))
        return [dict(row) for row in c.fetchall()]
    
    @staticmethod
    def get_order_by_id(order_id: str) -> Optional[Dict]:
        c = db.cursor()
        c.execute("SELECT * FROM ig_shop_orders WHERE order_id = ?", (order_id,))
        row = c.fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def mark_delivered(order_id: str) -> bool:
        c = db.cursor()
        c.execute("UPDATE ig_shop_orders SET status = 'delivered', delivered_date = ? WHERE order_id = ?",
                  (datetime.datetime.now().isoformat(), order_id))
        db.commit()
        return True

# =================================================================================
# CODE REQUEST MANAGER
# =================================================================================

class CodeRequestManager:
    @staticmethod
    def create_request(user_id: int, order_id: str) -> str:
        c = db.cursor()
        c.execute('''INSERT INTO code_requests (user_id, order_id, request_date, status) 
                    VALUES (?, ?, ?, 'pending')''',
                  (user_id, order_id, datetime.datetime.now().isoformat()))
        db.commit()
        return "Request created"
    
    @staticmethod
    def get_pending_requests() -> List[Dict]:
        c = db.cursor()
        c.execute("SELECT id, user_id, order_id, request_date FROM code_requests WHERE status = 'pending' ORDER BY request_date ASC")
        return [dict(row) for row in c.fetchall()]
    
    @staticmethod
    def provide_code(request_id: int, code: str, admin_id: int) -> bool:
        c = db.cursor()
        c.execute("UPDATE code_requests SET status = 'completed', code = ?, processed_by = ?, processed_date = ? WHERE id = ?",
                  (code, admin_id, datetime.datetime.now().isoformat(), request_id))
        db.commit()
        c.execute("SELECT user_id FROM code_requests WHERE id = ?", (request_id,))
        row = c.fetchone()
        return row[0] if row else None

# =================================================================================
# EMAIL STOCK FUNCTIONS
# =================================================================================

def add_email_only(email: str, followers: int, price: float, admin_id: int) -> bool:
    username = email.split('@')[0]
    c = db.cursor()
    try:
        c.execute("INSERT INTO email_stock (email, username, password, has_password, followers_count, price, added_by, added_date, status) VALUES (?, ?, ?, 0, ?, ?, ?, ?, 'available')",
                  (email, username, None, followers, price, admin_id, datetime.datetime.now().isoformat()))
        db.commit()
        return True
    except:
        return False

def add_email_with_password(email: str, password: str, followers: int, price: float, admin_id: int) -> bool:
    username = email.split('@')[0]
    c = db.cursor()
    try:
        c.execute("INSERT INTO email_stock (email, username, password, has_password, followers_count, price, added_by, added_date, status) VALUES (?, ?, ?, 1, ?, ?, ?, ?, 'available')",
                  (email, username, password, followers, price, admin_id, datetime.datetime.now().isoformat()))
        db.commit()
        return True
    except:
        return False

def get_available_email(followers: int, require_password: bool = False) -> Optional[Dict]:
    c = db.cursor()
    if require_password:
        c.execute("SELECT id, email, username, password, has_password, price FROM email_stock WHERE followers_count = ? AND has_password = 1 AND status = 'available' LIMIT 1", (followers,))
    else:
        c.execute("SELECT id, email, username, password, has_password, price FROM email_stock WHERE followers_count = ? AND status = 'available' LIMIT 1", (followers,))
    row = c.fetchone()
    return dict(row) if row else None

def mark_email_sold(email_id: int, user_id: int):
    c = db.cursor()
    c.execute("UPDATE email_stock SET status = 'sold', sold_date = ?, sold_to = ? WHERE id = ?",
              (datetime.datetime.now().isoformat(), user_id, email_id))
    db.commit()

def get_email_stock_count_with_pass(followers: int, require_password: bool = False) -> int:
    c = db.cursor()
    if require_password:
        c.execute("SELECT COUNT(*) FROM email_stock WHERE followers_count = ? AND has_password = 1 AND status = 'available'", (followers,))
    else:
        c.execute("SELECT COUNT(*) FROM email_stock WHERE followers_count = ? AND status = 'available'", (followers,))
    return c.fetchone()[0]

def get_all_email_stock() -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT id, email, username, has_password, followers_count, price, status FROM email_stock ORDER BY id DESC")
    return [dict(row) for row in c.fetchall()]

def delete_email_stock(stock_id: int):
    c = db.cursor()
    c.execute("DELETE FROM email_stock WHERE id = ?", (stock_id,))
    db.commit()

def delete_all_email_stock():
    c = db.cursor()
    c.execute("DELETE FROM email_stock")
    db.commit()

def get_email_stock_count(followers: int) -> int:
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM email_stock WHERE followers_count = ? AND status = 'available'", (followers,))
    return c.fetchone()[0]

def get_ig_stock_count(followers: int) -> int:
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM ig_stock WHERE followers_count = ? AND status = 'available'", (followers,))
    return c.fetchone()[0]

def get_bulk_stock_count(followers_per_email: int) -> int:
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM bulk_stock WHERE followers_per_email = ? AND status = 'available'", (followers_per_email,))
    return c.fetchone()[0]
# =================================================================================
# IG STOCK FUNCTIONS
# =================================================================================

def add_ig_only(username: str, followers: int, price: float, admin_id: int) -> bool:
    c = db.cursor()
    try:
        c.execute("INSERT INTO ig_stock (ig_username, password, has_password, followers_count, price, added_by, added_date, status) VALUES (?, ?, 0, ?, ?, ?, ?, 'available')",
                  (username, None, followers, price, admin_id, datetime.datetime.now().isoformat()))
        db.commit()
        return True
    except:
        return False

def add_ig_with_password(username: str, password: str, followers: int, price: float, admin_id: int) -> bool:
    c = db.cursor()
    try:
        c.execute("INSERT INTO ig_stock (ig_username, password, has_password, followers_count, price, added_by, added_date, status) VALUES (?, ?, 1, ?, ?, ?, ?, 'available')",
                  (username, password, followers, price, admin_id, datetime.datetime.now().isoformat()))
        db.commit()
        return True
    except:
        return False

def get_available_ig(followers: int, require_password: bool = False) -> Optional[Dict]:
    c = db.cursor()
    if require_password:
        c.execute("SELECT id, ig_username, password, has_password, price FROM ig_stock WHERE followers_count = ? AND has_password = 1 AND status = 'available' LIMIT 1", (followers,))
    else:
        c.execute("SELECT id, ig_username, password, has_password, price FROM ig_stock WHERE followers_count = ? AND status = 'available' LIMIT 1", (followers,))
    row = c.fetchone()
    return dict(row) if row else None

def mark_ig_sold(ig_id: int, user_id: int):
    c = db.cursor()
    c.execute("UPDATE ig_stock SET status = 'sold', sold_date = ?, sold_to = ? WHERE id = ?",
              (datetime.datetime.now().isoformat(), user_id, ig_id))
    db.commit()

def get_ig_stock_count(followers: int, require_password: bool = False) -> int:
    c = db.cursor()
    if require_password:
        c.execute("SELECT COUNT(*) FROM ig_stock WHERE followers_count = ? AND has_password = 1 AND status = 'available'", (followers,))
    else:
        c.execute("SELECT COUNT(*) FROM ig_stock WHERE followers_count = ? AND status = 'available'", (followers,))
    return c.fetchone()[0]

def get_all_ig_stock() -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT id, ig_username, has_password, followers_count, price, status FROM ig_stock ORDER BY id DESC")
    return [dict(row) for row in c.fetchall()]

def delete_ig_stock(stock_id: int):
    c = db.cursor()
    c.execute("DELETE FROM ig_stock WHERE id = ?", (stock_id,))
    db.commit()

def delete_all_ig_stock():
    c = db.cursor()
    c.execute("DELETE FROM ig_stock")
    db.commit()

# =================================================================================
# BULK STOCK FUNCTIONS
# =================================================================================

def add_bulk_stock(emails: str, emails_count: int, followers_per_email: int, total_followers: int, price: float, admin_id: int) -> bool:
    c = db.cursor()
    c.execute("INSERT INTO bulk_stock (emails, emails_count, followers_per_email, total_followers, price, added_by, added_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'available')",
              (emails, emails_count, followers_per_email, total_followers, price, admin_id, datetime.datetime.now().isoformat()))
    db.commit()
    return True

def get_available_bulk(followers_per_email: int) -> Optional[Dict]:
    c = db.cursor()
    c.execute("SELECT id, emails, emails_count, total_followers, price FROM bulk_stock WHERE followers_per_email = ? AND status = 'available' LIMIT 1", (followers_per_email,))
    row = c.fetchone()
    return dict(row) if row else None

def mark_bulk_sold(bulk_id: int, user_id: int):
    c = db.cursor()
    c.execute("UPDATE bulk_stock SET status = 'sold', sold_date = ?, sold_to = ? WHERE id = ?",
              (datetime.datetime.now().isoformat(), user_id, bulk_id))
    db.commit()

def get_bulk_stock_count(followers_per_email: int) -> int:
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM bulk_stock WHERE followers_per_email = ? AND status = 'available'", (followers_per_email,))
    return c.fetchone()[0]

def get_all_bulk_stock() -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT id, emails_count, followers_per_email, total_followers, price, status FROM bulk_stock ORDER BY id DESC")
    return [dict(row) for row in c.fetchall()]

def delete_bulk_stock(stock_id: int):
    c = db.cursor()
    c.execute("DELETE FROM bulk_stock WHERE id = ?", (stock_id,))
    db.commit()

def delete_all_bulk_stock():
    c = db.cursor()
    c.execute("DELETE FROM bulk_stock")
    db.commit()

def create_bulk_order(user_id: int, followers_per_email: int, total_emails: int, total_followers: int, total_price: float, emails: str) -> str:
    c = db.cursor()
    order_id = f"BULK{user_id}{int(time.time())}{random.randint(100, 999)}"
    order_date = datetime.datetime.now().isoformat()
    c.execute("INSERT INTO bulk_orders (order_id, user_id, followers_per_email, total_emails, total_followers, amount, emails, order_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (order_id, user_id, followers_per_email, total_emails, total_followers, total_price, emails, order_date))
    c.execute("UPDATE users SET total_spent = total_spent + ?, total_orders = total_orders + 1 WHERE user_id = ?", (total_price, user_id))
    db.commit()
    return order_id

def get_user_bulk_orders(user_id: int, limit: int = 20) -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT order_id, followers_per_email, total_emails, total_followers, amount, order_date FROM bulk_orders WHERE user_id = ? ORDER BY order_date DESC LIMIT ?", (user_id, limit))
    return [dict(row) for row in c.fetchall()]

# =================================================================================
# FB FUNCTIONS
# =================================================================================

def get_all_fb_categories() -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT * FROM fb_categories WHERE is_active = 1 ORDER BY sort_order")
    return [dict(row) for row in c.fetchall()]

def get_fb_category_by_id(cat_id: int) -> Optional[Dict]:
    c = db.cursor()
    c.execute("SELECT * FROM fb_categories WHERE id = ?", (cat_id,))
    row = c.fetchone()
    return dict(row) if row else None

def add_fb_category(name: str, display_name: str, price: float, has_page: int = 0, description: str = None) -> bool:
    c = db.cursor()
    try:
        c.execute("INSERT INTO fb_categories (name, display_name, price, has_page, description, is_active, sort_order, created_date) VALUES (?, ?, ?, ?, ?, 1, (SELECT COALESCE(MAX(sort_order), 0) + 1 FROM fb_categories), ?)",
                  (name, display_name, price, has_page, description or display_name, datetime.datetime.now().isoformat()))
        db.commit()
        return True
    except:
        return False

def get_fb_stock_count(category_id: int = None) -> int:
    c = db.cursor()
    if category_id:
        c.execute("SELECT COUNT(*) FROM fb_stock WHERE category_id = ? AND status = 'available'", (category_id,))
    else:
        c.execute("SELECT COUNT(*) FROM fb_stock WHERE status = 'available'")
    return c.fetchone()[0]

def get_available_fb_account(category_id: int) -> Optional[Dict]:
    c = db.cursor()
    c.execute("SELECT id, email, password, account_age, price FROM fb_stock WHERE category_id = ? AND status = 'available' LIMIT 1", (category_id,))
    row = c.fetchone()
    return dict(row) if row else None

def add_fb_stock(email: str, password: str, category_id: int, account_age: str, screenshot_ids: str = None, price: float = None, admin_id: int = None) -> bool:
    c = db.cursor()
    if price is None:
        cat = get_fb_category_by_id(category_id)
        price = cat['price'] if cat else 0
    try:
        c.execute("INSERT INTO fb_stock (email, password, category_id, account_age, has_screenshot, screenshot_file_ids, price, added_by, added_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'available')",
                  (email, password, category_id, account_age, 1 if screenshot_ids else 0, screenshot_ids, price, admin_id, datetime.datetime.now().isoformat()))
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error adding FB stock: {e}")
        return False

def get_all_fb_stock() -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT fs.*, fc.display_name as category_name FROM fb_stock fs LEFT JOIN fb_categories fc ON fs.category_id = fc.id WHERE fs.status = 'available' ORDER BY fs.added_date DESC LIMIT 100")
    return [dict(row) for row in c.fetchall()]

def delete_fb_stock(stock_id: int):
    c = db.cursor()
    c.execute("DELETE FROM fb_stock WHERE id = ?", (stock_id,))
    db.commit()

def delete_all_fb_stock():
    c = db.cursor()
    c.execute("DELETE FROM fb_stock")
    db.commit()

def mark_fb_sold(account_id: int, user_id: int):
    c = db.cursor()
    c.execute("UPDATE fb_stock SET status = 'sold', sold_date = ?, sold_to = ? WHERE id = ?",
              (datetime.datetime.now().isoformat(), user_id, account_id))
    db.commit()

# =================================================================================
# AUTO-EXTRACT FUNCTIONS
# =================================================================================

def extract_emails_from_text(text: str) -> List[Dict]:
    results = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        email = None
        password = None
        followers = None
        
        # Check for fancy format with ﴾ ﴿ brackets
        if '﴾' in line or 'EMAIL' in line.upper():
            email_match = re.search(r'EMAIL\s*:\s*﴾\s*([^\s﴾]+)', line, re.IGNORECASE)
            if email_match:
                email = email_match.group(1)
            
            followers_match = re.search(r'FOLLOWERS\s*:\s*﴾\s*(\d+)', line, re.IGNORECASE)
            if followers_match:
                followers = int(followers_match.group(1))
            
            reset_match = re.search(r'RESET\s*:\s*﴾\s*([^\s﴾]+)', line, re.IGNORECASE)
            if reset_match:
                password = reset_match.group(1)
        
        # Check for pipe separator |
        elif '|' in line:
            parts = line.split('|')
            if len(parts) >= 1 and '@' in parts[0]:
                email = parts[0].strip()
            if len(parts) >= 2:
                password = parts[1].strip()
            if len(parts) >= 3 and parts[2].strip().isdigit():
                followers = int(parts[2].strip())
        
        # Check for colon separator :
        elif ':' in line:
            parts = line.split(':')
            if len(parts) >= 1 and '@' in parts[0]:
                email = parts[0].strip()
            if len(parts) >= 2:
                password = parts[1].strip()
            if len(parts) >= 3 and parts[2].strip().isdigit():
                followers = int(parts[2].strip())
        
        # Just try to find email anywhere
        else:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
            if email_match:
                email = email_match.group()
                
                # Try to detect followers from email (e.g., name_500@gmail.com)
                underscore_match = re.search(r'_(\d+)', email)
                if underscore_match:
                    followers = int(underscore_match.group(1))
                else:
                    numbers = re.findall(r'\b(\d+)\b', line)
                    if numbers:
                        for num in numbers:
                            num_int = int(num)
                            if 1 <= num_int <= 1000000:
                                followers = num_int
                                break
        
        if email and re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            results.append({
                'email': email,
                'password': password if password else "",
                'followers': followers
            })
    
    # Remove duplicates
    seen = set()
    unique_results = []
    for item in results:
        if item['email'] not in seen:
            seen.add(item['email'])
            unique_results.append(item)
    
    return unique_results

# =================================================================================
# KEYBOARDS
# =================================================================================

def main_keyboard(user_id: int = None) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if user_id and is_admin(user_id):
        buttons = ["🔧 ADMIN PANEL", "👥 REFERRALS", "🏆 LEADERBOARD", "📜 HISTORY", "🔔 NOTIFICATIONS", "🤖 EXPERT SUPPORT", "❓ HELP"]
    else:
        buttons = ["📧 BUY EMAIL", "📦 BUY BULK", "🎁 BUY COMPLETE IG", "📘 BUY FACEBOOK", "💰 MY WALLET", "💳 FUND WALLET", "📦 MY ORDERS", "📊 MY STATS", "👥 REFERRALS", "🏆 LEADERBOARD", "📜 HISTORY", "🔔 NOTIFICATIONS", "📋 MY PURCHASES", "🤖 EXPERT SUPPORT", "❓ HELP"]
    
    row = []
    for btn in buttons:
        row.append(types.KeyboardButton(btn))
        if len(row) == 2:
            markup.add(*row)
            row = []
    if row:
        markup.add(*row)
    return markup

def admin_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💰 PRICING RULES", callback_data="admin_pricing"),
        types.InlineKeyboardButton("🎁 IG SHOP PRICING", callback_data="admin_ig_pricing"),
        types.InlineKeyboardButton("📘 FB MANAGEMENT", callback_data="admin_fb"),
        types.InlineKeyboardButton("💰 PENDING PAYMENTS", callback_data="admin_payments"),
        types.InlineKeyboardButton("📧 ADD EMAIL", callback_data="stock_add_email"),
        types.InlineKeyboardButton("🔗 ADD IG LINK", callback_data="stock_add_ig"),
        types.InlineKeyboardButton("📦 ADD BULK", callback_data="stock_add_bulk"),
        types.InlineKeyboardButton("🎁 ADD COMPLETE IG", callback_data="stock_add_complete_ig"),
        types.InlineKeyboardButton("📋 VIEW EMAIL", callback_data="stock_view_email"),
        types.InlineKeyboardButton("🔍 VIEW IG", callback_data="stock_view_ig"),
        types.InlineKeyboardButton("📊 VIEW BULK", callback_data="stock_view_bulk"),
        types.InlineKeyboardButton("🎁 VIEW COMPLETE IG", callback_data="stock_view_complete_ig"),
        types.InlineKeyboardButton("🗑 DELETE STOCK", callback_data="stock_delete"),
        types.InlineKeyboardButton("🗑 DELETE ALL STOCK", callback_data="stock_delete_all"),
        types.InlineKeyboardButton("🔐 CODE REQUESTS", callback_data="admin_code_requests"),
        types.InlineKeyboardButton("📢 IMAGE BROADCAST", callback_data="admin_image_broadcast"),  # ← ADD THIS LINE
        types.InlineKeyboardButton("👥 ALL USERS", callback_data="admin_users"),
        types.InlineKeyboardButton("👑 GRANT ADMIN", callback_data="admin_grant"),
        types.InlineKeyboardButton("🔧 REVOKE ADMIN", callback_data="admin_revoke"),
        types.InlineKeyboardButton("📊 STATS", callback_data="admin_stats"),
        types.InlineKeyboardButton("📢 BROADCAST", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("🚫 BAN/UNBAN", callback_data="admin_ban"),
        types.InlineKeyboardButton("💰 WALLET", callback_data="admin_wallet"),
        types.InlineKeyboardButton("📤 WITHDRAWALS", callback_data="admin_withdrawals"),
        types.InlineKeyboardButton("💾 BACKUP", callback_data="admin_backup"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
    )
    return markup

def pricing_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    rules = PricingEngine.get_all_rules(active_only=False)
    for rule in rules:
        status = "✅" if rule['is_active'] else "❌"
        markup.add(
            types.InlineKeyboardButton(f"{status} ✏️ {rule['rule_name']}: ₦{rule['price']:,.0f}", callback_data=f"edit_rule_{rule['id']}"),
            types.InlineKeyboardButton(f"🗑 DEL", callback_data=f"delete_rule_{rule['id']}")
        )
    markup.add(types.InlineKeyboardButton("🔄 DELETE ALL RULES", callback_data="delete_all_rules"))
    markup.add(types.InlineKeyboardButton("➕ ADD NEW RULE", callback_data="add_pricing_rule"))
    markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back"))
    return markup

def ig_pricing_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    prices = IGShopPricing.get_all_prices(active_only=False)
    for price in prices:
        status = "✅" if price['is_active'] else "❌"
        markup.add(
            types.InlineKeyboardButton(f"{status} ✏️ {price['rule_name']}: ₦{price['price']:,.0f}", callback_data=f"edit_ig_price_{price['id']}"),
            types.InlineKeyboardButton(f"🗑 DEL", callback_data=f"delete_ig_price_{price['id']}")
        )
    markup.add(types.InlineKeyboardButton("🔄 DELETE ALL IG PRICES", callback_data="delete_all_ig_prices"))
    markup.add(types.InlineKeyboardButton("➕ ADD NEW IG PRICE", callback_data="add_ig_pricing_rule"))
    markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back"))
    return markup
      
def packages_keyboard(product_type: str) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    symbol = get_setting('currency_symbol', '₦')
    c = db.cursor()
    
    # Get ALL available follower counts from stock (not from pricing rules)
    if product_type == "email":
        c.execute("SELECT followers_count, price, COUNT(*) as cnt FROM email_stock WHERE status = 'available' GROUP BY followers_count ORDER BY followers_count ASC")
    elif product_type == "ig":
        c.execute("SELECT followers_count, price, COUNT(*) as cnt FROM ig_stock WHERE status = 'available' GROUP BY followers_count ORDER BY followers_count ASC")
    elif product_type == "bulk":
        c.execute("SELECT followers_per_email as followers_count, price, COUNT(*) as cnt FROM bulk_stock WHERE status = 'available' GROUP BY followers_per_email ORDER BY followers_per_email ASC")
    else:
        c.execute("SELECT followers_count, price, COUNT(*) as cnt FROM email_stock WHERE status = 'available' GROUP BY followers_count ORDER BY followers_count ASC")
    
    stocks = c.fetchall()
    
    if stocks:
        # Show ALL available follower counts from stock
        for stock in stocks:
            followers = stock['followers_count']
            price = stock['price']
            stock_count = stock['cnt']
            stock_icon = "✅" if stock_count > 0 else "❌"
            
            if product_type == "email":
                display = f"📧 {followers} followers - {symbol}{price:,.0f} [{stock_count} in stock] {stock_icon}"
            elif product_type == "ig":
                display = f"🔗 {followers} followers - {symbol}{price:,.0f} [{stock_count} in stock] {stock_icon}"
            else:
                display = f"📦 {followers} followers/email - {symbol}{price:,.0f} [{stock_count} in stock] {stock_icon}"
            
            markup.add(types.InlineKeyboardButton(display, callback_data=f"buy_{product_type}_{followers}"))
    else:
        # Fallback to pricing rules if no stock exists
        rules = PricingEngine.get_all_rules(active_only=True)
        for rule in rules:
            min_val = rule['min_value']
            price = rule['price']
            display = f"📸 {min_val}+ followers - {symbol}{price:,.0f} [0 in stock] ❌"
            markup.add(types.InlineKeyboardButton(display, callback_data=f"buy_{product_type}_{min_val}"))
    
    markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="back_main"))
    return markup

def ig_type_keyboard(followers: int, price: float) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    ig_only_stock = get_ig_stock_count(followers)
    ig_with_pass_stock = get_ig_stock_count_with_password(followers)
    extra_percent = int(get_setting('ig_password_extra', '30'))
    price_with_pass = price * (1 + extra_percent / 100)
    symbol = get_setting('currency_symbol', '₦')
    
    markup.add(
        types.InlineKeyboardButton(f"🔗 IG Only - {symbol}{price:,.0f} ({ig_only_stock} in stock)", callback_data=f"buy_ig_type_{followers}_{price}_only"),
        types.InlineKeyboardButton(f"🔐 IG + Password - {symbol}{price_with_pass:,.0f} ({ig_with_pass_stock} in stock)", callback_data=f"buy_ig_type_{followers}_{price_with_pass}_withpass"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
    )
    return markup

def get_ig_stock_count_with_password(followers: int) -> int:
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM ig_stock WHERE followers_count = ? AND has_password = 1 AND status = 'available'", (followers,))
    return c.fetchone()[0]

def followers_amount_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    symbol = get_setting('currency_symbol', '₦')
    
    rules = PricingEngine.get_all_rules(active_only=True)
    
    for rule in rules[:8]:
        min_val = rule['min_value']
        price = rule['price']
        markup.add(types.InlineKeyboardButton(f"📸 {min_val}+ followers - {symbol}{price:,.0f}", callback_data=f"followers_preset_{min_val}"))
    
    markup.add(types.InlineKeyboardButton("✏️ CUSTOM AMOUNT", callback_data="followers_custom"))
    markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="back_main"))
    return markup

def get_ig_account_stock_count(followers: int) -> int:
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM ig_stock WHERE followers_count = ? AND status = 'available'", (followers,))
    return c.fetchone()[0]
    
def fb_admin_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📘 ADD FB CATEGORY", callback_data="fb_add_category"),
        types.InlineKeyboardButton("📧 ADD FB ACCOUNT", callback_data="fb_add_account"),
        types.InlineKeyboardButton("📋 VIEW FB STOCK", callback_data="fb_view_stock"),
        types.InlineKeyboardButton("✏️ EDIT FB PRICE", callback_data="fb_edit_price"),
        types.InlineKeyboardButton("🗑 DELETE FB STOCK", callback_data="fb_delete_stock"),
        types.InlineKeyboardButton("🗑 DELETE ALL FB", callback_data="fb_delete_all"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back")
    )
    return markup

def stock_delete_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📧 DELETE EMAIL", callback_data="delete_email_stock"),
        types.InlineKeyboardButton("🔗 DELETE IG", callback_data="delete_ig_stock"),
        types.InlineKeyboardButton("📦 DELETE BULK", callback_data="delete_bulk_stock"),
        types.InlineKeyboardButton("🎁 DELETE COMPLETE IG", callback_data="delete_complete_ig_stock"),
        types.InlineKeyboardButton("📘 DELETE FB", callback_data="delete_fb_stock"),
        types.InlineKeyboardButton("🗑 DELETE ALL EMAIL", callback_data="delete_all_email_stock"),
        types.InlineKeyboardButton("🗑 DELETE ALL IG", callback_data="delete_all_ig_stock"),
        types.InlineKeyboardButton("🗑 DELETE ALL BULK", callback_data="delete_all_bulk_stock"),
        types.InlineKeyboardButton("🗑 DELETE ALL COMPLETE IG", callback_data="delete_all_complete_ig_stock"),
        types.InlineKeyboardButton("🗑 DELETE ALL FB", callback_data="delete_all_fb_stock"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back")
    )
    return markup

def view_stock_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📧 VIEW EMAIL STOCK", callback_data="stock_view_email"),
        types.InlineKeyboardButton("🔍 VIEW IG STOCK", callback_data="stock_view_ig"),
        types.InlineKeyboardButton("📊 VIEW BULK STOCK", callback_data="stock_view_bulk"),
        types.InlineKeyboardButton("🎁 VIEW COMPLETE IG", callback_data="stock_view_complete_ig"),
        types.InlineKeyboardButton("📘 VIEW FB STOCK", callback_data="fb_view_stock"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back")
    )
    return markup
# =================================================================================
# MISSING KEYBOARD FUNCTIONS - ADD THESE
# =================================================================================

def complete_ig_keyboard() -> types.InlineKeyboardMarkup:
    items = IGShopStock.get_available_items()
    markup = types.InlineKeyboardMarkup(row_width=1)
    symbol = get_setting('currency_symbol', '₦')
    
    if not items:
        markup.add(types.InlineKeyboardButton("❌ NO COMPLETE IG ACCOUNTS AVAILABLE", callback_data="no_stock"))
        markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="back_main"))
        return markup
    
    for item in items:
        display = f"🎁 {item['product_name']} - {symbol}{item['price']:,.0f}"
        markup.add(types.InlineKeyboardButton(display, callback_data=f"buy_complete_ig_{item['id']}"))
    
    markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="back_main"))
    return markup
    
    total_stock = len(items)
    
    for item in items:
        display = f"🔐 @{item['username']} - {item['followers_count']} followers - {symbol}{item['price']:,.0f} [{total_stock} in stock] ✅"
        markup.add(types.InlineKeyboardButton(display, callback_data=f"view_complete_ig_{item['id']}"))
    
    markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="back_main"))
    return markup

def fb_categories_keyboard(user_id: int = None) -> types.InlineKeyboardMarkup:
    categories = get_all_fb_categories()
    markup = types.InlineKeyboardMarkup(row_width=1)
    symbol = get_setting('currency_symbol', '₦')
    
    user_balance = get_wallet(user_id) if user_id else 0
    
    for cat in categories:
        c = db.cursor()
        c.execute("SELECT COUNT(*) FROM fb_stock WHERE category_id = ? AND status = 'available'", (cat['id'],))
        stock_count = c.fetchone()[0]
        
        stock_icon = "✅" if stock_count > 0 else "❌"
        
        # Show if user can afford
        if user_balance >= cat['price']:
            can_afford = "💰"
        else:
            can_afford = "❌"
        
        display = f"{stock_icon} {cat['display_name']} - {symbol}{cat['price']:,.0f} [{stock_count} in stock] {can_afford}"
        markup.add(types.InlineKeyboardButton(display, callback_data=f"buy_fb_category_{cat['id']}"))
    
    if not categories:
        markup.add(types.InlineKeyboardButton("❌ No categories available", callback_data="back_main"))
    
    markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="back_main"))
    return markup

# =================================================================================
# FIX THE BROKEN buy_email_ CALLBACK - DELETE THIS BLOCK FROM handle_callback
# AND REPLACE WITH THE FIXED VERSION BELOW

# =================================================================================
# COMMAND HANDLERS
# =================================================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "User"
    
    if is_banned(user_id):
        bot.reply_to(message, "🚫 YOU ARE BANNED!\n\nContact admin for support.", parse_mode='HTML')
        return
    
    # Handle referral
    if ' ' in message.text:
        ref_code = message.text.split()[1]
        c = db.cursor()
        c.execute("SELECT user_id FROM users WHERE referral_code = ?", (ref_code,))
        referrer = c.fetchone()
        if referrer and referrer[0] != user_id:
            existing = get_user(user_id)
            if not existing:
                pass
    
    user = add_user(user_id, username, first_name)
    
    if ' ' in message.text and user and not user.get('referred_by'):
        ref_code = message.text.split()[1]
        c = db.cursor()
        c.execute("SELECT user_id FROM users WHERE referral_code = ?", (ref_code,))
        referrer = c.fetchone()
        if referrer and referrer[0] != user_id:
            c.execute("UPDATE users SET referred_by = ? WHERE user_id = ?", (referrer[0], user_id))
            db.commit()
            process_referral(user_id)
    
    symbol = get_setting('currency_symbol', '₦')
    bot_name = get_setting('bot_name', 'Hamzzy Marketplace')
    
    # Generate referral link for the user
    referral_link = f"https://t.me/{BOT_USERNAME}?start={user['referral_code']}"
    bonus = int(get_setting('referral_bonus', '200'))
    
    # Professional welcome message
    msg = f"""
🔥 WELCOME TO HAMZZY LOGS 🔥

✨ Hello {first_name}!

✅ 100% LEGIT & ACTIVE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 REFERRAL PROGRAM

🔗 <code>{referral_link}</code>
🎁 {symbol}{bonus} per referral
💎 after user buy a product your bonus will be added

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Use buttons below to shop

💎 {MY_SIGNATURE}
"""
    bot.reply_to(message, msg, parse_mode='HTML')

@bot.message_handler(commands=['withdraw'])
def cmd_withdraw(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, "🚫 YOU ARE BANNED!", parse_mode='HTML')
        return
    balance = get_wallet(user_id)
    symbol = get_setting('currency_symbol', '₦')
    min_wd = int(get_setting('min_withdrawal', '5000'))
    if balance < min_wd:
        bot.reply_to(message, f"❌ MINIMUM WITHDRAWAL: {symbol}{min_wd:,}\nYour balance: {symbol}{balance:,.2f}", parse_mode='HTML')
        return
    bot.reply_to(message, f"📤 WITHDRAWAL REQUEST\n\nYour balance: {symbol}{balance:,.2f}\nMinimum: {symbol}{min_wd:,}\n\nSend in format:\n<code>AMOUNT|BANK|ACCOUNT|NAME</code>\n\nExample:\n<code>5000|OPay|9032741650|John Doe</code>\n\nType /cancel to cancel.", parse_mode='HTML')
    user_sessions[user_id] = {'state': 'withdraw'}

@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(message):
    if not is_admin(message.from_user.id):
        return
    broadcast_text = message.text.replace('/broadcast', '').strip()
    if not broadcast_text:
        bot.reply_to(message, "📝 USAGE: /broadcast MESSAGE", parse_mode='HTML')
        return
    c = db.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned = 0")
    users = [row[0] for row in c.fetchall()]
    if not users:
        bot.reply_to(message, "❌ No users to broadcast to!", parse_mode='HTML')
        return
    success = 0
    for uid in users:
        try:
            bot.send_message(uid, f"📢 ANNOUNCEMENT\n\n{broadcast_text}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            success += 1
        except:
            pass
    bot.reply_to(message, f"✅ BROADCAST COMPLETE!\n\n✅ Sent: {success}\n❌ Failed: {len(users) - success}", parse_mode='HTML')

@bot.message_handler(commands=['ban'])
def cmd_ban(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "📝 USAGE: /ban USER_ID", parse_mode='HTML')
        return
    try:
        target_id = int(parts[1])
        if target_id == MASTER_ADMIN_ID:
            bot.reply_to(message, "❌ Cannot ban master admin!", parse_mode='HTML')
            return
        ban_user(target_id)
        bot.reply_to(message, f"✅ User {target_id} BANNED!", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Invalid user ID!", parse_mode='HTML')

@bot.message_handler(commands=['unban'])
def cmd_unban(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "📝 USAGE: /unban USER_ID", parse_mode='HTML')
        return
    try:
        target_id = int(parts[1])
        unban_user(target_id)
        bot.reply_to(message, f"✅ User {target_id} UNBANNED!", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Invalid user ID!", parse_mode='HTML')

@bot.message_handler(commands=['grantadmin'])
def cmd_grant_admin(message):
    if message.from_user.id != MASTER_ADMIN_ID:
        bot.reply_to(message, "🚫 MASTER ADMIN ONLY!", parse_mode='HTML')
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "📝 USAGE: /grantadmin USER_ID", parse_mode='HTML')
        return
    try:
        target_id = int(parts[1])
        if target_id == MASTER_ADMIN_ID:
            bot.reply_to(message, "❌ Cannot modify master admin!", parse_mode='HTML')
            return
        grant_admin(target_id)
        bot.reply_to(message, f"✅ Admin granted to {target_id}!", parse_mode='HTML')
        try:
            bot.send_message(target_id, "👑 You have been granted ADMIN access!\nUse /admin to access the panel.", parse_mode='HTML')
        except:
            pass
    except:
        bot.reply_to(message, "❌ Invalid user ID!", parse_mode='HTML')

@bot.message_handler(commands=['revokeadmin'])
def cmd_revoke_admin(message):
    if message.from_user.id != MASTER_ADMIN_ID:
        bot.reply_to(message, "🚫 MASTER ADMIN ONLY!", parse_mode='HTML')
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "📝 USAGE: /revokeadmin USER_ID", parse_mode='HTML')
        return
    try:
        target_id = int(parts[1])
        if target_id == MASTER_ADMIN_ID:
            bot.reply_to(message, "❌ Cannot revoke master admin!", parse_mode='HTML')
            return
        revoke_admin(target_id)
        bot.reply_to(message, f"✅ Admin revoked from {target_id}!", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Invalid user ID!", parse_mode='HTML')

@bot.message_handler(commands=['users'])
def cmd_users(message):
    if not is_admin(message.from_user.id):
        return
    users = get_all_users(limit=50)
    if not users:
        bot.reply_to(message, "👥 NO USERS FOUND", parse_mode='HTML')
        return
    symbol = get_setting('currency_symbol', '₦')
    msg = "👥 ALL USERS\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for u in users[:30]:
        status = "🚫" if u['is_banned'] else "✅"
        admin_tag = "👑" if u['is_admin'] else "👤"
        msg += f"{status}{admin_tag} <code>{u['user_id']}</code> - {u['first_name']}\n   💰 {symbol}{u['wallet_balance']:,.2f}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    bot.reply_to(message, msg, parse_mode='HTML')

@bot.message_handler(commands=['payments'])
def cmd_payments(message):
    if not is_admin(message.from_user.id):
        return
    payments = get_pending_payments()
    symbol = get_setting('currency_symbol', '₦')
    if not payments:
        bot.reply_to(message, "💰 NO PENDING PAYMENTS", parse_mode='HTML')
        return
    msg = f"💰 PENDING PAYMENTS: {len(payments)}\n\n"
    for p in payments[:10]:
        msg += f"• User {p['user_id']} - {symbol}{p['amount']:,.0f} - {p['method']}\n"
    bot.reply_to(message, msg, parse_mode='HTML')

@bot.message_handler(commands=['withdrawals'])
def cmd_withdrawals(message):
    if not is_admin(message.from_user.id):
        return
    withdrawals = get_pending_withdrawals()
    symbol = get_setting('currency_symbol', '₦')
    if not withdrawals:
        bot.reply_to(message, "📤 NO PENDING WITHDRAWALS", parse_mode='HTML')
        return
    msg = f"📤 PENDING WITHDRAWALS: {len(withdrawals)}\n\n"
    for w in withdrawals[:10]:
        msg += f"• User {w['user_id']} - {symbol}{w['amount']:,.0f} - {w['bank_name']}\n"
    bot.reply_to(message, msg, parse_mode='HTML')

@bot.message_handler(commands=['backup'])
def cmd_backup(message):
    if not is_admin(message.from_user.id):
        return
    backup_name = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = os.path.join("backups", backup_name)
    shutil.copy2('marketplace.db', backup_path)
    with open(backup_path, 'rb') as f:
        bot.send_document(message.from_user.id, f, caption=f"💾 DATABASE BACKUP\n\n{backup_name}", parse_mode='HTML')
    bot.reply_to(message, "✅ BACKUP CREATED AND SENT!", parse_mode='HTML')

# =================================================================================
# STOCK ADDITION HANDLERS
# =================================================================================

def process_add_email_price(message):
    user_id = message.from_user.id
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    try:
        price = float(message.text.strip())
        if price <= 0:
            bot.reply_to(message, "❌ Price must be greater than 0!", parse_mode='HTML')
            bot.register_next_step_handler(message, process_add_email_price)
            return
        user_sessions[user_id]['price'] = price
        bot.reply_to(message, "📧 **Now send the email(s)**\n\nFormat:\n`email1,email2,email3|followers`\n\nExample:\n`test@gmail.com,user2@gmail.com|500`\n\nOr single:\n`test@gmail.com|500`\n\nType /cancel to cancel.", parse_mode='HTML')
        bot.register_next_step_handler(message, process_add_email_data)
    except:
        bot.reply_to(message, "❌ Invalid price! Send a number like 2000", parse_mode='HTML')
        bot.register_next_step_handler(message, process_add_email_price)

def process_add_email_data(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    price = session.get('price')
    if not price:
        bot.reply_to(message, "❌ Session expired. Start over.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    parts = message.text.split('|')
    if len(parts) != 2:
        bot.reply_to(message, "❌ Invalid format! Use: email(s)|followers", parse_mode='HTML')
        bot.register_next_step_handler(message, process_add_email_data)
        return
    emails_part = parts[0].strip()
    try:
        followers = int(parts[1].strip())
    except:
        bot.reply_to(message, "❌ Followers must be a number!", parse_mode='HTML')
        bot.register_next_step_handler(message, process_add_email_data)
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📧 Email Only (no password)", callback_data=f"add_email_type_only_{price}_{followers}_{emails_part}"),
        types.InlineKeyboardButton("🔐 Email + Password", callback_data=f"add_email_type_pass_{price}_{followers}_{emails_part}"),
        types.InlineKeyboardButton("◀️ CANCEL", callback_data="admin_back")
    )
    bot.send_message(user_id, f"💰 Price: ₦{price:,.0f}\n📸 Followers: {followers}\n📧 Emails: {emails_part[:100]}\n\nDo these emails have passwords?", parse_mode='HTML', reply_markup=markup)

def process_add_ig_price(message):
    user_id = message.from_user.id
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    try:
        price = float(message.text.strip())
        if price <= 0:
            bot.reply_to(message, "❌ Price must be greater than 0!", parse_mode='HTML')
            bot.register_next_step_handler(message, process_add_ig_price)
            return
        user_sessions[user_id]['price'] = price
        bot.reply_to(message, "🔗 **Now send the IG username(s)**\n\nFormat:\n`user1,user2,user3|followers`\n\nExample:\n`john_doe,jane_doe|500`\n\nOr single:\n`john_doe|500`\n\nType /cancel to cancel.", parse_mode='HTML')
        bot.register_next_step_handler(message, process_add_ig_data)
    except:
        bot.reply_to(message, "❌ Invalid price! Send a number like 2000", parse_mode='HTML')
        bot.register_next_step_handler(message, process_add_ig_price)

def process_add_ig_data(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    price = session.get('price')
    if not price:
        bot.reply_to(message, "❌ Session expired. Start over.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    parts = message.text.split('|')
    if len(parts) != 2:
        bot.reply_to(message, "❌ Invalid format! Use: username(s)|followers", parse_mode='HTML')
        bot.register_next_step_handler(message, process_add_ig_data)
        return
    usernames_part = parts[0].strip()
    try:
        followers = int(parts[1].strip())
    except:
        bot.reply_to(message, "❌ Followers must be a number!", parse_mode='HTML')
        bot.register_next_step_handler(message, process_add_ig_data)
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔗 IG Only (no password)", callback_data=f"add_ig_type_only_{price}_{followers}_{usernames_part}"),
        types.InlineKeyboardButton("🔐 IG + Password", callback_data=f"add_ig_type_pass_{price}_{followers}_{usernames_part}"),
        types.InlineKeyboardButton("◀️ CANCEL", callback_data="admin_back")
    )
    bot.send_message(user_id, f"💰 Price: ₦{price:,.0f}\n📸 Followers: {followers}\n🔗 Usernames: {usernames_part[:100]}\n\nDo these IG accounts have passwords?", parse_mode='HTML', reply_markup=markup)

# =================================================================================
# COMPLETE IG STOCK ADDITION
# =================================================================================

def process_add_complete_ig_price(message):
    user_id = message.from_user.id
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    try:
        price = float(message.text.strip())
        if price <= 0:
            bot.reply_to(message, "❌ Price must be greater than 0!", parse_mode='HTML')
            bot.register_next_step_handler(message, process_add_complete_ig_price)
            return
        user_sessions[user_id]['price'] = price
        bot.reply_to(message, "🎁 **Send the product name**\n\nExample: `Premium Instagram Account - 5000 Followers`\n\nType /cancel to cancel.", parse_mode='HTML')
        bot.register_next_step_handler(message, process_add_complete_ig_name)
    except:
        bot.reply_to(message, "❌ Invalid price! Send a number.", parse_mode='HTML')
        bot.register_next_step_handler(message, process_add_complete_ig_price)

def process_add_complete_ig_name(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    price = session.get('price')
    if not price:
        bot.reply_to(message, "❌ Session expired. Start over.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    user_sessions[user_id]['product_name'] = message.text.strip()
    bot.reply_to(message, "🔗 **Send the Instagram username**\n\nExample: `john_doe`\n\nType /cancel to cancel.", parse_mode='HTML')
    bot.register_next_step_handler(message, process_add_complete_ig_username)

def process_add_complete_ig_username(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    if not session.get('price'):
        bot.reply_to(message, "❌ Session expired. Start over.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    user_sessions[user_id]['username'] = message.text.strip()
    bot.reply_to(message, "🔑 **Send the Instagram password**\n\nExample: `password123`\n\nType /cancel to cancel.", parse_mode='HTML')
    bot.register_next_step_handler(message, process_add_complete_ig_password)

def process_add_complete_ig_password(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    if not session.get('price'):
        bot.reply_to(message, "❌ Session expired. Start over.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    user_sessions[user_id]['password'] = message.text.strip()
    bot.reply_to(message, "📧 **Send the email (if available)**\n\nIf no email, send `none`\n\nType /cancel to cancel.", parse_mode='HTML')
    bot.register_next_step_handler(message, process_add_complete_ig_email)

def process_add_complete_ig_email(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    if not session.get('price'):
        bot.reply_to(message, "❌ Session expired. Start over.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    user_sessions[user_id]['email'] = message.text.strip() if message.text.strip().lower() != 'none' else None
    bot.reply_to(message, "🔑 **Send the email password (if available)**\n\nIf no email password, send `none`\n\nType /cancel to cancel.", parse_mode='HTML')
    bot.register_next_step_handler(message, process_add_complete_ig_email_password)

def process_add_complete_ig_email_password(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    if not session.get('price'):
        bot.reply_to(message, "❌ Session expired. Start over.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    user_sessions[user_id]['email_password'] = message.text.strip() if message.text.strip().lower() != 'none' else None
    bot.reply_to(message, "📸 **Send the account screenshot**\n\nSend a photo of the Instagram account.\n\nType /cancel to cancel.", parse_mode='HTML')
    bot.register_next_step_handler(message, process_add_complete_ig_screenshot)

def process_add_complete_ig_screenshot(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    if not session.get('price'):
        bot.reply_to(message, "❌ Session expired. Start over.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    if not message.photo:
        bot.reply_to(message, "❌ Please send a screenshot of the Instagram account!", parse_mode='HTML')
        bot.register_next_step_handler(message, process_add_complete_ig_screenshot)
        return
    
    photo = message.photo[-1]
    user_sessions[user_id]['screenshot'] = photo.file_id
    
    bot.reply_to(message, "📝 **Send a description (optional)**\n\nExample: `Verified account with 5000 followers, email access included`\n\nOr send `skip` to skip.\n\nType /cancel to cancel.", parse_mode='HTML')
    bot.register_next_step_handler(message, process_add_complete_ig_description)

def process_add_complete_ig_description(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    price = session.get('price')
    product_name = session.get('product_name')
    username = session.get('username')
    password = session.get('password')
    email = session.get('email')
    email_password = session.get('email_password')
    screenshot = session.get('screenshot')
    
    if not price:
        bot.reply_to(message, "❌ Session expired. Start over.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    
    description = message.text.strip() if message.text.strip().lower() != 'skip' else ""
    
    followers = 0
    numbers = re.findall(r'\d+', product_name)
    if numbers:
        followers = int(numbers[0])
    
    if IGShopStock.add_item(product_name, username, password, email, email_password, followers, price, screenshot, description, user_id):
        bot.reply_to(message, f"✅ **COMPLETE IG ACCOUNT ADDED!**\n\n🎁 {product_name}\n💰 ₦{price:,.0f}\n🔗 @{username}\n📸 Screenshot saved!\n\nThis account is now available for purchase.", parse_mode='HTML')
    else:
        bot.reply_to(message, "❌ Failed to add account!", parse_mode='HTML')
    
    del user_sessions[user_id]

# =================================================================================
# PAYMENT FLOW
# =================================================================================

def process_fund_amount(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    method = session.get('payment_method')
    if not method:
        return
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    try:
        amount = float(message.text.strip())
        min_deposit = int(get_setting('min_deposit', '500'))
        symbol = get_setting('currency_symbol', '₦')
        if amount < min_deposit:
            bot.reply_to(message, f"❌ Minimum deposit: {symbol}{min_deposit:,}", parse_mode='HTML')
            bot.register_next_step_handler(message, process_fund_amount)
            return
        user_sessions[user_id]['amount'] = amount
        if method == "OPay":
            account = OPAY_ACCOUNT
            name = OPAY_NAME
        elif method == "PalmPay":
            account = PALMPAY_ACCOUNT
            name = PALMPAY_NAME
        else:
            account = BANK_ACCOUNT
            name = BANK_NAME
        bot.reply_to(message, f"""
💳 {method.upper()} PAYMENT DETAILS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏦 {method}
📋 ACCOUNT: <code>{account}</code>
👤 NAME: {name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 AMOUNT TO SEND: {symbol}{amount:,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 INSTRUCTIONS:

1️⃣ Send exactly {symbol}{amount:,.2f} to the account above
2️⃣ Take a SCREENSHOT of the payment confirmation
3️⃣ Send the screenshot here

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📸 SEND YOUR PAYMENT SCREENSHOT NOW

Type /cancel to cancel.
""", parse_mode='HTML')
        bot.register_next_step_handler(message, process_payment_screenshot)
    except:
        bot.reply_to(message, "❌ Invalid amount! Send a number.", parse_mode='HTML')
        bot.register_next_step_handler(message, process_fund_amount)

def process_payment_screenshot(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    amount = session.get('amount')
    method = session.get('payment_method')
    if not amount or not method:
        bot.reply_to(message, "❌ Session expired. Start over.", parse_mode='HTML')
        return
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    if not message.photo:
        bot.reply_to(message, "❌ Please send a screenshot of your payment confirmation.", parse_mode='HTML')
        bot.register_next_step_handler(message, process_payment_screenshot)
        return
    photo = message.photo[-1]
    reference = f"IMG_{user_id}_{int(time.time())}"
    payment_id = create_payment(user_id, amount, method, reference, photo.file_id)
    symbol = get_setting('currency_symbol', '₦')
    bot.reply_to(message, f"""
✅ PAYMENT PROOF RECEIVED!

💰 Amount: {symbol}{amount:,.2f}
🏦 Method: {method}
🆔 ID: <code>{payment_id[:12]}...</code>

⏳ Pending admin approval. You will be notified when confirmed.
""", parse_mode='HTML')
    caption = f"""
💰 NEW PAYMENT REQUEST

👤 User: <code>{user_id}</code>
💰 Amount: {symbol}{amount:,.2f}
🏦 Method: {method}
🆔 ID: <code>{payment_id}</code>

Click CONFIRM to credit user wallet.
"""
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ CONFIRM", callback_data=f"confirm_payment_{payment_id}"),
        types.InlineKeyboardButton("❌ REJECT", callback_data=f"reject_payment_{payment_id}")
    )
    # Send to master admin only (no duplicates)
    try:
        bot.send_photo(MASTER_ADMIN_ID, photo.file_id, caption=caption, parse_mode='HTML', reply_markup=markup)
    except:
        pass
    if user_id in user_sessions:
        del user_sessions[user_id]

def process_buy_followers(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    followers = session.get('followers')
    price = session.get('price')
    if not followers or not price:
        bot.reply_to(message, "❌ Session expired. Start over.", parse_mode='HTML')
        return
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Purchase cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    username = message.text.strip().replace('@', '')
    balance = get_wallet(user_id)
    symbol = get_setting('currency_symbol', '₦')
    if balance < price:
        bot.reply_to(message, f"❌ Insufficient funds!\nNeed: {symbol}{price:,.2f}\nYour balance: {symbol}{balance:,.2f}", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    update_wallet(user_id, -price)
    update_admin_wallet(price, True)
    process_referral(user_id)
    order_id = create_order(user_id, "instagram", f"{followers} Instagram Followers", 1, price, username)
    add_transaction(user_id, -price, 'purchase', order_id, 'completed')
    bot.reply_to(message, f"""
✅ ORDER CONFIRMED!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📸 INSTAGRAM: @{username}
👥 FOLLOWERS: {followers}
💰 PAID: {symbol}{price:,.2f}

📦 ORDER ID: {order_id[:12]}...

⏱ DELIVERY TIME: 1-5 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 {MY_SIGNATURE}
""", parse_mode='HTML')
    
    # Send to master admin only
    try:
        bot.send_message(MASTER_ADMIN_ID, f"📸 IG ORDER!\n\nUser: {user_id}\nIG: @{username}\nFollowers: {followers}\nAmount: {symbol}{price:,.2f}", parse_mode='HTML')
    except:
        pass
    if user_id in user_sessions:
        del user_sessions[user_id]

def process_withdraw(message):
    user_id = message.from_user.id
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    parts = message.text.split('|')
    if len(parts) != 4:
        bot.reply_to(message, "❌ Invalid format! Use: AMOUNT|BANK|ACCOUNT|NAME", parse_mode='HTML')
        bot.register_next_step_handler(message, process_withdraw)
        return
    try:
        amount = float(parts[0].strip())
        bank = parts[1].strip()
        account_num = parts[2].strip()
        account_name = parts[3].strip()
        symbol = get_setting('currency_symbol', '₦')
        min_wd = int(get_setting('min_withdrawal', '5000'))
        if amount < min_wd:
            bot.reply_to(message, f"❌ Minimum withdrawal: {symbol}{min_wd:,}", parse_mode='HTML')
            return
        balance = get_wallet(user_id)
        if amount > balance:
            bot.reply_to(message, f"❌ Insufficient funds! Balance: {symbol}{balance:,.2f}", parse_mode='HTML')
            return
        update_wallet(user_id, -amount)
        add_transaction(user_id, -amount, 'withdrawal', 'pending', 'pending')
        withdraw_id = create_withdrawal(user_id, amount, bank, account_num, account_name)
        bot.reply_to(message, f"✅ WITHDRAWAL REQUEST SUBMITTED!\n\n💰 Amount: {symbol}{amount:,.2f}\n🏦 Bank: {bank}\n🆔 ID: {withdraw_id[:12]}...\n\n⏳ Admin will process within 24 hours.", parse_mode='HTML')
        # Send to master admin only
        try:
            bot.send_message(MASTER_ADMIN_ID, f"📤 NEW WITHDRAWAL\n\nUser: {user_id}\nAmount: {symbol}{amount:,.2f}\nBank: {bank}\nID: {withdraw_id}", parse_mode='HTML')
        except:
            pass
        if user_id in user_sessions:
            del user_sessions[user_id]
    except:
        bot.reply_to(message, "❌ Error processing withdrawal!", parse_mode='HTML')

# =================================================================================
# CALLBACK HANDLERS
# =================================================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    print(f"🔔 Callback received: {call.data}")  # ← ADD THIS LINE HERE
    user_id = call.from_user.id
    data = call.data
    symbol = get_setting('currency_symbol', '₦')
    
    # ========== BUY COMPLETE IG ==========
    if data.startswith("buy_complete_ig_"):
        item_id = int(data.replace("buy_complete_ig_", ""))
        item = IGShopStock.get_item_by_id(item_id)
        
        if not item or item['status'] != 'available':
            bot.answer_callback_query(call.id, "❌ Item not available!", show_alert=True)
            return
        
        # Show screenshot with "I WANT TO BUY THIS" button (NO wallet check yet)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ I WANT TO BUY THIS", callback_data=f"want_to_buy_ig_{item_id}"),
            types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
        )
        
        caption = f"""
🎁 **{item['product_name']}**

💰 Price: {symbol}{item['price']:,.2f}
🔗 Username: @{item['username']}
📸 Followers: {item['followers_count']:,}

📝 {item['description'] if item['description'] else 'No description'}

Click "I WANT TO BUY THIS" to proceed.
"""
        if item['screenshot_file_id']:
            bot.send_photo(call.message.chat.id, item['screenshot_file_id'], caption=caption, parse_mode='HTML', reply_markup=markup)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.edit_message_text(caption, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        
        bot.answer_callback_query(call.id, "View account details")
        return
        
    if data.startswith("want_to_buy_ig_"):
        item_id = int(data.replace("want_to_buy_ig_", ""))
        item = IGShopStock.get_item_by_id(item_id)
        
        if not item or item['status'] != 'available':
            bot.answer_callback_query(call.id, "❌ Item not available!", show_alert=True)
            return
        
        balance = get_wallet(user_id)
        
        if balance < item['price']:
            bot.answer_callback_query(call.id, f"❌ INSUFFICIENT FUNDS!\n\nNeed: {symbol}{item['price']:,.2f}\nYour balance: {symbol}{balance:,.2f}\n\nPlease fund your wallet first.", show_alert=True)
            return
        
        # Process purchase immediately
        update_wallet(user_id, -item['price'])
        process_referral(user_id)
        update_admin_wallet(item['price'], True)
        IGShopStock.mark_sold(item_id, user_id)
        order_id = IGShopOrder.create_order(user_id, item_id, item['product_name'], item['price'])
        add_transaction(user_id, -item['price'], 'purchase', order_id, 'completed')
        
        # Show success message with screenshot
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("◀️ BACK TO MAIN MENU", callback_data="back_main"))
        
        caption = f"""
✅ **THANK YOU FOR YOUR PURCHASE!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 {item['product_name']}
🔗 Username: @{item['username']}
📸 Followers: {item['followers_count']:,}
💰 Paid: {symbol}{item['price']:,.2f}
💳 New Balance: {symbol}{get_wallet(user_id):,.2f}

📦 Order ID: {order_id[:12]}...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ If you have any issues, contact: @{BOT_USERNAME}

💎 {MY_SIGNATURE}
"""
        if account['screenshot_file_ids']:
            screenshot_ids = account['screenshot_file_ids'].split(',')
            bot.send_photo(call.message.chat.id, screenshot_ids[0], caption=delivery_text, parse_mode='HTML', reply_markup=markup)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.edit_message_text(delivery_text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        
        bot.answer_callback_query(call.id, "✅ Purchase successful!")
        return


    # ========== FB EDIT PRICE (STEP 5) ==========
    if data == "fb_edit_price":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("✏️ **EDIT FB ACCOUNT PRICE**\n\nSend in format:\n`account_id|new_price`\n\nExample: `5|3000`\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        user_sessions[user_id] = {'state': 'fb_edit_price'}
        return

    # ========== BUY EXACT EMAIL (STEP 6) ==========
    if data.startswith("buy_exact_email_"):
        email_id = int(data.replace("buy_exact_email_", ""))
        
        c = db.cursor()
        c.execute("SELECT id, email, username, password, has_password, followers_count, price FROM email_stock WHERE id = ? AND status = 'available'", (email_id,))
        email_data = c.fetchone()
        
        if not email_data:
            bot.answer_callback_query(call.id, "❌ Email not available!", show_alert=True)
            return
        
        balance = get_wallet(user_id)
        
        if balance < email_data['price']:
            bot.answer_callback_query(call.id, f"❌ Insufficient funds! Need: {symbol}{email_data['price']:,.2f}", show_alert=True)
            return
        
        masked_email = mask_email(email_data['email'])
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        if email_data['has_password']:
            markup.add(
                types.InlineKeyboardButton(f"✅ CONFIRM PURCHASE - {symbol}{email_data['price']:,.0f}", callback_data=f"confirm_email_purchase_{email_id}_withpass"),
                types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
            )
            bot.edit_message_text(f"📧 **EMAIL DETAILS:**\n\n📧 {masked_email}\n📸 {email_data['followers_count']} followers\n💰 {symbol}{email_data['price']:,.0f}\n\n🔑 This email HAS a password\n💰 Balance: {symbol}{balance:,.2f}\n\nClick CONFIRM to purchase:", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        else:
            markup.add(
                types.InlineKeyboardButton(f"✅ CONFIRM PURCHASE - {symbol}{email_data['price']:,.0f}", callback_data=f"confirm_email_purchase_{email_id}_only"),
                types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
            )
            bot.edit_message_text(f"📧 **EMAIL DETAILS:**\n\n📧 {masked_email}\n📸 {email_data['followers_count']} followers\n💰 {symbol}{email_data['price']:,.0f}\n\n⚠️ No password\n💰 Balance: {symbol}{balance:,.2f}\n\nClick CONFIRM to purchase:", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        
        bot.answer_callback_query(call.id, "Select option")
        return

    # ========== CONFIRM EMAIL PURCHASE ==========
    if data.startswith("confirm_email_purchase_"):
        parts = data.split("_")
        email_id = int(parts[3])
        include_pass = parts[4] == "withpass"
        
        c = db.cursor()
        c.execute("SELECT id, email, username, password, has_password, followers_count, price FROM email_stock WHERE id = ? AND status = 'available'", (email_id,))
        email_data = c.fetchone()
        
        if not email_data:
            bot.answer_callback_query(call.id, "❌ Email not available!", show_alert=True)
            return
        
        balance = get_wallet(user_id)
        symbol = get_setting('currency_symbol', '₦')
        
        if balance < email_data['price']:
            bot.answer_callback_query(call.id, "❌ Insufficient funds!", show_alert=True)
            return
        
        # Process purchase
        update_wallet(user_id, -email_data['price'])
        process_referral(user_id)
        update_admin_wallet(email_data['price'], True)
        mark_email_sold(email_id, user_id)
        
        # Post to channel about this sale
        post_purchase_to_channel("email", f"{email_data['followers_count']} followers", email_data['price'])
        
        # Different message based on whether password is included
        if include_pass and email_data.get('password'):
            # HAS PASSWORD - Show password directly
            delivery_text = f"""
✅ ORDER CONFIRMED!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 EMAIL: {email_data['email']}
👤 USERNAME: {email_data['username']}
📸 FOLLOWERS: {email_data['followers_count']}
🔑 PASSWORD: {email_data['password']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **IMPORTANT:**
   • Change password immediately after login
   • Do not share this email with anyone
   • Enable login notifications for security

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 PAID: {symbol}{email_data['price']:,.2f}
💳 New Balance: {symbol}{get_wallet(user_id):,.2f}

📦 ORDER ID: {order_id[:12]}...

💎 {MY_SIGNATURE}
"""
        else:
            # NO PASSWORD - Show setup instructions
            delivery_text = f"""
✅ ORDER CONFIRMED!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 EMAIL: {email_data['email']}
👤 USERNAME: {email_data['username']}
📸 FOLLOWERS: {email_data['followers_count']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 **PASSWORD SETUP (No password included):**

1️⃣ GO TO GMAIL.COM
2️⃣ Click "Create account" → "For myself"
3️⃣ Fill in your details:
   • First Name: (any name)
   • Last Name: (any name)
   • Birthday: (any date)
   • Gender: (any)
4️⃣ When asked for email username → USE: {email_data['username']}
5️⃣ Create your own password (6-12 characters)
6️⃣ Verify with phone number (optional - can skip)
7️⃣ Complete the account creation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 **HOW TO ACCESS INSTAGRAM:**

1️⃣ Open Instagram App
2️⃣ Click "Forgot password"
3️⃣ Enter the username: {email_data['username']}
4️⃣ Select "Send email to {email_data['email']}"
5️⃣ Check your Gmail for the reset code
6️⃣ Enter the code and create new password
7️⃣ You're in! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **IMPORTANT NOTES:**
   • Do not share this email with anyone
   • Change recovery email to your personal email
   • Keep your password safe and secure

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ **NEED HELP?**
   • Contact admin: @{BOT_USERNAME}
   • For Instagram reset issues, admin can help

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 PAID: {symbol}{email_data['price']:,.2f}
💳 New Balance: {symbol}{get_wallet(user_id):,.2f}

📦 ORDER ID: {order_id[:12]}...

💎 {MY_SIGNATURE}
"""
        
        order_id = create_order(user_id, "email", f"{email_data['followers_count']} Followers Email", 1, email_data['price'], delivery_text)
        add_transaction(user_id, -email_data['price'], 'purchase', order_id, 'completed')
        
        bot.edit_message_text(delivery_text, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        
        bot.answer_callback_query(call.id, "✅ Purchase successful!")
        return

    # ========== FB VIEW STOCK (STEP 8) ==========
    if data == "fb_view_stock":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        stocks = get_all_fb_stock()
        if not stocks:
            bot.edit_message_text("📘 **NO FB ACCOUNTS IN STOCK**", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        msg = "📘 **FB ACCOUNTS STOCK**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for s in stocks[:20]:
            msg += f"✅ ID: `{s['id']}` | {s['email']}\n   📂 {s['category_name']} | {symbol}{s['price']:,.0f} | Age: {s['account_age']}\n"
            if s['has_screenshot']:
                msg += f"   📸 Has screenshot | /viewfb {s['id']} to see\n"
            msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return

    # ========== PAYMENT CONFIRMATION ==========
    if data.startswith("confirm_payment_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        payment_id = data.replace("confirm_payment_", "")
        success, credited_user, amount = confirm_payment(payment_id, user_id)
        if success:
            bot.answer_callback_query(call.id, f"✅ Payment confirmed! {symbol}{amount:,.2f} added.", show_alert=True)
            bot.edit_message_caption(f"✅ PAYMENT CONFIRMED!\n\nUser credited: {symbol}{amount:,.2f}", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            try:
                bot.send_message(credited_user, f"✅ PAYMENT CONFIRMED!\n\n💰 {symbol}{amount:,.2f} added to your wallet!\n\nNew balance: {symbol}{get_wallet(credited_user):,.2f}", parse_mode='HTML')
            except:
                pass
        else:
            bot.answer_callback_query(call.id, "❌ Payment already processed!", show_alert=True)
        return
    
    if data.startswith("reject_payment_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        payment_id = data.replace("reject_payment_", "")
        reject_payment(payment_id, user_id)
        bot.answer_callback_query(call.id, "❌ Payment rejected!", show_alert=True)
        bot.edit_message_caption("❌ PAYMENT REJECTED", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    # ========== PRICING RULES MANAGEMENT ==========
    if data == "admin_pricing":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        markup = pricing_keyboard()
        current_prices = PricingEngine.get_price_for_display()
        bot.edit_message_text(f"💰 **PRICING RULES MANAGEMENT**\n\nCurrent rules:\n{current_prices}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nClick a rule to edit its price.\n\nTo ADD a new rule, click the button below.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
        markup = pricing_keyboard()
        current_prices = PricingEngine.get_price_for_display()
        bot.edit_message_text(f"💰 **PRICING RULES MANAGEMENT**\n\nCurrent rules:\n{current_prices}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nClick a rule to edit its price.\n\nTo ADD a new rule, click the button below.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data == "admin_ig_pricing":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        markup = ig_pricing_keyboard()
        current_prices = IGShopPricing.get_price_for_display()
        bot.edit_message_text(f"💰 **IG SHOP PRICING MANAGEMENT**\n\nCurrent prices:\n{current_prices}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nClick a price to edit it.\n\nTo ADD a new price, click the button below.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data == "admin_fb":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("📘 **FACEBOOK MANAGEMENT**", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=fb_admin_keyboard())
        return
    
    if data.startswith("edit_rule_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        rule_id = int(data.replace("edit_rule_", ""))
        user_sessions[user_id] = {'state': 'edit_rule_price', 'rule_id': rule_id}
        bot.edit_message_text(f"✏️ **EDIT PRICE**\n\nEnter the new price for this rule:\n\nSend a number like `2000`\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data.startswith("edit_ig_price_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        price_id = int(data.replace("edit_ig_price_", ""))
        user_sessions[user_id] = {'state': 'edit_ig_price', 'price_id': price_id}
        bot.edit_message_text(f"✏️ **EDIT IG SHOP PRICE**\n\nEnter the new price:\n\nSend a number like `20000`\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data.startswith("delete_rule_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        rule_id = int(data.replace("delete_rule_", ""))
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ YES, DELETE", callback_data=f"confirm_delete_rule_{rule_id}"),
            types.InlineKeyboardButton("❌ CANCEL", callback_data="admin_pricing")
        )
        bot.edit_message_text("⚠️ **ARE YOU SURE?**\n\nThis rule will be permanently deleted.\n\nClick YES to confirm.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("delete_ig_price_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        price_id = int(data.replace("delete_ig_price_", ""))
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ YES, DELETE", callback_data=f"confirm_delete_ig_price_{price_id}"),
            types.InlineKeyboardButton("❌ CANCEL", callback_data="admin_ig_pricing")
        )
        bot.edit_message_text("⚠️ **ARE YOU SURE?**\n\nThis price will be permanently deleted.\n\nClick YES to confirm.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("confirm_delete_rule_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        rule_id = int(data.replace("confirm_delete_rule_", ""))
        PricingEngine.delete_rule(rule_id)
        bot.answer_callback_query(call.id, "✅ Rule deleted!", show_alert=True)
        markup = pricing_keyboard()
        current_prices = PricingEngine.get_price_for_display()
        bot.edit_message_text(f"💰 **PRICING RULES MANAGEMENT**\n\nCurrent rules:\n{current_prices}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ Rule deleted!\n\nClick a rule to edit its price.\n\nTo ADD a new rule, click the button below.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("confirm_delete_ig_price_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        price_id = int(data.replace("confirm_delete_ig_price_", ""))
        IGShopPricing.delete_price(price_id)
        bot.answer_callback_query(call.id, "✅ Price deleted!", show_alert=True)
        markup = ig_pricing_keyboard()
        current_prices = IGShopPricing.get_price_for_display()
        bot.edit_message_text(f"💰 **IG SHOP PRICING MANAGEMENT**\n\nCurrent prices:\n{current_prices}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ Price deleted!\n\nClick a price to edit it.\n\nTo ADD a new price, click the button below.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data == "delete_all_rules":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("⚠️ YES, DELETE ALL", callback_data="confirm_delete_all_rules"),
            types.InlineKeyboardButton("❌ CANCEL", callback_data="admin_pricing")
        )
        bot.edit_message_text("⚠️ **DELETE ALL PRICING RULES?**\n\nThis action cannot be undone!\n\nClick YES to confirm.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data == "confirm_delete_all_rules":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        PricingEngine.delete_all_rules()
        bot.answer_callback_query(call.id, "✅ All rules deleted!", show_alert=True)
        markup = pricing_keyboard()
        bot.edit_message_text(f"💰 **PRICING RULES MANAGEMENT**\n\nAll rules have been deleted.\n\nUse the button below to add new rules.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data == "delete_all_ig_prices":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("⚠️ YES, DELETE ALL", callback_data="confirm_delete_all_ig_prices"),
            types.InlineKeyboardButton("❌ CANCEL", callback_data="admin_ig_pricing")
        )
        bot.edit_message_text("⚠️ **DELETE ALL IG SHOP PRICES?**\n\nThis action cannot be undone!\n\nClick YES to confirm.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data == "confirm_delete_all_ig_prices":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        IGShopPricing.delete_all_prices()
        bot.answer_callback_query(call.id, "✅ All IG prices deleted!", show_alert=True)
        markup = ig_pricing_keyboard()
        bot.edit_message_text(f"💰 **IG SHOP PRICING MANAGEMENT**\n\nAll prices have been deleted.\n\nUse the button below to add new prices.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data == "add_pricing_rule":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("➕ **ADD NEW PRICING RULE**\n\nSend in format:\n`rule_name|type|min|max|price`\n\nTypes: `range` or `min` or `single`\n\nExamples:\n`Premium Package|range|200|500|5000`\n`VIP Package|min|1000|0|10000`\n`Basic|single|100|100|500`\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        user_sessions[user_id] = {'state': 'add_pricing_rule'}
        return
    
    if data == "add_ig_pricing_rule":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("➕ **ADD NEW IG SHOP PRICE**\n\nSend in format:\n`price_name|price|description`\n\nExample:\n`Premium IG Account|50000|5000+ followers, verified`\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        user_sessions[user_id] = {'state': 'add_ig_pricing_rule'}
        return
    
    if data == "fb_add_category":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("➕ **ADD FB CATEGORY**\n\nSend in format:\n`name|display_name|price|has_page`\n\nExample:\n`local_premium|🇳🇬 Premium Nigeria FB|5000|1`\n\nhas_page: 0=No page, 1=Has page\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        user_sessions[user_id] = {'state': 'fb_add_category'}
        return
    
    if data == "fb_add_account":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        categories = get_all_fb_categories()
        if not categories:
            bot.answer_callback_query(call.id, "❌ No categories! Add a category first.", show_alert=True)
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for cat in categories:
            markup.add(types.InlineKeyboardButton(f"📘 {cat['display_name']}", callback_data=f"fb_upload_category_{cat['id']}"))
        markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="admin_fb"))
        bot.edit_message_text("📘 **SELECT FB CATEGORY**", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("fb_upload_category_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        cat_id = int(data.replace("fb_upload_category_", ""))
        user_sessions[user_id] = {'state': 'fb_upload_price', 'fb_upload_category': cat_id}
        bot.edit_message_text("💰 **Enter the PRICE for these FB accounts**\n\nSend a number like: `2000`\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler(call.message, process_fb_upload_price)
        return
    
    if data == "fb_view_stock":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        stocks = get_all_fb_stock()
        if not stocks:
            bot.edit_message_text("📘 **NO FB ACCOUNTS IN STOCK**", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        msg = "📘 **FB ACCOUNTS STOCK**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for s in stocks[:50]:
            msg += f"✅ ID {s['id']} | {s['email']}\n   📂 {s['category_name']} | {symbol}{s['price']:,.0f} | Age: {s['account_age']}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "fb_delete_stock":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("🗑 **DELETE FB STOCK**\n\nSend the FB Account ID to delete.\n\nView IDs from 📋 VIEW FB STOCK.\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        user_sessions[user_id] = {'state': 'delete_fb_by_id'}
        return
    
    if data == "fb_delete_all":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        delete_all_fb_stock()
        bot.answer_callback_query(call.id, "✅ All FB stock deleted!", show_alert=True)
        bot.edit_message_text("✅ All FB stock has been deleted.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    # ========== ADD STOCK CALLBACKS ==========
    if data.startswith("add_email_type_only_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        parts = data.split("_")
        price = float(parts[4])
        followers = int(parts[5])
        emails_part = "_".join(parts[6:])
        email_list = [e.strip() for e in emails_part.split(',')]
        added = 0
        for email in email_list:
            if add_email_only(email, followers, price, user_id):
                added += 1
        bot.answer_callback_query(call.id, f"✅ Added {added} emails!", show_alert=True)
        bot.edit_message_text(f"✅ Added {added} emails (no password)!\n\nFollowers: {followers}\nPrice: {symbol}{price:,.0f} each", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data.startswith("add_email_type_pass_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        parts = data.split("_")
        price = float(parts[4])
        followers = int(parts[5])
        emails_part = "_".join(parts[6:])
        bot.edit_message_text("📧 **Send passwords for each email**\n\nFormat:\n`email1:password1,email2:password2`\n\nExample:\n`test@gmail.com:pass123,user2@gmail.com:pass456`\n\nMust match the email order!", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        user_sessions[user_id] = {'state': 'add_email_passwords', 'price': price, 'followers': followers, 'emails': emails_part.split(',')}
        return
    
    if data.startswith("add_ig_type_only_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        parts = data.split("_")
        price = float(parts[4])
        followers = int(parts[5])
        usernames_part = "_".join(parts[6:])
        username_list = [u.strip() for u in usernames_part.split(',')]
        added = 0
        for username in username_list:
            if add_ig_only(username, followers, price, user_id):
                added += 1
        bot.answer_callback_query(call.id, f"✅ Added {added} IG accounts!", show_alert=True)
        bot.edit_message_text(f"✅ Added {added} IG accounts (no password)!\n\nFollowers: {followers}\nPrice: {symbol}{price:,.0f} each", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data.startswith("add_ig_type_pass_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        parts = data.split("_")
        price = float(parts[4])
        followers = int(parts[5])
        usernames_part = "_".join(parts[6:])
        bot.edit_message_text("🔗 **Send passwords for each IG account**\n\nFormat:\n`user1:password1,user2:password2`\n\nExample:\n`john_doe:pass123,jane_doe:pass456`\n\nMust match the username order!", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        user_sessions[user_id] = {'state': 'add_ig_passwords', 'price': price, 'followers': followers, 'usernames': usernames_part.split(',')}
        return
    
        # ========== BUY PRODUCT CALLBACKS ==========
    
    # CHECK FOR TYPE CALLBACKS FIRST (more specific)
    if data.startswith("buy_email_type_"):
        parts = data.split("_")
        followers = int(parts[3])
        price = float(parts[4])
        item_type = parts[5]
        require_pass = (item_type == "withpass")
        stock = get_email_stock_count(followers, require_password=require_pass)
        if stock == 0:
            bot.answer_callback_query(call.id, "❌ Out of stock! Admin notified.", show_alert=True)
            return
        balance = get_wallet(user_id)
        if balance < price:
            bot.answer_callback_query(call.id, f"❌ Insufficient funds! Need: {symbol}{price:,.2f}", show_alert=True)
            return
        email_data = get_available_email(followers, require_password=require_pass)
        if not email_data:
            bot.answer_callback_query(call.id, "❌ Stock error!", show_alert=True)
            return
        update_wallet(user_id, -price)
        process_referral(user_id)
        update_admin_wallet(price, True)
        mark_email_sold(email_data['id'], user_id)
        delivery_text = f"📧 EMAIL: {email_data['email']}\n👤 USERNAME: {email_data['username']}"
        if require_pass and email_data.get('password'):
            delivery_text += f"\n🔑 PASSWORD: {email_data['password']}"
        order_id = create_order(user_id, "email", f"{followers} Followers Email", 1, price, delivery_text)
        add_transaction(user_id, -price, 'purchase', order_id, 'completed')
        bot.edit_message_text(f"""
✅ ORDER CONFIRMED!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{delivery_text}

📸 FOLLOWERS: {followers}
💰 PAID: {symbol}{price:,.2f}

📦 ORDER ID: {order_id[:12]}...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 {MY_SIGNATURE}
""", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.answer_callback_query(call.id, "✅ Purchase successful!")
        return

    if data.startswith("buy_ig_type_"):
        # Add similar for IG type
        parts = data.split("_")
        followers = int(parts[3])
        price = float(parts[4])
        item_type = parts[5]
        require_pass = (item_type == "withpass")
        stock = get_ig_stock_count(followers, require_password=require_pass)
        if stock == 0:
            bot.answer_callback_query(call.id, "❌ Out of stock! Admin notified.", show_alert=True)
            return
        balance = get_wallet(user_id)
        if balance < price:
            bot.answer_callback_query(call.id, f"❌ Insufficient funds! Need: {symbol}{price:,.2f}", show_alert=True)
            return
        ig_data = get_available_ig(followers, require_password=require_pass)
        if not ig_data:
            bot.answer_callback_query(call.id, "❌ Stock error!", show_alert=True)
            return
        update_wallet(user_id, -price)
        process_referral(user_id)
        update_admin_wallet(price, True)
        mark_ig_sold(ig_data['id'], user_id)
        delivery_text = f"🔗 INSTAGRAM: @{ig_data['ig_username']}"
        if require_pass and ig_data.get('password'):
            delivery_text += f"\n🔑 PASSWORD: {ig_data['password']}"
        order_id = create_order(user_id, "ig_link", f"{followers} Followers IG", 1, price, delivery_text)
        add_transaction(user_id, -price, 'purchase', order_id, 'completed')
        bot.edit_message_text(f"""
✅ ORDER CONFIRMED!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{delivery_text}

📸 FOLLOWERS: {followers}
💰 PAID: {symbol}{price:,.2f}

📦 ORDER ID: {order_id[:12]}...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 {MY_SIGNATURE}
""", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.answer_callback_query(call.id, "✅ Purchase successful!")
        return

    if data.startswith("buy_followers_"):
        followers = int(data.split("_")[2])
        price, rule_name = PricingEngine.get_price(followers)
        balance = get_wallet(user_id)
        if balance < price:
            bot.answer_callback_query(call.id, f"❌ Insufficient funds! Need: {symbol}{price:,.2f}", show_alert=True)
            return
        user_sessions[user_id] = {'state': 'buy_followers', 'followers': followers, 'price': price}
        bot.edit_message_text(f"📸 SELECTED: {followers} followers\n💰 PRICE: {symbol}{price:,.2f}\n\nSend your Instagram username (without @):\n\nExample: <code>john_doe123</code>\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler(call.message, process_buy_followers)
        return
    
    if data.startswith("buy_ig_"):
        try:
            followers = int(data.split("_")[2])
            price, rule_name = PricingEngine.get_price(followers)
            bot.edit_message_text("🔗 **SELECT IG LINK TYPE**", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=ig_type_keyboard(followers, price))
        except ValueError:
            bot.answer_callback_query(call.id, "❌ Invalid selection!", show_alert=True)
        return        
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ PURCHASE NOW", callback_data=f"confirm_buy_complete_ig_{item_id}"),
            types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
        )
        
        caption = f"""
🎁 **{item['product_name']}**

💰 Price: {symbol}{item['price']:,.2f}
🔗 Username: @{item['username']}
📸 Followers: {item['followers_count']:,}

📝 Description: {item['description'] if item['description'] else 'No description'}

Click PURCHASE to buy this account.
"""
        if item['screenshot_file_id']:
            bot.send_photo(call.message.chat.id, item['screenshot_file_id'], caption=caption, parse_mode='HTML', reply_markup=markup)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.edit_message_text(caption, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("confirm_buy_complete_ig_"):
        item_id = int(data.replace("confirm_buy_complete_ig_", ""))
        item = IGShopStock.get_item_by_id(item_id)
        if not item or item['status'] != 'available':
            bot.answer_callback_query(call.id, "❌ Item not available!", show_alert=True)
            return
        balance = get_wallet(user_id)
        if balance < item['price']:
            bot.answer_callback_query(call.id, f"❌ Insufficient funds! Need: {symbol}{item['price']:,.2f}", show_alert=True)
            return
        
        update_wallet(user_id, -item['price'])
        process_referral(user_id)
        update_admin_wallet(item['price'], True)
        IGShopStock.mark_sold(item_id, user_id)
        
        # Post to channel about this sale
        post_purchase_to_channel("complete_ig", item['product_name'], item['price'])
        
        order_id = IGShopOrder.create_order(user_id, item_id, item['product_name'], item['price'])
        add_transaction(user_id, -item['price'], 'purchase', order_id, 'completed')
        
        bot.edit_message_text(f"""
✅ **ORDER CONFIRMED!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 {item['product_name']}
💰 PAID: {symbol}{item['price']:,.2f}
🔗 Username: @{item['username']}

📦 ORDER ID: {order_id[:12]}...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
🔐 **Need verification code?** Click the button below to request the email/password if Instagram sends a verification code.

⚠️ You can request the account credentials now.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 {MY_SIGNATURE}
""", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔑 REQUEST EMAIL & PASSWORD", callback_data=f"request_credentials_{order_id}"))
        bot.send_message(user_id, "🔐 **VERIFICATION CODE NEEDED?**\n\nIf Instagram sends a verification code to the email, click below to request the email access.", parse_mode='HTML', reply_markup=markup)
        
        bot.answer_callback_query(call.id, "✅ Purchase successful!")
        return
    
    if data.startswith("request_credentials_"):
        order_id = data.replace("request_credentials_", "")
        order = IGShopOrder.get_order_by_id(order_id)
        if not order or order['user_id'] != user_id:
            bot.answer_callback_query(call.id, "❌ Invalid request!", show_alert=True)
            return
        
        c = db.cursor()
        c.execute("SELECT id FROM code_requests WHERE order_id = ? AND user_id = ? AND status = 'pending'", (order_id, user_id))
        existing = c.fetchone()
        if existing:
            bot.answer_callback_query(call.id, "⚠️ Request already pending! Admin will respond soon.", show_alert=True)
            return
        
        CodeRequestManager.create_request(user_id, order_id)
        bot.answer_callback_query(call.id, "✅ Request sent! Admin will provide the code shortly.", show_alert=True)
        
        # Send to master admin only
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✅ PROVIDE CODE", callback_data=f"provide_code_{order_id}"))
            bot.send_message(MASTER_ADMIN_ID, f"🔐 **CODE REQUEST**\n\nUser: {user_id}\nOrder ID: {order_id}\n\nProvide the verification code or credentials:", parse_mode='HTML', reply_markup=markup)
        except:
            pass
        return
    
    if data.startswith("provide_code_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        order_id = data.replace("provide_code_", "")
        order = IGShopOrder.get_order_by_id(order_id)
        if not order:
            bot.answer_callback_query(call.id, "❌ Order not found!", show_alert=True)
            return
        user_sessions[user_id] = {'state': 'provide_code', 'order_id': order_id, 'target_user': order['user_id']}
        bot.edit_message_text(f"✏️ **PROVIDE CODE/CREDENTIALS**\n\nOrder ID: {order_id}\nUser: {order['user_id']}\n\nSend the verification code or credentials to send to the user:", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_code_requests":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        requests = CodeRequestManager.get_pending_requests()
        if not requests:
            bot.edit_message_text("🔐 **NO PENDING CODE REQUESTS**", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for req in requests:
            markup.add(types.InlineKeyboardButton(f"🔐 User {req['user_id']} - Order {req['order_id'][:8]}...", callback_data=f"view_code_request_{req['id']}"))
        markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back"))
        bot.edit_message_text(f"🔐 **PENDING CODE REQUESTS** ({len(requests)})", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("view_code_request_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        request_id = int(data.replace("view_code_request_", ""))
        c = db.cursor()
        c.execute("SELECT user_id, order_id FROM code_requests WHERE id = ?", (request_id,))
        req = c.fetchone()
        if req:
            user_sessions[user_id] = {'state': 'provide_code', 'request_id': request_id, 'target_user': req['user_id']}
            bot.edit_message_text(f"✏️ **PROVIDE CODE**\n\nUser: {req['user_id']}\nOrder: {req['order_id']}\n\nSend the verification code or credentials:", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    # ========== FB BUY ==========
    if data.startswith("buy_fb_"):
        cat_id = int(data.replace("buy_fb_", ""))
        category = get_fb_category_by_id(cat_id)
        if not category:
            bot.answer_callback_query(call.id, "❌ Category not found!", show_alert=True)
            return
        
        stock = get_fb_stock_count(cat_id)
        if stock == 0:
            bot.answer_callback_query(call.id, "❌ Out of stock! Admin will restock soon.", show_alert=True)
            return
        
        balance = get_wallet(user_id)
        if balance < category['price']:
            bot.answer_callback_query(call.id, f"❌ Insufficient funds! Need: {symbol}{category['price']:,.2f}", show_alert=True)
            return
        
        fb_data = get_available_fb_account(cat_id)
        if not fb_data:
            bot.answer_callback_query(call.id, "❌ Stock error!", show_alert=True)
            return
        
        update_wallet(user_id, -category['price'])
        process_referral(user_id)
        update_admin_wallet(category['price'], True)
        mark_fb_sold(fb_data['id'], user_id)
        
        delivery_text = f"📧 **EMAIL:** {fb_data['email']}\n🔑 **PASSWORD:** {fb_data['password']}\n📂 **CATEGORY:** {category['display_name']}\n📅 **AGE:** {fb_data['account_age'] if fb_data['account_age'] else 'Unknown'}\n\n📌 **INSTRUCTIONS:**\n1️⃣ Login at Facebook.com\n2️⃣ Change password immediately\n3️⃣ Add phone number for security\n4️⃣ Enable 2FA if possible"
        
        order_id = create_order(user_id, "facebook", category['display_name'], 1, category['price'], delivery_text)
        add_transaction(user_id, -category['price'], 'purchase', order_id, 'completed')
        
        bot.edit_message_text(f"""
✅ **ORDER CONFIRMED!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{delivery_text}

💰 PAID: {symbol}{category['price']:,.2f}

📦 ORDER ID: {order_id[:12]}...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 {MY_SIGNATURE}
""", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        
        # Send to master admin only (no duplicates)
        try:
            bot.send_message(MASTER_ADMIN_ID, f"📘 FB SALE!\nUser: {user_id}\nAccount: {fb_data['email']}\nCategory: {category['display_name']}\nAmount: {symbol}{category['price']:,.2f}", parse_mode='HTML')
        except:
            pass
        
        bot.answer_callback_query(call.id, "✅ Purchase successful!")
        return
    
    # ========== PAYMENT METHODS ==========
    if data == "pay_opay":
        user_sessions[user_id] = {'payment_method': 'OPay'}
        min_deposit = int(get_setting('min_deposit', '500'))
        bot.edit_message_text(f"💰 ENTER AMOUNT TO DEPOSIT\n\nMinimum: {symbol}{min_deposit:,}\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler(call.message, process_fund_amount)
        return
    
    if data == "pay_palmpay":
        user_sessions[user_id] = {'payment_method': 'PalmPay'}
        min_deposit = int(get_setting('min_deposit', '500'))
        bot.edit_message_text(f"💰 ENTER AMOUNT TO DEPOSIT\n\nMinimum: {symbol}{min_deposit:,}\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler(call.message, process_fund_amount)
        return
    
    if data == "pay_bank":
        user_sessions[user_id] = {'payment_method': 'Bank Transfer'}
        min_deposit = int(get_setting('min_deposit', '500'))
        bot.edit_message_text(f"💰 ENTER AMOUNT TO DEPOSIT\n\nMinimum: {symbol}{min_deposit:,}\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler(call.message, process_fund_amount)
        return
    
    # ========== ADMIN PANEL ==========
    if data == "admin_payments":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        payments = get_pending_payments()
        if not payments:
            bot.edit_message_text("💰 NO PENDING PAYMENTS", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for pay in payments:
            markup.add(types.InlineKeyboardButton(f"💰 {symbol}{pay['amount']:,.0f} - User {pay['user_id']} - {pay['method']}", callback_data=f"view_payment_{pay['payment_id']}"))
        markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back"))
        bot.edit_message_text(f"💰 PENDING PAYMENTS ({len(payments)})", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("view_payment_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        payment_id = data.replace("view_payment_", "")
        c = db.cursor()
        c.execute("SELECT user_id, amount, method, image_file_id, timestamp FROM payments WHERE payment_id = ?", (payment_id,))
        payment = c.fetchone()
        if not payment:
            bot.answer_callback_query(call.id, "Payment not found!", show_alert=True)
            return
        caption = f"""
💰 PAYMENT DETAILS

👤 User: <code>{payment['user_id']}</code>
💰 Amount: {symbol}{payment['amount']:,.2f}
🏦 Method: {payment['method']}
📅 Date: {payment['timestamp'][:16]}

Click CONFIRM to credit user.
"""
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ CONFIRM", callback_data=f"confirm_payment_{payment_id}"),
            types.InlineKeyboardButton("❌ REJECT", callback_data=f"reject_payment_{payment_id}"),
            types.InlineKeyboardButton("◀️ BACK", callback_data="admin_payments")
        )
        if payment['image_file_id']:
            bot.send_photo(call.message.chat.id, payment['image_file_id'], caption=caption, parse_mode='HTML', reply_markup=markup)
        else:
            bot.edit_message_text(caption + "\n\n⚠️ No image provided.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        return
    
    if data == "stock_add_email":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("💰 **Enter the PRICE for these emails**\n\nSend a number like: `2000`\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        user_sessions[user_id] = {'state': 'add_email_price'}
        bot.register_next_step_handler(call.message, process_add_email_price)
        return
    
    if data == "stock_add_ig":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("💰 **Enter the PRICE for these IG accounts**\n\nSend a number like: `2000`\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        user_sessions[user_id] = {'state': 'add_ig_price'}
        bot.register_next_step_handler(call.message, process_add_ig_price)
        return
    
    if data == "stock_add_bulk":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("📦 **ADD BULK PACKAGE**\n\nUpload a `.txt` file with emails (one per line)\n\nThen type:\n`/bulk [followers_per_email] [price_per_email]`\n\nExample: First upload file, then:\n`/bulk 500 2000`\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        user_sessions[user_id] = {'state': 'add_bulk_stock'}
        return
    
    if data == "stock_add_complete_ig":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("💰 **Enter the PRICE for this complete IG account**\n\nSend a number like: `50000`\n\nType /cancel to cancel.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        user_sessions[user_id] = {'state': 'add_complete_ig_price'}
        bot.register_next_step_handler(call.message, process_add_complete_ig_price)
        return
    
    if data == "stock_view_email":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        stocks = get_all_email_stock()
        if not stocks:
            bot.edit_message_text("📧 NO EMAIL STOCK", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        msg = "📧 EMAIL STOCK\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for s in stocks[:50]:
            pwd_icon = "🔐" if s['has_password'] else "📧"
            status = "✅" if s['status'] == 'available' else "❌"
            msg += f"{status}{pwd_icon} {s['email']} (@{s['username']})\n   📸 {s['followers_count']} followers - {symbol}{s['price']:,.0f}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "stock_view_ig":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        stocks = get_all_ig_stock()
        if not stocks:
            bot.edit_message_text("🔗 NO IG STOCK", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        msg = "🔗 IG LINK STOCK\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for s in stocks[:50]:
            pwd_icon = "🔐" if s['has_password'] else "🔗"
            status = "✅" if s['status'] == 'available' else "❌"
            msg += f"{status}{pwd_icon} @{s['ig_username']}\n   📸 {s['followers_count']} followers - {symbol}{s['price']:,.0f}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "stock_view_bulk":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        stocks = get_all_bulk_stock()
        if not stocks:
            bot.edit_message_text("📦 NO BULK STOCK", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        msg = "📦 BULK STOCK\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for s in stocks[:50]:
            status = "✅" if s['status'] == 'available' else "❌"
            msg += f"{status} {s['emails_count']} emails x {s['followers_per_email']} followers\n   📊 Total: {s['total_followers']} - {symbol}{s['price']:,.0f}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "stock_view_complete_ig":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        stocks = IGShopStock.get_all_stock()
        if not stocks:
            bot.edit_message_text("🎁 NO COMPLETE IG STOCK", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        msg = "🎁 COMPLETE IG STOCK\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for s in stocks:
            status = "✅" if s['status'] == 'available' else "❌"
            sold_to = f" (Sold to {s['sold_to']})" if s['status'] == 'sold' else ""
            msg += f"{status} {s['product_name']}\n   🔗 @{s['username']} - {symbol}{s['price']:,.0f}{sold_to}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "stock_delete":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("🗑 **DELETE STOCK**\n\nSelect what to delete:", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=stock_delete_keyboard())
        return
    
    if data == "stock_delete_all":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🗑 DELETE ALL EMAIL", callback_data="delete_all_email_stock"),
            types.InlineKeyboardButton("🗑 DELETE ALL IG", callback_data="delete_all_ig_stock"),
            types.InlineKeyboardButton("🗑 DELETE ALL BULK", callback_data="delete_all_bulk_stock"),
            types.InlineKeyboardButton("🗑 DELETE ALL COMPLETE IG", callback_data="delete_all_complete_ig_stock"),
            types.InlineKeyboardButton("🗑 DELETE ALL FB", callback_data="delete_all_fb_stock"),
            types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back")
        )
        bot.edit_message_text("⚠️ **DELETE ALL STOCK - WARNING!**\n\nThis will delete ALL items in the selected category.\n\nSelect a category:", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data == "delete_all_email_stock":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        delete_all_email_stock()
        bot.answer_callback_query(call.id, "✅ All email stock deleted!", show_alert=True)
        bot.edit_message_text("✅ All email stock has been deleted.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "delete_all_ig_stock":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        delete_all_ig_stock()
        bot.answer_callback_query(call.id, "✅ All IG stock deleted!", show_alert=True)
        bot.edit_message_text("✅ All IG stock has been deleted.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "delete_all_complete_ig_stock":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        IGShopStock.delete_all_stock()
        bot.answer_callback_query(call.id, "✅ All complete IG stock deleted!", show_alert=True)
        bot.edit_message_text("✅ All complete IG stock has been deleted.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "delete_all_fb_stock":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        delete_all_fb_stock()
        bot.answer_callback_query(call.id, "✅ All FB stock deleted!", show_alert=True)
        bot.edit_message_text("✅ All FB stock has been deleted.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_users":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        users = get_all_users(limit=50)
        if not users:
            bot.edit_message_text("👥 NO USERS FOUND", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        msg = "👥 ALL USERS\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for u in users[:30]:
            status = "🚫" if u['is_banned'] else "✅"
            admin_tag = "👑" if u['is_admin'] else "👤"
            msg += f"{status}{admin_tag} <code>{u['user_id']}</code> - {u['first_name']}\n   💰 {symbol}{u['wallet_balance']:,.2f}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_grant":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("👑 GRANT ADMIN ACCESS\n\nUse: `/grantadmin USER_ID`\n\nExample: `/grantadmin 123456789`", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_revoke":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("🔧 REVOKE ADMIN ACCESS\n\nUse: `/revokeadmin USER_ID`\n\nExample: `/revokeadmin 123456789`", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_stats":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        stats = get_bot_stats()
        wallet = get_admin_wallet()
        msg = f"""
📊 BOT STATISTICS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 Users: {stats['total_users']:,}
🚫 Banned: {stats['banned_users']:,}
👑 Admins: {stats['admin_users']:,}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Orders: {stats['total_orders']:,}
💰 Sales: {symbol}{stats['total_sales']:,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Deposits Today: {symbol}{stats['deposits_today']:,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 Email Stock: {stats['email_stock']:,}
🔗 IG Stock: {stats['ig_stock']:,}
📦 Bulk Stock: {stats['bulk_stock']:,}
🎁 Complete IG: {stats['ig_shop_stock']:,}
📘 FB Stock: {stats['fb_stock']:,}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏳ Pending Payments: {stats['pending_payments']}
📤 Pending Withdrawals: {stats['pending_withdrawals']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏦 Admin Wallet: {symbol}{wallet['balance']:,.2f}
📈 Total Earned: {symbol}{wallet['total_earned']:,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 {MY_SIGNATURE}
"""
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_broadcast":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("📢 BROADCAST MESSAGE\n\nUse: `/broadcast MESSAGE`\n\nExample: `/broadcast Hello everyone!`", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_ban":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("🚫 BAN/UNBAN USER\n\nUse:\n`/ban USER_ID` - Ban user\n`/unban USER_ID` - Unban user", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_wallet":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        wallet = get_admin_wallet()
        msg = f"""
💰 ADMIN WALLET

**BALANCE:** {symbol}{wallet['balance']:,.2f}
**TOTAL EARNED:** {symbol}{wallet['total_earned']:,.2f}
**TOTAL WITHDRAWN:** {symbol}{wallet['total_withdrawn']:,.2f}
"""
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_withdrawals":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        withdrawals = get_pending_withdrawals()
        if not withdrawals:
            bot.edit_message_text("📤 NO PENDING WITHDRAWALS", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for wd in withdrawals:
            markup.add(types.InlineKeyboardButton(f"📤 {wd['bank_name']} - {symbol}{wd['amount']:,.0f} - User {wd['user_id']}", callback_data=f"view_withdrawal_{wd['withdraw_id']}"))
        markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back"))
        bot.edit_message_text(f"📤 PENDING WITHDRAWALS ({len(withdrawals)})", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("view_withdrawal_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        withdraw_id = data.replace("view_withdrawal_", "")
        c = db.cursor()
        c.execute("SELECT user_id, amount, bank_name, account_number, account_name, request_date FROM withdrawals WHERE withdraw_id = ?", (withdraw_id,))
        wd = c.fetchone()
        if not wd:
            bot.answer_callback_query(call.id, "Withdrawal not found!", show_alert=True)
            return
        msg = f"""
📤 WITHDRAWAL DETAILS

👤 User: <code>{wd['user_id']}</code>
💰 Amount: {symbol}{wd['amount']:,.2f}
🏦 Bank: {wd['bank_name']}
📋 Account: <code>{wd['account_number']}</code>
👤 Name: {wd['account_name']}
📅 Requested: {wd['request_date'][:16]}

Mark as completed after sending payment.
"""
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ MARK COMPLETED", callback_data=f"complete_withdrawal_{withdraw_id}"),
            types.InlineKeyboardButton("◀️ BACK", callback_data="admin_withdrawals")
        )
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("complete_withdrawal_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        withdraw_id = data.replace("complete_withdrawal_", "")
        complete_withdrawal(withdraw_id, user_id)
        bot.answer_callback_query(call.id, "✅ Withdrawal marked as completed!", show_alert=True)
        bot.edit_message_text("✅ WITHDRAWAL COMPLETED", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        c = db.cursor()
        c.execute("SELECT user_id FROM withdrawals WHERE withdraw_id = ?", (withdraw_id,))
        result = c.fetchone()
        if result:
            try:
                bot.send_message(result[0], "✅ WITHDRAWAL COMPLETED!\n\nYour withdrawal has been processed.", parse_mode='HTML')
            except:
                pass
        return
    
    if data == "admin_backup":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        backup_name = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = os.path.join("backups", backup_name)
        shutil.copy2('marketplace.db', backup_path)
        with open(backup_path, 'rb') as f:
            bot.send_document(user_id, f, caption=f"💾 DATABASE BACKUP\n\n{backup_name}", parse_mode='HTML')
        bot.edit_message_text("✅ BACKUP CREATED AND SENT!", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_back":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("🔧 ADMIN CONTROL PANEL", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=admin_keyboard())
        return
    
    if data == "back_main":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        if is_admin(user_id):
            bot.send_message(user_id, "🏠 MAIN MENU", parse_mode='HTML', reply_markup=main_keyboard(user_id))
        else:
            bot.send_message(user_id, "🏠 MAIN MENU", parse_mode='HTML', reply_markup=main_keyboard(user_id))
        return

# =================================================================================
# FB UPLOAD PROCESSORS
# =================================================================================

def process_fb_upload_price(message):
    user_id = message.from_user.id
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Upload cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    try:
        price = float(message.text.strip())
        if price <= 0:
            bot.reply_to(message, "❌ Price must be greater than 0!", parse_mode='HTML')
            bot.register_next_step_handler(message, process_fb_upload_price)
            return
        user_sessions[user_id]['fb_upload_price'] = price
        bot.reply_to(message, "📤 **SEND ACCOUNT DETAILS**\n\nFormat (one per line):\n`email|password|age`\n\nExamples:\n`user@gmail.com|pass123|2 years`\n\nType /cancel to cancel.", parse_mode='HTML')
        bot.register_next_step_handler(message, process_fb_upload_details)
    except:
        bot.reply_to(message, "❌ Invalid price! Send a number.", parse_mode='HTML')
        bot.register_next_step_handler(message, process_fb_upload_price)

def process_fb_upload_details(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    price = session.get('fb_upload_price')
    category_id = session.get('fb_upload_category')
    
    if not price or not category_id:
        bot.reply_to(message, "❌ Session expired. Start over.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Upload cancelled.", parse_mode='HTML')
        if user_id in user_sessions:
            del user_sessions[user_id]
        return
    
    # Check if message has text (account details)
    if message.text and not message.photo:
        # Store account text temporarily
        session['fb_account_text'] = message.text
        session['fb_screenshots'] = []
        bot.reply_to(message, "📸 **Now send the screenshot(s) of this Facebook account**\n\nSend 1 or more screenshots.\n\nType /done when finished.\nType /cancel to cancel.", parse_mode='HTML')
        bot.register_next_step_handler(message, process_fb_upload_screenshots)
    else:
        bot.reply_to(message, "❌ Please send account details first in format:\n`email|password|age`\n\nExample: `user@gmail.com|pass123|2 years`", parse_mode='HTML')
        bot.register_next_step_handler(message, process_fb_upload_details)

def process_fb_upload_screenshots(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    
    if message.text == '/done':
        # Save all data
        text = session.get('fb_account_text', '')
        screenshot_ids = session.get('fb_screenshots', [])
        price = session.get('fb_upload_price')
        category_id = session.get('fb_upload_category')
        
        if not screenshot_ids:
            bot.reply_to(message, "❌ No screenshots provided! Please send at least 1 screenshot.\n\nSend screenshot or type /cancel.", parse_mode='HTML')
            bot.register_next_step_handler(message, process_fb_upload_screenshots)
            return
        
        lines = text.strip().split('\n')
        added = 0
        failed = 0
        
        for line in lines:
            parts = line.split('|')
            if len(parts) >= 2:
                email = parts[0].strip()
                password = parts[1].strip()
                account_age = parts[2].strip() if len(parts) > 2 else ""
                
                screenshot_str = ','.join(screenshot_ids)
                
                if add_fb_stock(email, password, category_id, account_age, screenshot_str, price, user_id):
                    added += 1
                else:
                    failed += 1
        
        bot.reply_to(message, f"✅ **FB ACCOUNTS UPLOADED!**\n\n✅ Added: {added}\n❌ Failed: {failed}\n📸 Screenshots saved: {len(screenshot_ids)}", parse_mode='HTML')
        
        # Ask if user wants to continue
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ CONTINUE", callback_data="fb_continue_upload"),
            types.InlineKeyboardButton("❌ FINISH", callback_data="admin_back")
        )
        bot.reply_to(message, "📤 **Continue uploading?**\n\nClick CONTINUE to add more accounts.\nClick FINISH to exit.", parse_mode='HTML', reply_markup=markup)
        del user_sessions[user_id]
        return
    
    elif message.text == '/cancel':
        bot.reply_to(message, "❌ Upload cancelled.", parse_mode='HTML')
        del user_sessions[user_id]
        return
    
    elif message.photo:
        screenshot_ids = session.get('fb_screenshots', [])
        screenshot_ids.append(message.photo[-1].file_id)
        session['fb_screenshots'] = screenshot_ids
        bot.reply_to(message, f"📸 Screenshot {len(screenshot_ids)} saved!\n\nSend another screenshot or type /done to finish.", parse_mode='HTML')
        bot.register_next_step_handler(message, process_fb_upload_screenshots)
        return
    
    else:
        bot.reply_to(message, "❌ Please send a screenshot or type /done to finish.", parse_mode='HTML')
        bot.register_next_step_handler(message, process_fb_upload_screenshots)
        return

# =================================================================================
# MESSAGE HANDLER
# =================================================================================

@bot.message_handler(func=lambda message: not message.text or message.text.strip() == "")
def handle_empty(message):
    pass

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""
    
    if is_banned(user_id):
        bot.reply_to(message, "🚫 YOU ARE BANNED!", parse_mode='HTML')
        return
    
    # Session handlers
    if user_id in user_sessions:
        state = user_sessions[user_id].get('state')
        
        if state == 'withdraw':
            process_withdraw(message)
            return
        
        # ===== NEW HANDLERS START =====
        if state == 'waiting_email_followers':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled", reply_markup=main_keyboard(user_id))
                del user_sessions[user_id]
                return
            try:
                followers = int(text.strip())
                email = user_sessions[user_id].get('email')
                password = user_sessions[user_id].get('password')
                price, _ = PricingEngine.get_price(followers)
                success, msg = auto_add_email_to_stock(email, password, followers, price, user_id)
                bot.reply_to(message, f"📧 {msg}", parse_mode='HTML')
                del user_sessions[user_id]
            except:
                bot.reply_to(message, "❌ Send a valid number for followers!", parse_mode='HTML')
            return

        if state == 'waiting_ig_followers':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled", reply_markup=main_keyboard(user_id))
                del user_sessions[user_id]
                return
            try:
                followers = int(text.strip())
                username = user_sessions[user_id].get('username')
                password = user_sessions[user_id].get('password')
                price, _ = PricingEngine.get_price(followers)
                success, msg = auto_add_ig_account_to_stock(username, password, followers, price, user_id)
                bot.reply_to(message, f"🔗 {msg}", parse_mode='HTML')
                del user_sessions[user_id]
            except:
                bot.reply_to(message, "❌ Send a valid number for followers!", parse_mode='HTML')
            return

        if state == 'report_issue':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled", reply_markup=main_keyboard(user_id))
                del user_sessions[user_id]
                return
            issue = text if text else "No description"
            img_id = message.photo[-1].file_id if message.photo else None
            report_id = create_report(user_id, issue, img_id)
            bot.reply_to(message, f"✅ **REPORT SUBMITTED!**\n\n🆔 Report ID: `{report_id}`\n\nAdmin will review your issue.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            for admin in [MASTER_ADMIN_ID]:
                try:
                    if img_id:
                        bot.send_photo(admin, img_id, caption=f"📢 NEW REPORT\nUser: {user_id}\nID: {report_id}\nIssue: {issue}", parse_mode='HTML')
                    else:
                        bot.send_message(admin, f"📢 NEW REPORT\nUser: {user_id}\nID: {report_id}\nIssue: {issue}", parse_mode='HTML')
                except:
                    pass
            del user_sessions[user_id]
            return

        if state == 'expert_support':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled", reply_markup=main_keyboard(user_id))
                del user_sessions[user_id]
                return
            save_support_message(user_id, text)
            response = f"📞 For assistance, please contact @{BOT_USERNAME} directly.\n\n💎 {MY_SIGNATURE}"
            bot.reply_to(message, f"🤖 **SUPPORT**\n\n{response}", parse_mode='HTML', reply_markup=expert_support_keyboard())
            for admin in [MASTER_ADMIN_ID]:
                try:
                    bot.send_message(admin, f"💬 SUPPORT MESSAGE\nUser: {user_id}\nMessage: {text[:200]}", parse_mode='HTML')
                except:
                    pass
            del user_sessions[user_id]
            return

        if state == 'delete_ig_by_id':
            try:
                stock_id = int(text)
                delete_ig_stock(stock_id)
                bot.reply_to(message, f"✅ IG stock {stock_id} deleted!", parse_mode='HTML')
            except:
                bot.reply_to(message, "❌ Invalid ID!", parse_mode='HTML')
            del user_sessions[user_id]
            return

        if state == 'delete_bulk_by_id':
            try:
                stock_id = int(text)
                delete_bulk_stock(stock_id)
                bot.reply_to(message, f"✅ Bulk stock {stock_id} deleted!", parse_mode='HTML')
            except:
                bot.reply_to(message, "❌ Invalid ID!", parse_mode='HTML')
            del user_sessions[user_id]
            return

        if state == 'delete_complete_ig_by_id':
            try:
                stock_id = int(text)
                IGShopStock.delete_item(stock_id)
                bot.reply_to(message, f"✅ Complete IG stock {stock_id} deleted!", parse_mode='HTML')
            except:
                bot.reply_to(message, "❌ Invalid ID!", parse_mode='HTML')
            del user_sessions[user_id]
            return

        # =======q=== IMAGE BROADCAST HANDLER ==========
        if state == 'image_broadcast':
            if text == '/cancel':
                bot.reply_to(message, "❌ Broadcast cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            
            if not message.photo:
                bot.reply_to(message, "❌ Please send an image!", parse_mode='HTML')
                return
            
            caption = message.caption if message.caption else ""
            image_id = message.photo[-1].file_id
            
            c = db.cursor()
            c.execute("SELECT user_id FROM users WHERE is_banned = 0")
            users = [row[0] for row in c.fetchall()]
            
            success = 0
            failed = 0
            
            progress_msg = bot.reply_to(message, f"📢 Sending broadcast to {len(users)} users...", parse_mode='HTML')
            
            for uid in users:
                try:
                    bot.send_photo(uid, image_id, caption=f"📢 {caption}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                    success += 1
                except:
                    failed += 1
                time.sleep(0.05)
            
            bot.edit_message_text(f"✅ **BROADCAST COMPLETE!**\n\n✅ Sent: {success}\n❌ Failed: {failed}", progress_msg.chat.id, progress_msg.message_id, parse_mode='HTML')
            del user_sessions[user_id]
            return
    
    # ========== FB EDIT PRICE STATE ==========
        if state == 'fb_edit_price':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            
            parts = text.split('|')
            if len(parts) != 2:
                bot.reply_to(message, "❌ Invalid format! Use: account_id|new_price", parse_mode='HTML')
                return
            
            try:
                account_id = int(parts[0].strip())
                new_price = float(parts[1].strip())
                
                if new_price <= 0:
                    bot.reply_to(message, "❌ Price must be greater than 0!", parse_mode='HTML')
                    return
                
                c = db.cursor()
                c.execute("UPDATE fb_stock SET price = ? WHERE id = ?", (new_price, account_id))
                db.commit()
                
                symbol = get_setting('currency_symbol', '₦')
                bot.reply_to(message, f"✅ FB Account ID {account_id} price updated to {symbol}{new_price:,.0f}!", parse_mode='HTML')
                del user_sessions[user_id]
                
            except ValueError:
                bot.reply_to(message, "❌ Invalid ID or price! Send a number.", parse_mode='HTML')
            except Exception as e:
                bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')
            return
    
    # Main menu buttons
    symbol = get_setting('currency_symbol', '₦')
    
    if text == "🔧 ADMIN PANEL" and is_admin(user_id):
        bot.reply_to(message, "🔧 ADMIN CONTROL PANEL", parse_mode='HTML', reply_markup=admin_keyboard())
    elif text == "🛍 BUY FOLLOWERS":
        bot.reply_to(message, "📸 **HOW MANY FOLLOWERS DO YOU WANT?**\n\nSelect an option below:", parse_mode='HTML', reply_markup=followers_amount_keyboard())
    elif text == "📧 BUY EMAIL":
        bot.reply_to(message, "📧 **SELECT EMAIL PACKAGE:**", parse_mode='HTML', reply_markup=packages_keyboard("email"))
    elif text == "🔗 BUY IG LINK":
        bot.reply_to(message, "🔗 **SELECT IG LINK PACKAGE:**", parse_mode='HTML', reply_markup=packages_keyboard("ig"))
    elif text == "📦 BUY BULK":
        bot.reply_to(message, "📦 **SELECT BULK PACKAGE:**", parse_mode='HTML', reply_markup=packages_keyboard("bulk"))
    elif text == "🎁 BUY COMPLETE IG":
        bot.reply_to(message, "🎁 **SELECT COMPLETE IG ACCOUNT:**", parse_mode='HTML', reply_markup=complete_ig_keyboard())
    elif text == "📘 BUY FACEBOOK":
        bot.reply_to(message, "📘 **SELECT FACEBOOK ACCOUNT TYPE**", parse_mode='HTML', reply_markup=fb_categories_keyboard())
    elif text == "💰 MY WALLET":
        balance = get_wallet(user_id)
        bot.reply_to(message, f"💰 YOUR WALLET BALANCE\n\n{symbol}{balance:,.2f}\n\n📌 Withdraw: /withdraw\nMinimum: {symbol}{int(get_setting('min_withdrawal', '5000')):,}", parse_mode='HTML')
    elif text == "💳 FUND WALLET":
        bot.reply_to(message, "💳 SELECT PAYMENT METHOD:", parse_mode='HTML', reply_markup=payment_methods_keyboard())
    elif text == "📦 MY ORDERS":
        orders = get_user_orders(user_id)
        bulk_orders = get_user_bulk_orders(user_id)
        ig_shop_orders = IGShopOrder.get_user_orders(user_id)
        if not orders and not bulk_orders and not ig_shop_orders:
            bot.reply_to(message, "📦 NO ORDERS YET!", parse_mode='HTML')
        else:
            msg = "📦 YOUR ORDERS\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for order in orders[:10]:
                msg += f"✅ {order['product_name']}\n   💰 {symbol}{order['amount']:,.2f}\n   📅 {order['order_date'][:16]}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for order in bulk_orders[:10]:
                msg += f"✅ BULK: {order['total_emails']} emails x {order['followers_per_email']} followers\n   💰 {symbol}{order['amount']:,.2f}\n   📅 {order['order_date'][:16]}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for order in ig_shop_orders[:10]:
                msg += f"✅ COMPLETE IG: {order['product_name']}\n   💰 {symbol}{order['amount']:,.2f}\n   📅 {order['order_date'][:16]}\n   Status: {order['status']}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"💎 {MY_SIGNATURE}"
            bot.reply_to(message, msg, parse_mode='HTML')
    elif text == "📊 MY STATS":
        user = get_user(user_id)
        if user:
            msg = f"""
📊 YOUR STATISTICS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 BALANCE: {symbol}{user['wallet_balance']:,.2f}
💸 SPENT: {symbol}{user['total_spent']:,.2f}
📦 ORDERS: {user.get('total_orders', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 REFERRALS: {user.get('total_referrals', 0)}
💰 EARNINGS: {symbol}{user.get('referral_earnings', 0):,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 JOINED: {user['join_date'][:16]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 {MY_SIGNATURE}
"""
            bot.reply_to(message, msg, parse_mode='HTML')
    elif text == "👥 REFERRALS":
        user = get_user(user_id)
        if user:
            ref_count, ref_earnings = get_user_referral_stats(user_id)
            link = f"https://t.me/{BOT_USERNAME}?start={user['referral_code']}"
            bonus = int(get_setting('referral_bonus', '250'))
            msg = f"""
👥 REFERRAL PROGRAM

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 BONUS: {symbol}{bonus} per referral

YOUR STATS:
• Referrals: {ref_count}
• Earnings: {symbol}{ref_earnings:,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 YOUR LINK:
<code>{link}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Share this link with friends!
When they join and buy, you get {symbol}{bonus}!
"""
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📤 SHARE", url=f"https://t.me/share/url?url={link}&text=Join%20Hamzzy%20Marketplace!"))
            bot.reply_to(message, msg, parse_mode='HTML', reply_markup=markup)
    elif text == "🏆 LEADERBOARD":
        leaders = get_referral_leaderboard()
        if not leaders:
            bot.reply_to(message, "🏆 NO REFERRALS YET!", parse_mode='HTML')
        else:
            msg = "🏆 REFERRAL LEADERBOARD\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for i, leader in enumerate(leaders, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                msg += f"{medal} {leader['first_name'][:20]}\n   📊 {leader['total_referrals']} referrals | {symbol}{leader['referral_earnings']:,.0f}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"💎 {MY_SIGNATURE}"
            bot.reply_to(message, msg, parse_mode='HTML')
    elif text == "📜 HISTORY":
        transactions = get_user_transactions(user_id)
        if not transactions:
            bot.reply_to(message, "📜 NO TRANSACTIONS YET!", parse_mode='HTML')
        else:
            msg = "📜 TRANSACTION HISTORY\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for txn in transactions:
                sign = "+" if txn['amount'] > 0 else ""
                emoji = "✅" if txn['status'] == 'completed' else "⏳"
                msg += f"{emoji} {txn['type'].upper()}: {sign}{symbol}{abs(txn['amount']):,.2f}\n   📅 {txn['timestamp'][:16]}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"💎 {MY_SIGNATURE}"
            bot.reply_to(message, msg, parse_mode='HTML')
    elif text == "🔔 NOTIFICATIONS":
        c = db.cursor()
        c.execute("SELECT id, title, message, created_date FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY created_date DESC LIMIT 10", (user_id,))
        notifs = c.fetchall()
        if not notifs:
            bot.reply_to(message, "🔔 NO NEW NOTIFICATIONS!", parse_mode='HTML')
        else:
            msg = "🔔 YOUR NOTIFICATIONS\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for n in notifs:
                msg += f"📌 {n['title']}\n{n['message'][:200]}\n📅 {n['created_date'][:16]}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                c.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (n['id'],))
            db.commit()
            msg += f"💎 {MY_SIGNATURE}"
            bot.reply_to(message, msg, parse_mode='HTML')

    elif text == "📋 MY PURCHASES":
        c = db.cursor()
        
        # Get email purchases
        c.execute("SELECT product_name, amount, delivery_info, order_date FROM orders WHERE user_id = ? AND product_type = 'email' ORDER BY order_date DESC LIMIT 20", (user_id,))
        email_orders = c.fetchall()
        
        # Get IG purchases
        c.execute("SELECT product_name, amount, delivery_info, order_date FROM orders WHERE user_id = ? AND product_type = 'ig_link' ORDER BY order_date DESC LIMIT 20", (user_id,))
        ig_orders = c.fetchall()
        
        # Get Complete IG purchases
        c.execute("SELECT product_name, amount, delivery_info, order_date FROM ig_shop_orders WHERE user_id = ? ORDER BY order_date DESC LIMIT 20", (user_id,))
        complete_ig_orders = c.fetchall()
        
        # Get Facebook purchases
        c.execute("SELECT product_name, amount, delivery_info, order_date FROM orders WHERE user_id = ? AND product_type = 'facebook' ORDER BY order_date DESC LIMIT 20", (user_id,))
        fb_orders = c.fetchall()
        
        # Get Bulk purchases
        c.execute("SELECT product_name, amount, delivery_info, order_date FROM orders WHERE user_id = ? AND product_type = 'bulk' ORDER BY order_date DESC LIMIT 20", (user_id,))
        bulk_orders = c.fetchall()
        
        all_orders = []
        for order in email_orders:
            all_orders.append(('📧', order))
        for order in ig_orders:
            all_orders.append(('🔗', order))
        for order in complete_ig_orders:
            all_orders.append(('🎁', order))
        for order in fb_orders:
            all_orders.append(('📘', order))
        for order in bulk_orders:
            all_orders.append(('📦', order))
        
        if not all_orders:
            bot.reply_to(message, "📋 **NO PURCHASES YET!**\n\nClick the buttons below to buy something.", parse_mode='HTML')
            return
        
        msg = "📋 **YOUR PURCHASED LOGS**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for icon, order in all_orders[:10]:
            msg += f"{icon} {order['product_name']}\n"
            msg += f"💰 {symbol}{order['amount']:,.2f}\n"
            msg += f"📅 {order['order_date'][:16]}\n"
            msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"📄 **DELIVERY DETAILS:**\n{order['delivery_info']}\n"
            msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        bot.reply_to(message, msg, parse_mode='HTML')

    elif text == "🤖 EXPERT SUPPORT":
        bot.reply_to(message, "🤖 **EXPERT SUPPORT**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nDescribe your issue or question in detail.\n\nAn expert will respond to you within 24 hours.\n\n📝 **Tips:**\n• Be specific about your problem\n• Include order ID if related to a purchase\n• Add screenshots if needed\n\nType /cancel to cancel.\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💎 @hamzzyhacket", parse_mode='HTML')
        user_sessions[user_id] = {'state': 'expert_support'}

    elif text == "❓ HELP":
        msg = f"""
❓ HELP & SUPPORT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 HOW TO BUY:
1. Click product button (FOLLOWERS/EMAIL/IG LINK/BULK/COMPLETE IG/FACEBOOK)
2. Select package from price list
3. For followers: Send username
4. For email/IG: Choose type (with/without password)
5. For Complete IG: View screenshot, purchase, request credentials if needed
6. For Facebook: Select category, purchase, receive login details

📌 COMPLETE IG FEATURE:
• View account screenshot before buying
• Purchase with wallet balance
• Request email/password if verification code needed
• Admin provides code, you get credentials

📌 HOW TO FUND WALLET:
1. Click "💳 FUND WALLET"
2. Select payment method (OPay/PalmPay/Bank)
3. Enter amount
4. Send payment and SCREENSHOT
5. Admin confirms → Wallet credited

📌 HOW TO WITHDRAW:
Type: `/withdraw` → Follow the prompts

📌 REFERRAL PROGRAM:
Share your link → Get ₦250 per referral!

📞 SUPPORT:
• Admin: @hamzzyhacket
• Channel: https://t.me/hamzzylogs

💎 @hamzzyhacket
"""
        bot.reply_to(message, msg, parse_mode='HTML')
    else:
        # Auto-extract emails for admin
        if is_admin(user_id) and '@' in text and '.' in text:
            extracted = extract_emails_from_text(text)
            if extracted:
                added = 0
                results = []
                for item in extracted:
                    followers = item['followers']
                    if not followers:
                        bot.reply_to(message, f"❓ Could not detect followers for `{item['email']}`.\n\nSend followers count:", parse_mode='HTML')
                        user_sessions[user_id] = {'state': 'waiting_email_followers', 'email': item['email'], 'password': item.get('password', '')}
                        return
                    price = auto_price(followers)
                    if not price:
                        price, _ = PricingEngine.get_price(followers)
                    if not price:
                        results.append(f"❌ {item['email']} - No package for {followers} followers")
                        continue
                    success, msg = auto_add_email_to_stock(item['email'], item.get('password', ''), followers, price, user_id)
                    if success:
                        added += 1
                        results.append(f"✅ {msg}")
                    else:
                        results.append(f"❌ {msg}")
                if results:
                    bot.reply_to(message, f"📧 **EMAIL STOCK UPDATE**\n\n" + "\n".join(results[:15]) + f"\n\n✅ Added: {added}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML', reply_markup=main_keyboard(user_id))
                return
        
        bot.reply_to(message, "🏠 MAIN MENU", parse_mode='HTML', reply_markup=main_keyboard(user_id))

# =================================================================================
# BULK FILE COMMANDS
# ================================================================================= 

@bot.message_handler(commands=['bulk'])
def cmd_bulk(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    if session.get('state') != 'add_bulk_stock':
        bot.reply_to(message, "❌ Please use 'ADD BULK' from admin panel first!", parse_mode='HTML')
        return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "📝 USAGE: /bulk [followers_per_email] [price_per_email]\n\nExample: /bulk 500 2000", parse_mode='HTML')
        return
    try:
        followers_per_email = int(parts[1])
        price_per_email = float(parts[2])
        emails = session.get('bulk_emails', [])
        if not emails:
            bot.reply_to(message, "❌ No emails found. Upload a .txt file first.", parse_mode='HTML')
            return
        emails_count = len(emails)
        total_followers = emails_count * followers_per_email
        total_price = emails_count * price_per_email
        emails_str = "\n".join(emails)
        symbol = get_setting('currency_symbol', '₦')
        add_bulk_stock(emails_str, emails_count, followers_per_email, total_followers, total_price, user_id)
        bot.reply_to(message, f"""
✅ BULK PACKAGE ADDED!

📧 Emails: {emails_count}
📸 Per email: {followers_per_email} followers
📊 Total followers: {total_followers}
💰 Total price: {symbol}{total_price:,.2f}
💰 Price per email: {symbol}{price_per_email:,.0f}

This package is now available for purchase!
""", parse_mode='HTML')
        del user_sessions[user_id]['bulk_emails']
        del user_sessions[user_id]['state']
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(content_types=['document'])
def handle_bulk_file(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    if session.get('state') != 'add_bulk_stock':
        bot.reply_to(message, "❌ Please use 'ADD BULK' from admin panel first!", parse_mode='HTML')
        return
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        text = downloaded.decode('utf-8', errors='ignore')
        emails = [line.strip() for line in text.split('\n') if line.strip() and '@' in line]
        if not emails:
            bot.reply_to(message, "❌ No valid emails found in file!", parse_mode='HTML')
            return
        user_sessions[user_id]['bulk_emails'] = emails
        symbol = get_setting('currency_symbol', '₦')
        bot.reply_to(message, f"""
✅ FILE RECEIVED!

📧 Found {len(emails)} valid emails

Now type:
`/bulk [followers_per_email] [price_per_email]`

Example: `/bulk 500 2000`

This will create:
• {len(emails)} emails × 500 followers = {len(emails) * 500} total followers
• Total price: {symbol}{len(emails) * 2000:,.2f}
""", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Error reading file: {str(e)}", parse_mode='HTML')

# =================================================================================
# MISSING FUNCTIONS - ADD THIS ENTIRE BLOCK
# =================================================================================

def complete_ig_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    items = IGShopStock.get_available_items()
    symbol = get_setting('currency_symbol', '₦')
    
    for item in items[:10]:
        markup.add(types.InlineKeyboardButton(
            f"🎁 {item['product_name']} - {symbol}{item['price']:,.0f}", 
            callback_data=f"view_complete_ig_{item['id']}"
        ))
    
    if not items:
        markup.add(types.InlineKeyboardButton("❌ No items available - Ask admin to add stock", callback_data="back_main"))
    
    markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="back_main"))
    return markup

def fb_categories_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    categories = get_all_fb_categories()
    symbol = get_setting('currency_symbol', '₦')
    c = db.cursor()
    
    for cat in categories:
        c.execute("SELECT COUNT(*) FROM fb_stock WHERE category_id = ? AND status = 'available'", (cat['id'],))
        stock_count = c.fetchone()[0]
        
        stock_icon = "✅" if stock_count > 0 else "❌"
        display = f"📘 {cat['display_name']} - {symbol}{cat['price']:,.0f} [{stock_count} in stock] {stock_icon}"
        markup.add(types.InlineKeyboardButton(display, callback_data=f"buy_fb_category_{cat['id']}"))
    
    if not categories:
        markup.add(types.InlineKeyboardButton("❌ No categories available", callback_data="back_main"))
    
    markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="back_main"))
    return markup

def payment_methods_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💳 OPay", callback_data="pay_opay"),
        types.InlineKeyboardButton("💳 PalmPay", callback_data="pay_palmpay"),
        types.InlineKeyboardButton("🏦 Bank Transfer", callback_data="pay_bank"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
    )
    return markup

def email_type_keyboard(followers: int, price: float) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    email_only_stock = get_email_stock_count(followers)
    email_with_pass_stock = get_email_stock_count_with_pass(followers, require_password=True)
    extra_percent = int(get_setting('email_password_extra', '30'))
    price_with_pass = price * (1 + extra_percent / 100)
    symbol = get_setting('currency_symbol', '₦')
    
    markup.add(
        types.InlineKeyboardButton(f"📧 Email Only - {symbol}{price:,.0f} ({email_only_stock} in stock)", callback_data=f"buy_email_type_{followers}_{price}_only"),
        types.InlineKeyboardButton(f"🔐 Email + Password - {symbol}{price_with_pass:,.0f} ({email_with_pass_stock} in stock)", callback_data=f"buy_email_type_{followers}_{price_with_pass}_withpass"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
    )
    return markup

def get_email_stock_count_with_pass(followers: int, require_password: bool = False) -> int:
    c = db.cursor()
    if require_password:
        c.execute("SELECT COUNT(*) FROM email_stock WHERE followers_count = ? AND has_password = 1 AND status = 'available'", (followers,))
    else:
        c.execute("SELECT COUNT(*) FROM email_stock WHERE followers_count = ? AND status = 'available'", (followers,))
    return c.fetchone()[0]

def expert_support_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{BOT_USERNAME}"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
    )
    return markup

def auto_add_ig_account_to_stock(username: str, password: str, followers: int, price: float, admin_id: int) -> tuple:
    c = db.cursor()
    try:
        c.execute("INSERT INTO ig_stock (ig_username, password, has_password, followers_count, price, added_by, added_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'available')",
                  (username, password if password else None, 1 if password else 0, followers, price, admin_id, datetime.datetime.now().isoformat()))
        db.commit()
        return True, f"Added @{username} with {followers} followers @ ₦{price:,.0f}"
    except Exception as e:
        return False, f"Failed to add @{username}: {str(e)}"

def create_report(user_id: int, issue: str, image_id: str = None) -> str:
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS reports (report_id TEXT PRIMARY KEY, user_id INTEGER, issue TEXT, image_id TEXT, timestamp TEXT)")
    report_id = f"RPT{user_id}{int(time.time())}{random.randint(100, 999)}"
    c.execute("INSERT INTO reports (report_id, user_id, issue, image_id, timestamp) VALUES (?, ?, ?, ?, ?)",
              (report_id, user_id, issue, image_id, datetime.datetime.now().isoformat()))
    db.commit()
    return report_id

def save_support_message(user_id: int, message: str):
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS support_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message TEXT, timestamp TEXT)")
    c.execute("INSERT INTO support_messages (user_id, message, timestamp) VALUES (?, ?, ?)",
              (user_id, message, datetime.datetime.now().isoformat()))
    db.commit()

def broadcast_with_image(caption: str, image_id: str) -> tuple:
    c = db.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned = 0")
    users = [row[0] for row in c.fetchall()]
    success = 0
    failed = 0
    for uid in users:
        try:
            bot.send_photo(uid, image_id, caption=f"📢 ANNOUNCEMENT\n\n{caption}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            success += 1
        except:
            failed += 1
    return success, failed

def auto_price(followers: int) -> float:
    price, _ = PricingEngine.get_price(followers)
    return price

if __name__ == "__main__":
    print("=" * 80)
    print("🔥 HAMZZY MARKETPLACE BOT - COMPLETE WITH FB OPTION 🔥")
    print("=" * 80)
    print(f"👑 Master Admin: {MASTER_ADMIN_ID}")
    print(f"🤖 Bot: @{BOT_USERNAME}")
    print(f"💎 Created by: {MY_SIGNATURE}")
    print("=" * 80)
    print("✅ FEATURES INCLUDED:")
    print("   • Followers/Email/IG/Bulk products")
    print("   • COMPLETE IG ACCOUNTS with screenshots")
    print("   • FACEBOOK ACCOUNTS with categories")
    print("   • Verification code system")
    print("   • Admin can provide codes")
    print("   • Users can request credentials")
    print("   • Delete any stock individually")
    print("   • Delete all stock by category")
    print("   • Fully editable pricing")
    print("   • Multi-admin support")
    print("   • Auto-extract emails for admin")
    print("=" * 80)
    print("🚀 BOT IS RUNNING...")
    print("=" * 80)
    
    # ========== START AUTO-POST THREAD ==========
    try:
        auto_post_thread = threading.Thread(target=daily_stock_post, daemon=True)
        auto_post_thread.start()
        print("✅ Auto-post thread started (7:00 AM & 7:00 PM)")
    except Exception as e:
        print(f"❌ Failed to start auto-post thread: {e}")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except KeyboardInterrupt:
            print("\n❌ BOT STOPPED BY USER")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}")
            time.sleep(10)