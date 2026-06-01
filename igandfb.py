#!/usr/bin/env python3
"""
HAMZZY MARKETPLACE BOT - COMPLETE PROFESSIONAL VERSION
All features working: BUY IG, BUY FACEBOOK, Wallet Control, Referrals,
Admin Panel, Payment System, Withdrawals, Stock Management, Broadcasts,
Auto-Email Extraction, Low Stock Alerts, Daily Reports, Notifications
Channel: https://t.me/hamzzylogs
Author: @hamzzyhacket
Version: 8.0 - FULLY COMPLETE
"""

import telebot
from telebot import types
import sqlite3
import os  # ← MAKE SURE THIS IS PRESENT
import psycopg2  # ← ADD THIS
from psycopg2.extras import RealDictCursor  # ← ADD THIS
import time
import datetime
import json
import random
import re
import logging
import shutil
import threading
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

# =================================================================================
# CONFIGURATION
# =================================================================================

BOT_TOKEN = "8694523853:AAHsmwaN3VEW2oRrDX3YHhCZHakDnb3fp2U"
MASTER_ADMIN_ID = 7443685686
BOT_USERNAME = "Igtoolsandbypass_bot"  # ← CHANGED to avoid conflict with personal account
MY_SIGNATURE = "@hamzzyhacket"
CHANNEL_LINK = "https://t.me/hamzzylogs"
CHANNEL_USERNAME = "hamzzylogs"
REFERRAL_BONUS = 250

# Contact Info
CONTACT_PHONE = "09032741650"
CONTACT_EMAIL = "hamzzyhacket@gmail.com"
CONTACT_ADMIN = "@hamzzyhacket"

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
LOW_STOCK_THRESHOLD = 3

# IG PRICES
IG_PRICE_STRUCTURE = [
    (0, 39, 1000, "0-39 followers"),
    (50, 89, 2000, "50-89 followers"),
    (100, 180, 3000, "100-180 followers"),
    (200, 280, 3500, "200-280 followers"),
    (300, 380, 4000, "300-380 followers"),
    (400, 490, 4500, "400-490 followers"),
    (500, 580, 5000, "500-580 followers"),
    (600, 680, 6000, "600-680 followers"),
    (700, 790, 7000, "700-790 followers"),
    (800, 890, 8000, "800-890 followers"),
    (900, 980, 9000, "900-980 followers"),
    (1000, 1000, 10000, "1000+ followers"),
]

# VIP Levels
VIP_LEVELS = {
    'bronze': {'min_spent': 0, 'discount': 0, 'color': '🥉'},
    'silver': {'min_spent': 50000, 'discount': 5, 'color': '🥈'},
    'gold': {'min_spent': 150000, 'discount': 10, 'color': '🥇'},
    'platinum': {'min_spent': 500000, 'discount': 15, 'color': '💎'},
    'diamond': {'min_spent': 1000000, 'discount': 20, 'color': '👑'}
}

# Create directories
for dir_name in ["backups", "logs", "payment_images", "reports", "fb_screenshots"]:
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
# DATABASE
# =================================================================================

import os
import psycopg2
from psycopg2.extras import RealDictCursor

class Database:
    _instance = None
    _use_postgres = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # Check if running on Railway (has DATABASE_URL)
        self._use_postgres = os.environ.get('DATABASE_URL') is not None
        
        if self._use_postgres:
            self.conn = None
            self.init_postgres()
        else:
            self.conn = None
            self.init_sqlite()
    
    def connect(self):
        if self._use_postgres:
            if self.conn is None or self.conn.closed:
                self.conn = psycopg2.connect(os.environ.get('DATABASE_URL'), cursor_factory=RealDictCursor)
            return self.conn
        else:
            if self.conn is None:
                self.conn = sqlite3.connect('marketplace.db', check_same_thread=False, timeout=30)
                self.conn.row_factory = sqlite3.Row
                self.conn.execute("PRAGMA synchronous = OFF")
                self.conn.execute("PRAGMA journal_mode = WAL")
                self.conn.execute("PRAGMA cache_size = 10000")
            return self.conn
    
    def cursor(self):
        if self._use_postgres:
            return self.connect().cursor()
        else:
            return self.connect().cursor()
    
    def commit(self):
        if self.conn:
            self.conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def init_postgres(self):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            wallet_balance REAL DEFAULT 0,
            referral_code TEXT UNIQUE,
            referred_by BIGINT,
            total_referrals INTEGER DEFAULT 0,
            referral_earnings REAL DEFAULT 0,
            referral_bonus_given INTEGER DEFAULT 0,
            join_date TEXT,
            last_active TEXT,
            total_spent REAL DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0
        )''')
        
        # IG STOCK
        c.execute('''CREATE TABLE IF NOT EXISTS ig_stock (
            id SERIAL PRIMARY KEY,
            ig_username TEXT UNIQUE,
            password TEXT,
            has_password INTEGER DEFAULT 0,
            followers_count INTEGER,
            price REAL,
            status TEXT DEFAULT 'available',
            added_by BIGINT,
            added_date TEXT,
            sold_date TEXT,
            sold_to BIGINT
        )''')
        
        # FB CATEGORIES
        c.execute('''CREATE TABLE IF NOT EXISTS fb_categories (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
            email TEXT,
            password TEXT,
            category_id INTEGER,
            account_age TEXT,
            has_screenshot INTEGER DEFAULT 0,
            screenshot_file_ids TEXT,
            price REAL,
            status TEXT DEFAULT 'available',
            added_by BIGINT,
            added_date TEXT,
            sold_date TEXT,
            sold_to BIGINT
        )''')
        
        # Orders
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_id BIGINT,
            product_type TEXT,
            product_name TEXT,
            quantity INTEGER,
            amount REAL,
            delivery_info TEXT,
            order_date TEXT,
            status TEXT DEFAULT 'completed'
        )''')
        
        # Transactions
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
            txn_id TEXT PRIMARY KEY,
            user_id BIGINT,
            amount REAL,
            type TEXT,
            reference TEXT,
            status TEXT,
            timestamp TEXT,
            processed_by BIGINT
        )''')
        
        # Payments
        c.execute('''CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            user_id BIGINT,
            amount REAL,
            method TEXT,
            reference TEXT,
            image_file_id TEXT,
            status TEXT DEFAULT 'pending',
            timestamp TEXT,
            processed_by BIGINT,
            processed_date TEXT
        )''')
        
        # Withdrawals
        c.execute('''CREATE TABLE IF NOT EXISTS withdrawals (
            withdraw_id TEXT PRIMARY KEY,
            user_id BIGINT,
            amount REAL,
            bank_name TEXT,
            account_number TEXT,
            account_name TEXT,
            status TEXT DEFAULT 'pending',
            request_date TEXT,
            processed_date TEXT,
            processed_by BIGINT
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
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
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
        
        # Reports
        c.execute('''CREATE TABLE IF NOT EXISTS reports (
            report_id TEXT PRIMARY KEY,
            user_id BIGINT,
            issue TEXT,
            image_id TEXT,
            timestamp TEXT
        )''')
        
        # Support messages
        c.execute('''CREATE TABLE IF NOT EXISTS support_messages (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            message TEXT,
            timestamp TEXT
        )''')
        
        # Daily sales
        c.execute('''CREATE TABLE IF NOT EXISTS daily_sales (
            id SERIAL PRIMARY KEY,
            sale_date TEXT UNIQUE,
            total_sales REAL,
            total_orders INTEGER,
            total_users INTEGER,
            new_users INTEGER,
            report_sent INTEGER DEFAULT 0
        )''')
        
        # Default settings
        default_settings = [
            ('bot_name', 'Hamzzy Marketplace', 'Bot display name'),
            ('currency_symbol', '₦', 'Currency symbol'),
            ('min_deposit', '500', 'Minimum deposit'),
            ('min_withdrawal', '5000', 'Minimum withdrawal'),
            ('referral_bonus', '250', 'Referral bonus'),
            ('low_stock_threshold', '3', 'Low stock alert threshold'),
            ('contact_phone', CONTACT_PHONE, 'Contact phone'),
            ('contact_email', CONTACT_EMAIL, 'Contact email'),
            ('contact_admin', CONTACT_ADMIN, 'Contact admin'),
            ('auto_report_time', '08:00', 'Daily report time'),
        ]
        for key, value, desc in default_settings:
            c.execute('INSERT INTO bot_settings (setting_key, setting_value, description, updated_date) VALUES (%s, %s, %s, %s) ON CONFLICT (setting_key) DO NOTHING',
                      (key, value, desc, datetime.datetime.now().isoformat()))
        
        # Default FB categories
        default_fb_categories = [
            ("local_normal", "🇳🇬 Local Nigeria FB", 2000, 0, "Local Nigerian account", 1, 1),
            ("local_with_page", "🇳🇬 Local Nigeria FB + Page", 3500, 1, "Local account with page", 1, 2),
            ("foreign_normal", "🌍 Foreign FB", 3000, 0, "Foreign account", 1, 3),
            ("foreign_with_page", "🌍 Foreign FB + Page", 4500, 1, "Foreign account with page", 1, 4),
        ]
        for name, display, price, has_page, desc, active, order in default_fb_categories:
            c.execute('INSERT INTO fb_categories (name, display_name, price, has_page, description, is_active, sort_order, created_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (name) DO NOTHING',
                      (name, display, price, has_page, desc, active, order, datetime.datetime.now().isoformat()))
        
        # Admin wallet
        c.execute('SELECT COUNT(*) FROM admin_wallet')
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO admin_wallet (id, balance, total_earned, total_withdrawn, last_updated) VALUES (1, 0, 0, 0, %s)',
                      (datetime.datetime.now().isoformat(),))
        
        # Make master admin
        c.execute('UPDATE users SET is_admin = 1 WHERE user_id = %s', (MASTER_ADMIN_ID,))
        c.execute('INSERT INTO users (user_id, username, first_name, referral_code, join_date, last_active, is_admin, wallet_balance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (user_id) DO NOTHING',
                  (MASTER_ADMIN_ID, BOT_USERNAME, "Master Admin", f"rf_{MASTER_ADMIN_ID}", datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat(), 1, 0))
        
        # Create indexes
        c.execute('CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)')
        
        conn.commit()
        conn.close()
        print("✅ PostgreSQL database initialized")
    
    def init_sqlite(self):
        # Your existing SQLite initialization code here
        # (keep your original init_db code)
        c = self.cursor()
        
        # Users table with referral_bonus_given column
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            wallet_balance REAL DEFAULT 0,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            total_referrals INTEGER DEFAULT 0,
            referral_earnings REAL DEFAULT 0,
            referral_bonus_given INTEGER DEFAULT 0,
            join_date TEXT,
            last_active TEXT,
            total_spent REAL DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0
        )''')
        
        # IG STOCK
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
        
        # Payments with screenshot storage
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
        
        # Reports
        c.execute('''CREATE TABLE IF NOT EXISTS reports (
            report_id TEXT PRIMARY KEY,
            user_id INTEGER,
            issue TEXT,
            image_id TEXT,
            timestamp TEXT
        )''')
        
        # Support messages
        c.execute('''CREATE TABLE IF NOT EXISTS support_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            timestamp TEXT
        )''')
        
        # Daily sales
        c.execute('''CREATE TABLE IF NOT EXISTS daily_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_date TEXT UNIQUE,
            total_sales REAL,
            total_orders INTEGER,
            total_users INTEGER,
            new_users INTEGER,
            report_sent INTEGER DEFAULT 0
        )''')
        
        # Default settings
        default_settings = [
            ('bot_name', 'Hamzzy Marketplace', 'Bot display name'),
            ('currency_symbol', '₦', 'Currency symbol'),
            ('min_deposit', '500', 'Minimum deposit'),
            ('min_withdrawal', '5000', 'Minimum withdrawal'),
            ('referral_bonus', '250', 'Referral bonus'),
            ('low_stock_threshold', '3', 'Low stock alert threshold'),
            ('contact_phone', CONTACT_PHONE, 'Contact phone'),
            ('contact_email', CONTACT_EMAIL, 'Contact email'),
            ('contact_admin', CONTACT_ADMIN, 'Contact admin'),
            ('auto_report_time', '08:00', 'Daily report time'),
        ]
        for key, value, desc in default_settings:
            c.execute('INSERT OR IGNORE INTO bot_settings (setting_key, setting_value, description, updated_date) VALUES (?, ?, ?, ?)',
                      (key, value, desc, datetime.datetime.now().isoformat()))
        
        # Default FB categories
        default_fb_categories = [
            ("local_normal", "🇳🇬 Local Nigeria FB", 2000, 0, "Local Nigerian account", 1, 1),
            ("local_with_page", "🇳🇬 Local Nigeria FB + Page", 3500, 1, "Local account with page", 1, 2),
            ("foreign_normal", "🌍 Foreign FB", 3000, 0, "Foreign account", 1, 3),
            ("foreign_with_page", "🌍 Foreign FB + Page", 4500, 1, "Foreign account with page", 1, 4),
        ]
        for name, display, price, has_page, desc, active, order in default_fb_categories:
            c.execute('INSERT OR IGNORE INTO fb_categories (name, display_name, price, has_page, description, is_active, sort_order, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                      (name, display, price, has_page, desc, active, order, datetime.datetime.now().isoformat()))
        
        # Admin wallet
        c.execute('SELECT COUNT(*) FROM admin_wallet')
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO admin_wallet (id, balance, total_earned, total_withdrawn, last_updated) VALUES (1, 0, 0, 0, ?)',
                      (datetime.datetime.now().isoformat(),))
        
        # Make master admin
        c.execute('UPDATE users SET is_admin = 1 WHERE user_id = ?', (MASTER_ADMIN_ID,))
        c.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, referral_code, join_date, last_active, is_admin, wallet_balance) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                  (MASTER_ADMIN_ID, BOT_USERNAME, "Master Admin", f"rf_{MASTER_ADMIN_ID}", datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat(), 1, 0))
        
        # Add missing columns to existing database
        try:
            c.execute("ALTER TABLE users ADD COLUMN referral_bonus_given INTEGER DEFAULT 0")
            print("✅ Added referral_bonus_given column")
        except:
            pass
        
        # Create indexes for performance
        c.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)")
        
        self.commit()
        print("✅ SQLite database initialized")

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
        referral_code = f"rf_{user_id}"
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
    c.execute("SELECT wallet_balance FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row is None:
        c.execute("INSERT OR IGNORE INTO users (user_id, wallet_balance, join_date, last_active) VALUES (?, ?, ?, ?)",
                  (user_id, 0, datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat()))
        db.commit()
        current_balance = 0
    else:
        current_balance = row[0]
    new_balance = current_balance + amount
    c.execute("UPDATE users SET wallet_balance = ? WHERE user_id = ?", (new_balance, user_id))
    db.commit()
    return new_balance

def set_wallet(user_id: int, new_balance: float) -> float:
    """Set user wallet to exact amount"""
    if new_balance < 0:
        new_balance = 0
    c = db.cursor()
    c.execute("UPDATE users SET wallet_balance = ? WHERE user_id = ?", (new_balance, user_id))
    db.commit()
    return new_balance

def add_wallet(user_id: int, amount: float) -> float:
    """Add funds to user wallet"""
    return update_wallet(user_id, amount)

def remove_wallet(user_id: int, amount: float) -> float:
    """Remove funds from user wallet"""
    return update_wallet(user_id, -amount)

def get_wallet(user_id: int) -> float:
    c = db.cursor()
    c.execute("SELECT wallet_balance FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 0.0

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

def process_referral_bonus_on_purchase(user_id: int):
    """Give referral bonus to referrer when user makes first purchase"""
    user = get_user(user_id)
    if not user or not user.get('referred_by'):
        return
    
    # Check if bonus already given
    if user.get('referral_bonus_given', 0) == 1:
        return
    
    referrer_id = user['referred_by']
    bonus = int(get_setting('referral_bonus', '250'))
    
    # Add bonus to referrer
    update_wallet(referrer_id, bonus)
    add_transaction(referrer_id, bonus, 'referral_bonus', f'ref_{user_id}', 'completed')
    
    # Update referrer stats
    c = db.cursor()
    c.execute("UPDATE users SET total_referrals = total_referrals + 1, referral_earnings = referral_earnings + ? WHERE user_id = ?", (bonus, referrer_id))
    
    # Mark bonus as given
    c.execute("UPDATE users SET referral_bonus_given = 1 WHERE user_id = ?", (user_id,))
    db.commit()
    
    # Notify referrer
    try:
        bot.send_message(referrer_id, 
            f"🎉 **REFERRAL BONUS!**\n\n"
            f"💰 +₦{bonus:,.2f} added to your wallet!\n"
            f"👤 User @{user.get('username', 'someone')} made their first purchase!\n\n"
            f"💎 {MY_SIGNATURE}", 
            parse_mode='Markdown')
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
    c.execute("SELECT order_id, product_name, amount, delivery_info, order_date FROM orders WHERE user_id = ? ORDER BY order_date DESC LIMIT ?", (user_id, limit))
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
    add_notification(user_id, "Account Banned", "You have been banned. Contact admin for support.")
    try:
        bot.send_message(user_id, "🚫 YOU HAVE BEEN BANNED!\nContact admin for support.", parse_mode='HTML')
    except:
        pass

def unban_user(user_id: int):
    c = db.cursor()
    c.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    db.commit()
    add_notification(user_id, "Account Unbanned", "You have been unbanned. You can now use the bot.")
    try:
        bot.send_message(user_id, "✅ YOU HAVE BEEN UNBANNED!\nYou can now use the bot.", parse_mode='HTML')
    except:
        pass

def grant_admin(user_id: int):
    c = db.cursor()
    c.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
    db.commit()
    add_notification(user_id, "Admin Granted", "You have been granted admin access.")
    try:
        bot.send_message(user_id, "👑 You have been granted ADMIN access!\nUse /admin to access the panel.", parse_mode='HTML')
    except:
        pass

def revoke_admin(user_id: int):
    if user_id == MASTER_ADMIN_ID:
        return False
    c = db.cursor()
    c.execute("UPDATE users SET is_admin = 0 WHERE user_id = ?", (user_id,))
    db.commit()
    add_notification(user_id, "Admin Revoked", "Your admin access has been revoked.")
    try:
        bot.send_message(user_id, "❌ Your admin access has been revoked.", parse_mode='HTML')
    except:
        pass
    return True

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
    c.execute("SELECT COUNT(*) FROM ig_stock WHERE status = 'available'")
    ig_stock = c.fetchone()[0]
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
        'ig_stock': ig_stock, 'fb_stock': fb_stock,
        'pending_payments': pending_payments, 'pending_withdrawals': pending_withdrawals, 'deposits_today': deposits_today
    }

def create_withdrawal(user_id: int, amount: float, bank: str, account: str, name: str) -> str:
    c = db.cursor()
    withdraw_id = f"WDR{user_id}{int(time.time())}{random.randint(100, 999)}"
    c.execute("INSERT INTO withdrawals (withdraw_id, user_id, amount, bank_name, account_number, account_name, request_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (withdraw_id, user_id, amount, bank, account, name, datetime.datetime.now().isoformat()))
    db.commit()
    add_notification(user_id, "Withdrawal Requested", f"Your withdrawal request of ₦{amount:,.2f} has been submitted. Admin will process it soon.")
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
        add_notification(row[0], "Withdrawal Completed", "Your withdrawal has been processed and sent to your bank account.")
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
    new_balance = update_wallet(user_id, amount)
    add_transaction(user_id, amount, 'deposit', payment_id, 'completed', admin_id)
    update_admin_wallet(amount, True)
    db.commit()
    
    # Send notification to user
    add_notification(user_id, "Payment Confirmed", f"Your payment of ₦{amount:,.2f} has been confirmed. New balance: ₦{new_balance:,.2f}")
    try:
        bot.send_message(user_id, f"✅ PAYMENT CONFIRMED!\n\n💰 ₦{amount:,.2f} added to your wallet!\n\nNew balance: ₦{new_balance:,.2f}", parse_mode='HTML')
    except:
        pass
    
    return True, user_id, amount

def reject_payment(payment_id: str, admin_id: int):
    c = db.cursor()
    c.execute("UPDATE payments SET status = 'rejected', processed_by = ?, processed_date = ? WHERE payment_id = ?",
              (admin_id, datetime.datetime.now().isoformat(), payment_id))
    db.commit()
    c.execute("SELECT user_id FROM payments WHERE payment_id = ?", (payment_id,))
    row = c.fetchone()
    if row:
        add_notification(row[0], "Payment Rejected", "Your payment was rejected. Please submit a clear screenshot.")
        try:
            bot.send_message(row[0], "❌ PAYMENT REJECTED!\n\nYour payment was rejected. Please submit a clear screenshot.", parse_mode='HTML')
        except:
            pass

def check_low_stock():
    """Check for low stock and notify admin"""
    threshold = int(get_setting('low_stock_threshold', '3'))
    alerts = []
    symbol = get_setting('currency_symbol', '₦')
    
    c = db.cursor()
    c.execute("SELECT followers_count, COUNT(*) as stock FROM ig_stock WHERE status = 'available' GROUP BY followers_count")
    for row in c.fetchall():
        if row['stock'] < threshold:
            alerts.append(f"🔗 IG: {row['followers_count']} followers - Only {row['stock']} left")
    
    c.execute("SELECT fc.display_name, COUNT(*) as stock FROM fb_stock fs JOIN fb_categories fc ON fs.category_id = fc.id WHERE fs.status = 'available' GROUP BY fc.display_name")
    for row in c.fetchall():
        if row['stock'] < threshold:
            alerts.append(f"📘 FB: {row['display_name']} - Only {row['stock']} left")
    
    if alerts:
        msg = "⚠️ **LOW STOCK ALERT!**\n\n" + "\n".join(alerts) + f"\n\nThreshold: {threshold} items\n\n💎 {MY_SIGNATURE}"
        for admin in [MASTER_ADMIN_ID] + [a['user_id'] for a in get_all_admins()]:
            try:
                bot.send_message(admin, msg, parse_mode='Markdown')
            except:
                pass

def generate_daily_report():
    """Generate and send daily sales report to admin"""
    today = datetime.date.today().isoformat()
    c = db.cursor()
    
    c.execute("SELECT COUNT(*) FROM users WHERE date(join_date) = ?", (today,))
    new_users = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    c.execute("SELECT COALESCE(SUM(amount), 0) FROM orders WHERE date(order_date) = ?", (today,))
    today_sales = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM orders WHERE date(order_date) = ?", (today,))
    today_orders = c.fetchone()[0]
    
    c.execute("SELECT COALESCE(SUM(amount), 0) FROM orders")
    total_sales = c.fetchone()[0]
    
    c.execute("SELECT report_sent FROM daily_sales WHERE sale_date = ?", (today,))
    existing = c.fetchone()
    
    if not existing or existing['report_sent'] == 0:
        symbol = get_setting('currency_symbol', '₦')
        msg = f"📊 **DAILY SALES REPORT**\n📅 {today}\n\n"
        msg += f"💰 Sales Today: {symbol}{today_sales:,.2f}\n"
        msg += f"📦 Orders Today: {today_orders}\n"
        msg += f"👥 New Users: {new_users}\n"
        msg += f"👥 Total Users: {total_users:,}\n"
        msg += f"💰 Total Sales: {symbol}{total_sales:,.2f}\n\n"
        msg += f"💎 {MY_SIGNATURE}"
        
        for admin in [MASTER_ADMIN_ID] + [a['user_id'] for a in get_all_admins()]:
            try:
                bot.send_message(admin, msg, parse_mode='Markdown')
            except:
                pass
        
        if existing:
            c.execute("UPDATE daily_sales SET total_sales = ?, total_orders = ?, total_users = ?, new_users = ?, report_sent = 1 WHERE sale_date = ?",
                      (today_sales, today_orders, total_users, new_users, today))
        else:
            c.execute("INSERT INTO daily_sales (sale_date, total_sales, total_orders, total_users, new_users, report_sent) VALUES (?, ?, ?, ?, ?, 1)",
                      (today, today_sales, today_orders, total_users, new_users))
        db.commit()

def broadcast_with_image(caption: str, image_id: str) -> Tuple[int, int]:
    """Send image broadcast to all users"""
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
        time.sleep(0.05)
    return success, failed

def extract_emails_from_text(text: str) -> List[Dict]:
    """Extract emails, passwords, followers from any text"""
    results = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        email = None
        password = None
        followers = None
        
        # Pipe format: email|password|followers
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 1 and '@' in parts[0]:
                email = parts[0].strip()
            if len(parts) >= 2:
                password = parts[1].strip()
            if len(parts) >= 3 and parts[2].strip().isdigit():
                followers = int(parts[2].strip())
        
        # Colon format: email:password:followers
        elif ':' in line and not email:
            parts = line.split(':')
            if len(parts) >= 1 and '@' in parts[0]:
                email = parts[0].strip()
            if len(parts) >= 2:
                password = parts[1].strip()
            if len(parts) >= 3 and parts[2].strip().isdigit():
                followers = int(parts[2].strip())
        
        # Just email with underscore followers
        elif '@' in line:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
            if email_match:
                email = email_match.group()
                underscore_match = re.search(r'_(\d+)', email)
                if underscore_match:
                    followers = int(underscore_match.group(1))
                else:
                    numbers = re.findall(r'\b(\d+)\b', line)
                    if numbers:
                        followers = int(numbers[0])
        
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
# IG STOCK FUNCTIONS
# =================================================================================

def add_ig_stock(username: str, password: str, followers: int, price: float, admin_id: int, has_pass: bool = False) -> bool:
    c = db.cursor()
    try:
        c.execute("INSERT INTO ig_stock (ig_username, password, has_password, followers_count, price, added_by, added_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'available')",
                  (username, password if has_pass else None, 1 if has_pass else 0, followers, price, admin_id, datetime.datetime.now().isoformat()))
        db.commit()
        return True
    except:
        return False

def get_available_ig(followers_min: int, followers_max: int, require_password: bool = False) -> Optional[Dict]:
    c = db.cursor()
    if require_password:
        c.execute("SELECT id, ig_username, password, price FROM ig_stock WHERE followers_count BETWEEN ? AND ? AND has_password = 1 AND status = 'available' LIMIT 1", (followers_min, followers_max))
    else:
        c.execute("SELECT id, ig_username, password, price FROM ig_stock WHERE followers_count BETWEEN ? AND ? AND status = 'available' LIMIT 1", (followers_min, followers_max))
    row = c.fetchone()
    return dict(row) if row else None

def get_ig_stock_count(followers_min: int, followers_max: int, require_password: bool = False) -> int:
    c = db.cursor()
    if require_password:
        c.execute("SELECT COUNT(*) FROM ig_stock WHERE followers_count BETWEEN ? AND ? AND has_password = 1 AND status = 'available'", (followers_min, followers_max))
    else:
        c.execute("SELECT COUNT(*) FROM ig_stock WHERE followers_count BETWEEN ? AND ? AND status = 'available'", (followers_min, followers_max))
    return c.fetchone()[0]

def get_all_ig_stock() -> List[Dict]:
    c = db.cursor()
    c.execute("SELECT id, ig_username, has_password, followers_count, price, status FROM ig_stock ORDER BY id DESC")
    return [dict(row) for row in c.fetchall()]

def mark_ig_sold(ig_id: int, user_id: int):
    c = db.cursor()
    c.execute("UPDATE ig_stock SET status = 'sold', sold_date = ?, sold_to = ? WHERE id = ?",
              (datetime.datetime.now().isoformat(), user_id, ig_id))
    db.commit()

def delete_ig_stock(stock_id: int):
    c = db.cursor()
    c.execute("DELETE FROM ig_stock WHERE id = ?", (stock_id,))
    db.commit()

def delete_all_ig_stock():
    c = db.cursor()
    c.execute("DELETE FROM ig_stock")
    db.commit()

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

def update_fb_category_price(cat_id: int, new_price: float) -> bool:
    c = db.cursor()
    try:
        c.execute("UPDATE fb_categories SET price = ?, updated_date = ? WHERE id = ?", (new_price, datetime.datetime.now().isoformat(), cat_id))
        db.commit()
        return True
    except:
        return False

def delete_fb_category(cat_id: int) -> bool:
    c = db.cursor()
    try:
        # First delete all FB stock in this category
        c.execute("DELETE FROM fb_stock WHERE category_id = ?", (cat_id,))
        c.execute("DELETE FROM fb_categories WHERE id = ?", (cat_id,))
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
    c.execute("SELECT id, email, password, account_age, price, screenshot_file_ids FROM fb_stock WHERE category_id = ? AND status = 'available' LIMIT 1", (category_id,))
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
# KEYBOARDS
# =================================================================================

def main_keyboard(user_id: int = None) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if user_id and is_admin(user_id):
        buttons = ["🔧 ADMIN PANEL", "💰 MY WALLET", "💳 FUND WALLET", "📦 MY ORDERS", "🏆 LEADERBOARD", "📊 MY STATS", "👑 VIP STATUS", "👥 REFERRALS", "📜 HISTORY", "🔔 NOTIFICATIONS", "❓ HELP", "📢 REPORT ISSUE", "🤖 EXPERT SUPPORT"]
    else:
        buttons = ["🔗 BUY IG", "📘 BUY FACEBOOK", "💰 MY WALLET", "💳 FUND WALLET", "📦 MY ORDERS", "📊 MY STATS", "👥 REFERRALS", "🏆 LEADERBOARD", "📜 HISTORY", "🔔 NOTIFICATIONS", "❓ HELP", "📢 REPORT ISSUE", "🤖 EXPERT SUPPORT"]
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
        types.InlineKeyboardButton("💰 PENDING PAYMENTS", callback_data="admin_payments"),
        types.InlineKeyboardButton("🔗 IG MANAGEMENT", callback_data="admin_ig"),
        types.InlineKeyboardButton("📘 FB MANAGEMENT", callback_data="admin_fb"),
        types.InlineKeyboardButton("💰 MANAGE WALLETS", callback_data="admin_wallet_control"),
        types.InlineKeyboardButton("📤 WITHDRAWALS", callback_data="admin_withdrawals"),
        types.InlineKeyboardButton("👥 ALL USERS", callback_data="admin_users"),
        types.InlineKeyboardButton("👑 MANAGE ADMINS", callback_data="admin_manage_admins"),
        types.InlineKeyboardButton("📊 STATS", callback_data="admin_stats"),
        types.InlineKeyboardButton("📢 BROADCAST", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("📸 IMAGE BROADCAST", callback_data="admin_image_broadcast"),
        types.InlineKeyboardButton("🚫 BAN/UNBAN", callback_data="admin_ban"),
        types.InlineKeyboardButton("💰 ADMIN WALLET", callback_data="admin_wallet"),
        types.InlineKeyboardButton("💾 BACKUP", callback_data="admin_backup"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
    )
    return markup

def ig_management_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ ADD IG ACCOUNT", callback_data="add_ig_account"),
        types.InlineKeyboardButton("📋 VIEW IG STOCK", callback_data="view_ig_stock"),
        types.InlineKeyboardButton("🗑 DELETE IG STOCK", callback_data="delete_ig_stock"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back")
    )
    return markup

def fb_management_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📘 ADD FB CATEGORY", callback_data="fb_add_category"),
        types.InlineKeyboardButton("📧 ADD FB ACCOUNT", callback_data="fb_add_account"),
        types.InlineKeyboardButton("📋 VIEW FB STOCK", callback_data="fb_view_stock"),
        types.InlineKeyboardButton("✏️ EDIT CATEGORY PRICE", callback_data="fb_edit_category_price"),
        types.InlineKeyboardButton("🗑 DELETE FB CATEGORY", callback_data="fb_delete_category"),
        types.InlineKeyboardButton("🗑 DELETE FB STOCK", callback_data="fb_delete_stock"),
        types.InlineKeyboardButton("🗑 DELETE ALL FB", callback_data="fb_delete_all"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back")
    )
    return markup

def ig_packages_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    symbol = get_setting('currency_symbol', '₦')
    for min_f, max_f, price, desc in IG_PRICE_STRUCTURE:
        stock = get_ig_stock_count(min_f, max_f)
        stock_icon = "✅" if stock > 0 else "❌"
        display = f"🔗 {desc} - {symbol}{price:,.0f} [{stock} in stock] {stock_icon}"
        markup.add(types.InlineKeyboardButton(display, callback_data=f"buy_ig_{min_f}_{max_f}_{price}"))
    markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="back_main"))
    return markup

def ig_type_keyboard(followers_min: int, followers_max: int, price: float) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    symbol = get_setting('currency_symbol', '₦')
    only_stock = get_ig_stock_count(followers_min, followers_max, require_password=False)
    with_pass_stock = get_ig_stock_count(followers_min, followers_max, require_password=True)
    extra_percent = 30
    price_with_pass = price * (1 + extra_percent / 100)
    markup.add(
        types.InlineKeyboardButton(f"🔗 IG Only - {symbol}{price:,.0f} ({only_stock} in stock)", callback_data=f"buy_ig_only_{followers_min}_{followers_max}_{price}"),
        types.InlineKeyboardButton(f"🔐 IG + Password - {symbol}{price_with_pass:,.0f} ({with_pass_stock} in stock)", callback_data=f"buy_ig_withpass_{followers_min}_{followers_max}_{price_with_pass}"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
    )
    return markup

def fb_categories_keyboard() -> types.InlineKeyboardMarkup:
    categories = get_all_fb_categories()
    markup = types.InlineKeyboardMarkup(row_width=1)
    symbol = get_setting('currency_symbol', '₦')
    for cat in categories:
        stock_count = get_fb_stock_count(cat['id'])
        stock_icon = "✅" if stock_count > 0 else "❌"
        display = f"📘 {cat['display_name']} - {symbol}{cat['price']:,.0f} [{stock_count} in stock] {stock_icon}"
        markup.add(types.InlineKeyboardButton(display, callback_data=f"buy_fb_category_{cat['id']}"))
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

def expert_support_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{BOT_USERNAME}"),
        types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
    )
    return markup

def get_price_for_followers(followers: int) -> Optional[float]:
    for min_f, max_f, price, _ in IG_PRICE_STRUCTURE:
        if min_f <= followers <= max_f:
            return price
    return None

# =================================================================================
# COMMAND HANDLERS
# =================================================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "User"
    
    print(f"START - User: {user_id}, Name: {first_name}")
    
    if is_banned(user_id):
        bot.reply_to(message, "🚫 YOU ARE BANNED!", parse_mode='HTML')
        return
    
    # Handle referral
    referred_by = None
    if ' ' in message.text:
        ref_code = message.text.split()[1]
        print(f"Referral code: {ref_code}")
        
        # Check if it's a valid referral code
        c = db.cursor()
        c.execute("SELECT user_id FROM users WHERE referral_code = ?", (ref_code,))
        referrer = c.fetchone()
        
        if referrer and referrer[0] != user_id:
            referred_by = referrer[0]
            print(f"User referred by: {referred_by}")
    
    # Add or update user
    user = add_user(user_id, username, first_name)
    
    # Save referral ONLY if not already referred
    if referred_by and not user.get('referred_by'):
        c = db.cursor()
        c.execute("UPDATE users SET referred_by = ? WHERE user_id = ?", (referred_by, user_id))
        db.commit()
        print(f"Referral saved: {referred_by} referred {user_id}")
    
    symbol = get_setting('currency_symbol', '₦')
    referral_link = f"https://t.me/{BOT_USERNAME}?start={user['referral_code']}"
    bonus = int(get_setting('referral_bonus', '250'))
    
    msg = f"""
🔥 WELCOME TO HAMZZY LOGS 🔥

✨ Hello {first_name}!

✅ 100% LEGIT & ACTIVE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 REFERRAL PROGRAM

🔗 <code>{referral_link}</code>
🎁 {symbol}{bonus} per referral (when they make first purchase)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Use buttons below to shop

💎 {MY_SIGNATURE}
"""
    
    keyboard = main_keyboard(user_id)
    print(f"Keyboard generated, is_admin: {is_admin(user_id)}")
    
    try:
        bot.reply_to(message, msg, parse_mode='HTML', reply_markup=keyboard)
        print("Message sent successfully")
    except Exception as e:
        print(f"Error sending message: {e}")
        bot.reply_to(message, msg, parse_mode='HTML')

@bot.message_handler(commands=['admin'])
def cmd_admin(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "🚫 ADMIN ONLY!", parse_mode='HTML')
        return
    bot.reply_to(message, "🔧 **ADMIN CONTROL PANEL**", parse_mode='Markdown', reply_markup=admin_keyboard())

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
    success = 0
    for uid in users:
        try:
            bot.send_message(uid, f"📢 ANNOUNCEMENT\n\n{broadcast_text}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            success += 1
            add_notification(uid, "Announcement", broadcast_text[:200])
        except:
            pass
        time.sleep(0.05)
    bot.reply_to(message, f"✅ BROADCAST COMPLETE!\n\n✅ Sent: {success}\n❌ Failed: {len(users)-success}", parse_mode='HTML')

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
# PAYMENT FLOW HANDLERS
# =================================================================================

def process_fund_amount(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    method = session.get('payment_method')
    if not method:
        return
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
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
    try:
        bot.send_photo(MASTER_ADMIN_ID, photo.file_id, caption=caption, parse_mode='HTML', reply_markup=markup)
    except:
        pass
    del user_sessions[user_id]

def process_withdraw(message):
    user_id = message.from_user.id
    if message.text == '/cancel':
        bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
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
        try:
            bot.send_message(MASTER_ADMIN_ID, f"📤 NEW WITHDRAWAL\n\nUser: {user_id}\nAmount: {symbol}{amount:,.2f}\nBank: {bank}\nID: {withdraw_id}", parse_mode='HTML')
        except:
            pass
        del user_sessions[user_id]
    except:
        bot.reply_to(message, "❌ Error processing withdrawal!", parse_mode='HTML')

# =================================================================================
# CALLBACK HANDLERS
# =================================================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    data = call.data
    symbol = get_setting('currency_symbol', '₦')
    
    # ========== BUY IG FLOW ==========
    if data.startswith("buy_ig_"):
        parts = data.split("_")
        followers_min = int(parts[2])
        followers_max = int(parts[3])
        price = float(parts[4])
        
        stock = get_ig_stock_count(followers_min, followers_max)
        if stock == 0:
            bot.answer_callback_query(call.id, f"❌ No IG accounts in this range!", show_alert=True)
            return
        
        markup = ig_type_keyboard(followers_min, followers_max, price)
        bot.edit_message_text(
            f"🔗 **IG PACKAGE: {followers_min}-{followers_max} followers**\n\n💰 Price: {symbol}{price:,.0f}\n📦 Available: {stock}\n\nSelect option:",
            call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup
        )
        return
    
    if data.startswith("buy_ig_only_"):
        parts = data.split("_")
        followers_min = int(parts[3])
        followers_max = int(parts[4])
        price = float(parts[5])
        
        ig_data = get_available_ig(followers_min, followers_max, require_password=False)
        if not ig_data:
            bot.answer_callback_query(call.id, "❌ Out of stock!", show_alert=True)
            return
        
        balance = get_wallet(user_id)
        if balance < price:
            bot.answer_callback_query(call.id, f"❌ Need {symbol}{price:,.2f}", show_alert=True)
            return
        
        update_wallet(user_id, -price)
        update_admin_wallet(price, True)
        mark_ig_sold(ig_data['id'], user_id)
        
        # Give referral bonus if this is first purchase
        process_referral_bonus_on_purchase(user_id)
        
        delivery = f"🔗 INSTAGRAM: @{ig_data['ig_username']}\n🔑 PASSWORD: No password included\n📸 Followers: {followers_min}-{followers_max}"
        order_id = create_order(user_id, "ig", f"{followers_min}-{followers_max} followers", 1, price, delivery)
        add_transaction(user_id, -price, 'purchase', order_id, 'completed')
        add_notification(user_id, "Purchase Complete", f"You purchased IG account with {followers_min}-{followers_max} followers")
        
        bot.edit_message_text(
            f"✅ ORDER CONFIRMED!\n\n{delivery}\n\n💰 Paid: {symbol}{price:,.2f}\n📦 Order ID: {order_id[:12]}...\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        bot.answer_callback_query(call.id, "✅ Purchase successful!")
        return
    
    if data.startswith("buy_ig_withpass_"):
        parts = data.split("_")
        followers_min = int(parts[3])
        followers_max = int(parts[4])
        price = float(parts[5])
        
        ig_data = get_available_ig(followers_min, followers_max, require_password=True)
        if not ig_data:
            bot.answer_callback_query(call.id, "❌ Out of stock!", show_alert=True)
            return
        
        balance = get_wallet(user_id)
        if balance < price:
            bot.answer_callback_query(call.id, f"❌ Need {symbol}{price:,.2f}", show_alert=True)
            return
        
        update_wallet(user_id, -price)
        update_admin_wallet(price, True)
        mark_ig_sold(ig_data['id'], user_id)
        
        # Give referral bonus if this is first purchase
        process_referral_bonus_on_purchase(user_id)
        
        delivery = f"🔗 INSTAGRAM: @{ig_data['ig_username']}\n🔑 PASSWORD: {ig_data['password']}\n📸 Followers: {followers_min}-{followers_max}"
        order_id = create_order(user_id, "ig", f"{followers_min}-{followers_max} followers", 1, price, delivery)
        add_transaction(user_id, -price, 'purchase', order_id, 'completed')
        add_notification(user_id, "Purchase Complete", f"You purchased IG account with {followers_min}-{followers_max} followers")
        
        bot.edit_message_text(
            f"✅ ORDER CONFIRMED!\n\n{delivery}\n\n💰 Paid: {symbol}{price:,.2f}\n📦 Order ID: {order_id[:12]}...\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        bot.answer_callback_query(call.id, "✅ Purchase successful!")
        return
    
    # ========== BUY FB FLOW ==========
    if data.startswith("buy_fb_category_"):
        cat_id = int(data.replace("buy_fb_category_", ""))
        category = get_fb_category_by_id(cat_id)
        if not category:
            bot.answer_callback_query(call.id, "❌ Category not found!", show_alert=True)
            return
        
        stock = get_fb_stock_count(cat_id)
        if stock == 0:
            bot.answer_callback_query(call.id, f"❌ No {category['display_name']} in stock!", show_alert=True)
            return
        
        balance = get_wallet(user_id)
        if balance < category['price']:
            bot.answer_callback_query(call.id, f"❌ Need {symbol}{category['price']:,.2f}", show_alert=True)
            return
        
        fb_data = get_available_fb_account(cat_id)
        if not fb_data:
            bot.answer_callback_query(call.id, "❌ Stock error!", show_alert=True)
            return
        
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ CONFIRM PURCHASE", callback_data=f"confirm_fb_buy_{fb_data['id']}_{category['price']}_{cat_id}"),
            types.InlineKeyboardButton("◀️ BACK", callback_data="back_main")
        )
        
        caption = f"""
📘 **FACEBOOK ACCOUNT**

📂 Category: {category['display_name']}
💰 Price: {symbol}{category['price']:,.2f}
📅 Age: {fb_data['account_age'] if fb_data['account_age'] else 'Unknown'}

💳 Your balance: {symbol}{balance:,.2f}

Click CONFIRM to purchase.
"""
        if fb_data['screenshot_file_ids']:
            screenshot_ids = fb_data['screenshot_file_ids'].split(',')
            bot.send_photo(call.message.chat.id, screenshot_ids[0], caption=caption, parse_mode='HTML', reply_markup=markup)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.edit_message_text(caption, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("confirm_fb_buy_"):
        parts = data.split("_")
        fb_id = int(parts[3])
        price = float(parts[4])
        cat_id = int(parts[5])
        
        c = db.cursor()
        c.execute("SELECT * FROM fb_stock WHERE id = ? AND status = 'available'", (fb_id,))
        fb_data = c.fetchone()
        if not fb_data:
            bot.answer_callback_query(call.id, "❌ Account not available!", show_alert=True)
            return
        
        balance = get_wallet(user_id)
        if balance < price:
            bot.answer_callback_query(call.id, f"❌ Need {symbol}{price:,.2f}", show_alert=True)
            return
        
        update_wallet(user_id, -price)
        update_admin_wallet(price, True)
        mark_fb_sold(fb_id, user_id)
        
        # Give referral bonus if this is first purchase
        process_referral_bonus_on_purchase(user_id)
        
        category = get_fb_category_by_id(cat_id)
        delivery = f"""
✅ **FACEBOOK ACCOUNT DELIVERED!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 Email: {fb_data['email']}
🔑 Password: {fb_data['password']}
📂 Category: {category['display_name']}
📅 Age: {fb_data['account_age'] if fb_data['account_age'] else 'Unknown'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 **INSTRUCTIONS:**
1️⃣ Always use VPN for foreign FB accounts
2️⃣ Login and wait 2-3 hours before use
3️⃣ For support: {CONTACT_PHONE}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Paid: {symbol}{price:,.2f}
💳 New Balance: {symbol}{get_wallet(user_id):,.2f}

💎 {MY_SIGNATURE}
"""
        order_id = create_order(user_id, "facebook", category['display_name'], 1, price, delivery)
        add_transaction(user_id, -price, 'purchase', order_id, 'completed')
        add_notification(user_id, "Purchase Complete", f"You purchased a {category['display_name']} Facebook account")
        
        bot.send_message(call.message.chat.id, delivery, parse_mode='HTML')
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Purchase successful!")
        return
    
    # ========== ADMIN IG MANAGEMENT ==========
    if data == "admin_ig":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("🔗 **IG MANAGEMENT**", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=ig_management_keyboard())
        return
    
    if data == "add_ig_account":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text(
            "➕ **ADD IG ACCOUNT**\n\nSend in format:\n`username|followers|password`\n\nExample:\n`john_doe|500|pass123`\n\nIf no password, send:\n`john_doe|500|none`\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        user_sessions[user_id] = {'state': 'add_ig_account'}
        return
    
    if data == "view_ig_stock":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        stocks = get_all_ig_stock()
        if not stocks:
            bot.edit_message_text("🔗 NO IG STOCK", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        msg = "🔗 IG STOCK\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for s in stocks[:50]:
            pwd_icon = "🔐" if s['has_password'] else "🔗"
            status = "✅" if s['status'] == 'available' else "❌"
            msg += f"{status}{pwd_icon} @{s['ig_username']}\n   📸 {s['followers_count']} followers - {symbol}{s['price']:,.0f}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"💎 {MY_SIGNATURE}"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "delete_ig_stock":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text(
            "🗑 **DELETE IG STOCK**\n\nSend the IG stock ID to delete.\n\nView IDs from VIEW IG STOCK.\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        user_sessions[user_id] = {'state': 'delete_ig_by_id'}
        return
    
    # ========== ADMIN FB MANAGEMENT ==========
    if data == "admin_fb":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("📘 **FB MANAGEMENT**", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=fb_management_keyboard())
        return
    
    if data == "fb_add_category":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text(
            "➕ **ADD FB CATEGORY**\n\nSend in format:\n`name|display_name|price|has_page`\n\nExample:\n`local_premium|🇳🇬 Premium Nigeria FB|5000|1`\n\nhas_page: 0=No page, 1=Has page\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
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
        bot.edit_message_text("📤 **SELECT FB CATEGORY**", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("fb_upload_category_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        cat_id = int(data.replace("fb_upload_category_", ""))
        user_sessions[user_id] = {'state': 'fb_upload_price', 'fb_upload_category': cat_id}
        bot.edit_message_text(
            "💰 **Enter the PRICE for these FB accounts**\n\nSend a number like: `2000`\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        bot.register_next_step_handler(call.message, process_fb_upload_price)
        return
    
    if data == "fb_view_stock":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        stocks = get_all_fb_stock()
        if not stocks:
            bot.edit_message_text("📘 NO FB ACCOUNTS IN STOCK", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        msg = "📘 FB STOCK\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for s in stocks[:50]:
            msg += f"✅ ID {s['id']} | {s['email']}\n   📂 {s['category_name']} | {symbol}{s['price']:,.0f} | Age: {s['account_age']}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"💎 {MY_SIGNATURE}"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "fb_edit_category_price":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        categories = get_all_fb_categories()
        markup = types.InlineKeyboardMarkup(row_width=1)
        for cat in categories:
            markup.add(types.InlineKeyboardButton(f"✏️ {cat['display_name']} - {symbol}{cat['price']:,.0f}", callback_data=f"fb_edit_price_{cat['id']}"))
        markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="admin_fb"))
        bot.edit_message_text("✏️ **SELECT CATEGORY TO EDIT**", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("fb_edit_price_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        cat_id = int(data.replace("fb_edit_price_", ""))
        user_sessions[user_id] = {'state': 'fb_edit_category_price', 'cat_id': cat_id}
        bot.edit_message_text(
            "✏️ **ENTER NEW PRICE**\n\nSend the new price for this category:\n\nExample: `3000`\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        return
    
    if data == "fb_delete_category":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        categories = get_all_fb_categories()
        markup = types.InlineKeyboardMarkup(row_width=1)
        for cat in categories:
            markup.add(types.InlineKeyboardButton(f"🗑 DELETE {cat['display_name']}", callback_data=f"fb_delete_cat_{cat['id']}"))
        markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="admin_fb"))
        bot.edit_message_text("🗑 **DELETE FB CATEGORY**\n\n⚠️ This will also delete all FB accounts in this category!\n\nSelect a category to delete:", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("fb_delete_cat_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        cat_id = int(data.replace("fb_delete_cat_", ""))
        confirm_markup = types.InlineKeyboardMarkup()
        confirm_markup.add(
            types.InlineKeyboardButton("✅ YES, DELETE", callback_data=f"confirm_fb_delete_cat_{cat_id}"),
            types.InlineKeyboardButton("❌ NO, CANCEL", callback_data="admin_fb")
        )
        bot.edit_message_text("⚠️ **ARE YOU SURE?**\n\nThis will delete the category AND all FB accounts in it.\n\nThis action cannot be undone.\n\nClick YES to confirm.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=confirm_markup)
        return
    
    if data.startswith("confirm_fb_delete_cat_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        cat_id = int(data.replace("confirm_fb_delete_cat_", ""))
        if delete_fb_category(cat_id):
            bot.answer_callback_query(call.id, "✅ Category deleted!", show_alert=True)
            bot.edit_message_text("✅ Category and all its accounts have been deleted.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        else:
            bot.answer_callback_query(call.id, "❌ Failed to delete!", show_alert=True)
        return
    
    if data == "fb_delete_stock":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text(
            "🗑 **DELETE FB STOCK**\n\nSend the FB Account ID to delete.\n\nView IDs from VIEW FB STOCK.\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        user_sessions[user_id] = {'state': 'delete_fb_by_id'}
        return
    
    if data == "fb_delete_all":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        confirm_markup = types.InlineKeyboardMarkup()
        confirm_markup.add(
            types.InlineKeyboardButton("⚠️ YES, DELETE ALL", callback_data="confirm_fb_delete_all"),
            types.InlineKeyboardButton("❌ NO, CANCEL", callback_data="admin_fb")
        )
        bot.edit_message_text("⚠️ **DELETE ALL FB STOCK?**\n\nThis will delete ALL Facebook accounts from stock.\n\nThis action cannot be undone.\n\nClick YES to confirm.", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=confirm_markup)
        return
    
    if data == "confirm_fb_delete_all":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        delete_all_fb_stock()
        bot.answer_callback_query(call.id, "✅ All FB stock deleted!", show_alert=True)
        bot.edit_message_text("✅ All FB stock has been deleted.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    # ========== ADMIN WALLET CONTROL ==========
    if data == "admin_wallet_control":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("➕ ADD FUNDS", callback_data="wallet_add"),
            types.InlineKeyboardButton("➖ REMOVE FUNDS", callback_data="wallet_remove"),
            types.InlineKeyboardButton("✏️ SET BALANCE", callback_data="wallet_set"),
            types.InlineKeyboardButton("🔍 CHECK BALANCE", callback_data="wallet_check"),
            types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back")
        )
        bot.edit_message_text("💰 **WALLET CONTROL PANEL**\n\nSelect action:", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data == "wallet_add":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text(
            "➕ **ADD FUNDS**\n\nSend: `USER_ID|AMOUNT`\n\nExample: `7443685686|5000`\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        user_sessions[user_id] = {'state': 'wallet_add'}
        return
    
    if data == "wallet_remove":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text(
            "➖ **REMOVE FUNDS**\n\nSend: `USER_ID|AMOUNT`\n\nExample: `7443685686|2000`\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        user_sessions[user_id] = {'state': 'wallet_remove'}
        return
    
    if data == "wallet_set":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text(
            "✏️ **SET EXACT BALANCE**\n\nSend: `USER_ID|NEW_BALANCE`\n\nExample: `7443685686|10000`\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        user_sessions[user_id] = {'state': 'wallet_set'}
        return
    
    if data == "wallet_check":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text(
            "🔍 **CHECK BALANCE**\n\nSend USER_ID:\n\nExample: `7443685686`\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        user_sessions[user_id] = {'state': 'wallet_check'}
        return
    
    # ========== ADMIN PAYMENTS ==========
    if data == "admin_payments":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        payments = get_pending_payments()
        if not payments:
            bot.edit_message_text("💰 NO PENDING PAYMENTS", call.message.chat.id, call.message.message_id, parse_mode='HTML')
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for p in payments:
            markup.add(types.InlineKeyboardButton(f"💰 {symbol}{p['amount']:,.0f} - User {p['user_id']} - {p['method']}", callback_data=f"view_payment_{p['payment_id']}"))
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
        caption = f"💰 PAYMENT DETAILS\n\n👤 User: <code>{payment['user_id']}</code>\n💰 Amount: {symbol}{payment['amount']:,.2f}\n🏦 Method: {payment['method']}\n📅 Date: {payment['timestamp'][:16]}\n\nClick CONFIRM to credit user."
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ CONFIRM", callback_data=f"confirm_payment_{payment_id}"),
            types.InlineKeyboardButton("❌ REJECT", callback_data=f"reject_payment_{payment_id}"),
            types.InlineKeyboardButton("◀️ BACK", callback_data="admin_payments")
        )
        if payment['image_file_id']:
            bot.send_photo(call.message.chat.id, payment['image_file_id'], caption=caption, parse_mode='HTML', reply_markup=markup)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.edit_message_text(caption, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    
    if data.startswith("confirm_payment_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        payment_id = data.replace("confirm_payment_", "")
        success, credited_user, amount = confirm_payment(payment_id, user_id)
        if success:
            bot.answer_callback_query(call.id, f"✅ Payment confirmed! {symbol}{amount:,.2f} added.", show_alert=True)
            bot.edit_message_caption(f"✅ PAYMENT CONFIRMED!\n\nUser credited: {symbol}{amount:,.2f}", call.message.chat.id, call.message.message_id, parse_mode='HTML')
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
    
    # ========== ADMIN WITHDRAWALS ==========
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
        msg = f"📤 WITHDRAWAL DETAILS\n\n👤 User: <code>{wd['user_id']}</code>\n💰 Amount: {symbol}{wd['amount']:,.2f}\n🏦 Bank: {wd['bank_name']}\n📋 Account: <code>{wd['account_number']}</code>\n👤 Name: {wd['account_name']}\n📅 Requested: {wd['request_date'][:16]}\n\nMark as completed after sending payment."
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
        return
    
    # ========== ADMIN USERS & STATS ==========
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
        msg += f"💎 {MY_SIGNATURE}"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_manage_admins":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        admins = get_all_admins()
        markup = types.InlineKeyboardMarkup(row_width=1)
        for admin in admins:
            if admin['user_id'] != MASTER_ADMIN_ID:
                markup.add(types.InlineKeyboardButton(f"👑 {admin['first_name']} ({admin['user_id']})", callback_data=f"revoke_admin_{admin['user_id']}"))
        markup.add(types.InlineKeyboardButton("◀️ BACK", callback_data="admin_back"))
        bot.edit_message_text("👑 MANAGE ADMINS", call.message.chat.id, call.message.message_id, reply_markup=markup)
        return
    
    if data.startswith("revoke_admin_"):
        if user_id != MASTER_ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Master admin only!", show_alert=True)
            return
        target_id = int(data.replace("revoke_admin_", ""))
        revoke_admin(target_id)
        bot.answer_callback_query(call.id, f"✅ Admin revoked from {target_id}!", show_alert=True)
        bot.edit_message_text(f"✅ ADMIN REVOKED", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_stats":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        stats = get_bot_stats()
        wallet = get_admin_wallet()
        msg = f"📊 BOT STATISTICS\n\n👥 Users: {stats['total_users']:,}\n🚫 Banned: {stats['banned_users']:,}\n👑 Admins: {stats['admin_users']:,}\n\n📦 Orders: {stats['total_orders']:,}\n💰 Sales: {symbol}{stats['total_sales']:,.2f}\n💰 Deposits Today: {symbol}{stats['deposits_today']:,.2f}\n\n🔗 IG Stock: {stats['ig_stock']:,}\n📘 FB Stock: {stats['fb_stock']:,}\n\n⏳ Pending Payments: {stats['pending_payments']}\n📤 Pending Withdrawals: {stats['pending_withdrawals']}\n\n🏦 Admin Wallet: {symbol}{wallet['balance']:,.2f}\n📈 Total Earned: {symbol}{wallet['total_earned']:,.2f}\n\n💎 {MY_SIGNATURE}"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        return
    
    if data == "admin_broadcast":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text(
            "📢 BROADCAST MESSAGE\n\nSend your broadcast message:\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        user_sessions[user_id] = {'state': 'broadcast_text'}
        return
    
    if data == "admin_image_broadcast":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text(
            "📸 IMAGE BROADCAST\n\nSend the image you want to broadcast (you can add a caption).\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        user_sessions[user_id] = {'state': 'image_broadcast'}
        return
    
    if data == "admin_ban":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text(
            "🚫 BAN/UNBAN USER\n\nUse:\n`/ban USER_ID` - Ban user\n`/unban USER_ID` - Unban user\n\nExample: `/ban 123456789`\n\n💎 {MY_SIGNATURE}",
            call.message.chat.id, call.message.message_id, parse_mode='HTML'
        )
        return
    
    if data == "admin_wallet":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        wallet = get_admin_wallet()
        msg = f"💰 ADMIN WALLET\n\n**BALANCE:** {symbol}{wallet['balance']:,.2f}\n**TOTAL EARNED:** {symbol}{wallet['total_earned']:,.2f}\n**TOTAL WITHDRAWN:** {symbol}{wallet['total_withdrawn']:,.2f}\n\n💎 {MY_SIGNATURE}"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
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
    
    # ========== FB CONTINUE UPLOAD ==========
    if data == "fb_continue_upload":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
            return
        bot.edit_message_text("📘 **FB MANAGEMENT**", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=fb_management_keyboard())
        return

    # ========== CONFIRM EXTRACT ADD ==========
    if data == "confirm_extract_add":
        items = user_sessions.get(user_id, {}).get('extracted_items', [])
        added = 0
        for item in items:
            email = item['email']
            password = item.get('password', '')
            followers = item['followers']
            
            if not followers:
                continue
            
            price = get_price_for_followers(followers)
            if price is None:
                continue
            
            if password:
                success = add_ig_stock(email.split('@')[0], password, followers, price, user_id, has_pass=True)
            else:
                success = add_ig_stock(email.split('@')[0], None, followers, price, user_id, has_pass=False)
            
            if success:
                added += 1
        
        bot.edit_message_text(f"✅ Added {added} items to IG stock!", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        del user_sessions[user_id]
        return

    # ========== CONFIRM EXTRACT CANCEL ==========
    if data == "confirm_extract_cancel":
        bot.edit_message_text("❌ Cancelled. No items added.", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        del user_sessions[user_id]
        return

    if data == "admin_back":
        bot.edit_message_text("🔧 ADMIN CONTROL PANEL", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=admin_keyboard())
        return
    
    if data == "back_main":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(user_id, "🏠 MAIN MENU", parse_mode='HTML', reply_markup=main_keyboard(user_id))
        return
    
# ========== PAYMENT METHODS ==========
    if data == "pay_opay":
        user_sessions[user_id] = {'payment_method': 'OPay'}
        min_deposit = int(get_setting('min_deposit', '500'))
        bot.edit_message_text(f"💰 ENTER AMOUNT TO DEPOSIT\n\nMinimum: {symbol}{min_deposit:,}\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler(call.message, process_fund_amount)
        return
    
    if data == "pay_palmpay":
        user_sessions[user_id] = {'payment_method': 'PalmPay'}
        min_deposit = int(get_setting('min_deposit', '500'))
        bot.edit_message_text(f"💰 ENTER AMOUNT TO DEPOSIT\n\nMinimum: {symbol}{min_deposit:,}\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler(call.message, process_fund_amount)
        return
    
    if data == "pay_bank":
        user_sessions[user_id] = {'payment_method': 'Bank Transfer'}
        min_deposit = int(get_setting('min_deposit', '500'))
        bot.edit_message_text(f"💰 ENTER AMOUNT TO DEPOSIT\n\nMinimum: {symbol}{min_deposit:,}\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler(call.message, process_fund_amount)
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
        bot.reply_to(message, "📤 **SEND ACCOUNT DETAILS**\n\nFormat (one per line):\n`email|password|age`\n\nExample:\n`user@gmail.com|pass123|2 years`\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
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
        del user_sessions[user_id]
        return
    if message.text and not message.photo:
        session['fb_account_text'] = message.text
        session['fb_screenshots'] = []
        bot.reply_to(message, "📸 **Now send the screenshot(s) of this Facebook account**\n\nSend 1 or more screenshots.\n\nType /done when finished.\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
        bot.register_next_step_handler(message, process_fb_upload_screenshots)
    else:
        bot.reply_to(message, "❌ Please send account details first in format:\n`email|password|age`\n\nExample: `user@gmail.com|pass123|2 years`\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
        bot.register_next_step_handler(message, process_fb_upload_details)

def process_fb_upload_screenshots(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    if message.text == '/done':
        text = session.get('fb_account_text', '')
        screenshot_ids = session.get('fb_screenshots', [])
        price = session.get('fb_upload_price')
        category_id = session.get('fb_upload_category')
        if not screenshot_ids:
            bot.reply_to(message, "❌ No screenshots provided! Please send at least 1 screenshot.\n\nSend screenshot or type /cancel.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            bot.register_next_step_handler(message, process_fb_upload_screenshots)
            return
        lines = text.strip().split('\n')
        added = 0
        for line in lines:
            parts = line.split('|')
            if len(parts) >= 2:
                email = parts[0].strip()
                password = parts[1].strip()
                account_age = parts[2].strip() if len(parts) > 2 else ""
                screenshot_str = ','.join(screenshot_ids)
                if add_fb_stock(email, password, category_id, account_age, screenshot_str, price, user_id):
                    added += 1
        bot.reply_to(message, f"✅ **FB ACCOUNTS UPLOADED!**\n\n✅ Added: {added}\n📸 Screenshots saved: {len(screenshot_ids)}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ CONTINUE", callback_data="fb_continue_upload"),
            types.InlineKeyboardButton("❌ FINISH", callback_data="admin_back")
        )
        bot.reply_to(message, "📤 Continue uploading?", parse_mode='HTML', reply_markup=markup)
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
        bot.reply_to(message, f"📸 Screenshot {len(screenshot_ids)} saved!\n\nSend another screenshot or type /done to finish.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
        bot.register_next_step_handler(message, process_fb_upload_screenshots)
        return
    else:
        bot.reply_to(message, "❌ Please send a screenshot or type /done to finish.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
        bot.register_next_step_handler(message, process_fb_upload_screenshots)
        return

# =================================================================================
# MESSAGE HANDLER
# =================================================================================

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""
    symbol = get_setting('currency_symbol', '₦')
    
    if is_banned(user_id):
        bot.reply_to(message, "🚫 YOU ARE BANNED!", parse_mode='HTML')
        return
    
    # Session states
    if user_id in user_sessions:
        state = user_sessions[user_id].get('state')
        
        if state == 'withdraw':
            process_withdraw(message)
            return
        
        if state == 'add_ig_account':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            parts = text.split('|')
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format! Use: username|followers|password", parse_mode='HTML')
                return
            username = parts[0].strip()
            try:
                followers = int(parts[1].strip())
            except:
                bot.reply_to(message, "❌ Followers must be a number!", parse_mode='HTML')
                return
            password = parts[2].strip() if len(parts) > 2 and parts[2].strip().lower() != 'none' else None
            price = get_price_for_followers(followers)
            if price is None:
                bot.reply_to(message, f"❌ No price defined for {followers} followers", parse_mode='HTML')
                return
            success = add_ig_stock(username, password, followers, price, user_id, has_pass=(password is not None))
            if success:
                bot.reply_to(message, f"✅ Added IG account @{username} with {followers} followers @ ₦{price:,.0f}", parse_mode='HTML')
            else:
                bot.reply_to(message, f"❌ Failed to add @{username} (duplicate?)", parse_mode='HTML')
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
        
        if state == 'delete_fb_by_id':
            try:
                stock_id = int(text)
                delete_fb_stock(stock_id)
                bot.reply_to(message, f"✅ FB stock {stock_id} deleted!", parse_mode='HTML')
            except:
                bot.reply_to(message, "❌ Invalid ID!", parse_mode='HTML')
            del user_sessions[user_id]
            return
        
        if state == 'fb_edit_category_price':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            try:
                new_price = float(text.strip())
                if new_price <= 0:
                    bot.reply_to(message, "❌ Price must be greater than 0!", parse_mode='HTML')
                    return
                cat_id = user_sessions[user_id].get('cat_id')
                if update_fb_category_price(cat_id, new_price):
                    bot.reply_to(message, f"✅ Category price updated to {symbol}{new_price:,.0f}!", parse_mode='HTML')
                else:
                    bot.reply_to(message, "❌ Failed to update!", parse_mode='HTML')
                del user_sessions[user_id]
            except:
                bot.reply_to(message, "❌ Invalid price!", parse_mode='HTML')
            return
        
        if state == 'fb_add_category':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            parts = text.split('|')
            if len(parts) < 4:
                bot.reply_to(message, "❌ Invalid format! Use: name|display_name|price|has_page", parse_mode='HTML')
                return
            name = parts[0].strip()
            display_name = parts[1].strip()
            try:
                price = float(parts[2].strip())
                has_page = int(parts[3].strip())
            except:
                bot.reply_to(message, "❌ Invalid price or has_page!", parse_mode='HTML')
                return
            if add_fb_category(name, display_name, price, has_page):
                bot.reply_to(message, f"✅ FB Category {display_name} added!", parse_mode='HTML')
            else:
                bot.reply_to(message, "❌ Failed to add category (name exists?)", parse_mode='HTML')
            del user_sessions[user_id]
            return
        
        if state == 'fb_upload_price':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            try:
                price = float(text.strip())
                if price <= 0:
                    raise ValueError
                user_sessions[user_id]['fb_upload_price'] = price
                bot.reply_to(message, "📤 **SEND ACCOUNT DETAILS**\n\nFormat:\n`email|password|age`\n\nExample: `user@gmail.com|pass123|2 years`\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                user_sessions[user_id]['state'] = 'fb_upload_details'
            except:
                bot.reply_to(message, "❌ Invalid price! Send a number.", parse_mode='HTML')
            return
        
        if state == 'fb_upload_details':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            user_sessions[user_id]['fb_account_text'] = text
            user_sessions[user_id]['fb_screenshots'] = []
            user_sessions[user_id]['state'] = 'fb_upload_screenshots'
            bot.reply_to(message, "📸 **Now send the screenshot(s) of this Facebook account**\n\nSend 1 or more screenshots.\n\nType /done when finished.\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            return
        
        if state == 'fb_upload_screenshots':
            if text == '/done':
                text_data = user_sessions[user_id].get('fb_account_text', '')
                screenshot_ids = user_sessions[user_id].get('fb_screenshots', [])
                price = user_sessions[user_id].get('fb_upload_price')
                category_id = user_sessions[user_id].get('fb_upload_category')
                if not screenshot_ids:
                    bot.reply_to(message, "❌ No screenshots provided!", parse_mode='HTML')
                    return
                lines = text_data.strip().split('\n')
                added = 0
                for line in lines:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        email = parts[0].strip()
                        password = parts[1].strip()
                        account_age = parts[2].strip() if len(parts) > 2 else ""
                        screenshot_str = ','.join(screenshot_ids)
                        if add_fb_stock(email, password, category_id, account_age, screenshot_str, price, user_id):
                            added += 1
                bot.reply_to(message, f"✅ Added {added} FB accounts!\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                del user_sessions[user_id]
            elif text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
            elif message.photo:
                screenshots = user_sessions[user_id].get('fb_screenshots', [])
                screenshots.append(message.photo[-1].file_id)
                user_sessions[user_id]['fb_screenshots'] = screenshots
                bot.reply_to(message, f"📸 Screenshot {len(screenshots)} saved!\n\nSend another or type /done.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            else:
                bot.reply_to(message, "❌ Please send a screenshot or type /done.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            return
        
        if state == 'report_issue':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            issue = text
            img_id = message.photo[-1].file_id if message.photo else None
            report_id = f"RPT{user_id}{int(time.time())}{random.randint(100,999)}"
            c = db.cursor()
            c.execute("INSERT INTO reports (report_id, user_id, issue, image_id, timestamp) VALUES (?, ?, ?, ?, ?)",
                      (report_id, user_id, issue, img_id, datetime.datetime.now().isoformat()))
            db.commit()
            bot.reply_to(message, f"✅ REPORT SUBMITTED!\n\n🆔 ID: {report_id}\n\nAdmin will review.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            for admin in [MASTER_ADMIN_ID]:
                try:
                    if img_id:
                        bot.send_photo(admin, img_id, caption=f"📢 NEW REPORT\nUser: {user_id}\nID: {report_id}\nIssue: {issue}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                    else:
                        bot.send_message(admin, f"📢 NEW REPORT\nUser: {user_id}\nID: {report_id}\nIssue: {issue}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                except:
                    pass
            del user_sessions[user_id]
            return
        
        if state == 'expert_support':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            c = db.cursor()
            c.execute("INSERT INTO support_messages (user_id, message, timestamp) VALUES (?, ?, ?)",
                      (user_id, text, datetime.datetime.now().isoformat()))
            db.commit()
            bot.reply_to(message, f"🤖 SUPPORT\n\nWe'll get back to you soon.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            for admin in [MASTER_ADMIN_ID]:
                try:
                    bot.send_message(admin, f"💬 SUPPORT MESSAGE\nUser: {user_id}\nMessage: {text[:200]}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                except:
                    pass
            del user_sessions[user_id]
            return
        
        if state == 'broadcast_text':
            if text == '/cancel':
                bot.reply_to(message, "❌ Broadcast cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            c = db.cursor()
            c.execute("SELECT user_id FROM users WHERE is_banned = 0")
            users = [row[0] for row in c.fetchall()]
            success = 0
            for uid in users:
                try:
                    bot.send_message(uid, f"📢 ANNOUNCEMENT\n\n{text}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                    success += 1
                    add_notification(uid, "Announcement", text[:200])
                except:
                    pass
                time.sleep(0.05)
            bot.reply_to(message, f"✅ Broadcast sent to {success} users!\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            del user_sessions[user_id]
            return
        
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
            success, failed = broadcast_with_image(caption, image_id)
            bot.reply_to(message, f"✅ Image broadcast sent to {success} users (Failed: {failed})!\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            del user_sessions[user_id]
            return
        
        # Wallet control states
        if state == 'wallet_add':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            parts = text.split('|')
            if len(parts) != 2:
                bot.reply_to(message, "❌ Use: USER_ID|AMOUNT", parse_mode='HTML')
                return
            try:
                target_id = int(parts[0].strip())
                amount = float(parts[1].strip())
                if amount <= 0:
                    bot.reply_to(message, "❌ Amount must be > 0", parse_mode='HTML')
                    return
                new_balance = add_wallet(target_id, amount)
                bot.reply_to(message, f"✅ Added ₦{amount:,.2f} to user {target_id}\n💰 New balance: ₦{new_balance:,.2f}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                add_notification(target_id, "Wallet Update", f"₦{amount:,.2f} added to your wallet. New balance: ₦{new_balance:,.2f}")
                try:
                    bot.send_message(target_id, f"💰 ₦{amount:,.2f} added to your wallet!\n💰 New balance: ₦{new_balance:,.2f}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                except:
                    pass
            except:
                bot.reply_to(message, "❌ Invalid!", parse_mode='HTML')
            del user_sessions[user_id]
            return
        
        if state == 'wallet_remove':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            parts = text.split('|')
            if len(parts) != 2:
                bot.reply_to(message, "❌ Use: USER_ID|AMOUNT", parse_mode='HTML')
                return
            try:
                target_id = int(parts[0].strip())
                amount = float(parts[1].strip())
                if amount <= 0:
                    bot.reply_to(message, "❌ Amount must be > 0", parse_mode='HTML')
                    return
                new_balance = remove_wallet(target_id, amount)
                bot.reply_to(message, f"✅ Removed ₦{amount:,.2f} from user {target_id}\n💰 New balance: ₦{new_balance:,.2f}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                add_notification(target_id, "Wallet Update", f"₦{amount:,.2f} removed from your wallet. New balance: ₦{new_balance:,.2f}")
                try:
                    bot.send_message(target_id, f"💰 ₦{amount:,.2f} removed from your wallet!\n💰 New balance: ₦{new_balance:,.2f}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                except:
                    pass
            except:
                bot.reply_to(message, "❌ Invalid!", parse_mode='HTML')
            del user_sessions[user_id]
            return
        
        if state == 'wallet_set':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            parts = text.split('|')
            if len(parts) != 2:
                bot.reply_to(message, "❌ Use: USER_ID|NEW_BALANCE", parse_mode='HTML')
                return
            try:
                target_id = int(parts[0].strip())
                new_balance = float(parts[1].strip())
                if new_balance < 0:
                    bot.reply_to(message, "❌ Balance cannot be negative", parse_mode='HTML')
                    return
                set_wallet(target_id, new_balance)
                bot.reply_to(message, f"✅ User {target_id} wallet set to ₦{new_balance:,.2f}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                add_notification(target_id, "Wallet Update", f"Your wallet balance has been set to ₦{new_balance:,.2f}")
                try:
                    bot.send_message(target_id, f"💰 Your wallet balance has been set to ₦{new_balance:,.2f}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
                except:
                    pass
            except:
                bot.reply_to(message, "❌ Invalid!", parse_mode='HTML')
            del user_sessions[user_id]
            return
        
        if state == 'wallet_check':
            if text == '/cancel':
                bot.reply_to(message, "❌ Cancelled.", parse_mode='HTML')
                del user_sessions[user_id]
                return
            try:
                target_id = int(text.strip())
                balance = get_wallet(target_id)
                user = get_user(target_id)
                name = user.get('first_name', 'Unknown') if user else 'Unknown'
                bot.reply_to(message, f"🔍 **USER BALANCE**\n\n👤 {name} ({target_id})\n💰 ₦{balance:,.2f}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
            except:
                bot.reply_to(message, "❌ Invalid USER_ID!", parse_mode='HTML')
            del user_sessions[user_id]
            return
    
    # Main menu buttons
    if text == "🔧 ADMIN PANEL" and is_admin(user_id):
        bot.reply_to(message, "🔧 ADMIN CONTROL PANEL", parse_mode='HTML', reply_markup=admin_keyboard())
    elif text == "🔗 BUY IG":
        bot.reply_to(message, "🔗 **SELECT IG PACKAGE:**", parse_mode='HTML', reply_markup=ig_packages_keyboard())
    elif text == "📘 BUY FACEBOOK":
        bot.reply_to(message, "📘 **SELECT FACEBOOK ACCOUNT TYPE**", parse_mode='HTML', reply_markup=fb_categories_keyboard())
    elif text == "💰 MY WALLET":
        balance = get_wallet(user_id)
        bot.reply_to(message, f"💰 YOUR WALLET BALANCE\n\n{symbol}{balance:,.2f}\n\n📌 Withdraw: /withdraw\nMinimum: {symbol}{int(get_setting('min_withdrawal', '5000')):,}\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
    elif text == "💳 FUND WALLET":
        bot.reply_to(message, "💳 SELECT PAYMENT METHOD:", parse_mode='HTML', reply_markup=payment_methods_keyboard())
    elif text == "📦 MY ORDERS":
        orders = get_user_orders(user_id)
        if not orders:
            bot.reply_to(message, "📦 NO ORDERS YET!\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
        else:
            msg = "📦 YOUR ORDERS\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for order in orders[:10]:
                msg += f"✅ {order['product_name']}\n   💰 {symbol}{order['amount']:,.2f}\n   📅 {order['order_date'][:16]}\n"
                if order.get('delivery_info'):
                    msg += f"   📄 {order['delivery_info'][:100]}...\n"
                msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"💎 {MY_SIGNATURE}"
            bot.reply_to(message, msg, parse_mode='HTML')
    elif text == "📊 MY STATS":
        user = get_user(user_id)
        if user:
            msg = f"📊 YOUR STATISTICS\n\n💰 BALANCE: {symbol}{user['wallet_balance']:,.2f}\n💸 SPENT: {symbol}{user['total_spent']:,.2f}\n📦 ORDERS: {user.get('total_orders', 0)}\n\n👥 REFERRALS: {user.get('total_referrals', 0)}\n💰 EARNINGS: {symbol}{user.get('referral_earnings', 0):,.2f}\n\n📅 JOINED: {user['join_date'][:16]}\n\n💎 {MY_SIGNATURE}"
            bot.reply_to(message, msg, parse_mode='HTML')
    elif text == "👥 REFERRALS":
        user = get_user(user_id)
        if user:
            ref_count, ref_earnings = get_user_referral_stats(user_id)
            link = f"https://t.me/{BOT_USERNAME}?start={user['referral_code']}"
            bonus = int(get_setting('referral_bonus', '250'))
            msg = f"👥 REFERRAL PROGRAM\n\n💰 BONUS: {symbol}{bonus} per referral (when they make first purchase)\n\nYOUR STATS:\n• Referrals: {ref_count}\n• Earnings: {symbol}{ref_earnings:,.2f}\n\n🔗 YOUR LINK:\n<code>{link}</code>\n\nShare this link with friends!\n\n💎 {MY_SIGNATURE}"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📤 SHARE", url=f"https://t.me/share/url?url={link}&text=Join%20Hamzzy%20Marketplace!"))
            bot.reply_to(message, msg, parse_mode='HTML', reply_markup=markup)
    elif text == "🏆 LEADERBOARD":
        leaders = get_referral_leaderboard()
        if not leaders:
            bot.reply_to(message, "🏆 NO REFERRALS YET!\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
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
            bot.reply_to(message, "📜 NO TRANSACTIONS YET!\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
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
            bot.reply_to(message, "🔔 NO NEW NOTIFICATIONS!\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
        else:
            msg = "🔔 YOUR NOTIFICATIONS\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for n in notifs:
                msg += f"📌 {n['title']}\n{n['message'][:200]}\n📅 {n['created_date'][:16]}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                c.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (n['id'],))
            db.commit()
            msg += f"💎 {MY_SIGNATURE}"
            bot.reply_to(message, msg, parse_mode='HTML')
    elif text == "👑 VIP STATUS":
        # Simple VIP display
        total_spent = get_user(user_id).get('total_spent', 0) if get_user(user_id) else 0
        level = "Bronze"
        discount = 0
        if total_spent >= 1000000:
            level, discount = "Diamond 👑", 20
        elif total_spent >= 500000:
            level, discount = "Platinum 💎", 15
        elif total_spent >= 150000:
            level, discount = "Gold 🥇", 10
        elif total_spent >= 50000:
            level, discount = "Silver 🥈", 5
        msg = f"👑 VIP STATUS\n\nYour Level: {level}\nDiscount: {discount}% off\nTotal Spent: {symbol}{total_spent:,.2f}\n\nSpend {symbol}{50000 - total_spent:,.2f} more to reach Silver!\n\n💎 {MY_SIGNATURE}"
        bot.reply_to(message, msg, parse_mode='HTML')
    elif text == "❓ HELP":
        msg = f"❓ HELP & SUPPORT\n\n📌 HOW TO BUY IG:\n1. Click BUY IG\n2. Select follower range\n3. Choose with/without password\n4. Purchase with wallet balance\n\n📌 HOW TO BUY FACEBOOK:\n1. Click BUY FACEBOOK\n2. Select category\n3. View screenshot\n4. Confirm purchase\n\n📌 HOW TO FUND WALLET:\n1. Click FUND WALLET\n2. Select payment method\n3. Enter amount\n4. Send payment and screenshot\n5. Admin confirms → Wallet credited\n\n📌 HOW TO WITHDRAW:\nType /withdraw\n\n📌 REFERRAL PROGRAM:\nShare your link → Get ₦250 per referral!\n\n📞 SUPPORT:\n• Admin: @hamzzyhacket\n• Channel: {CHANNEL_LINK}\n\n💎 {MY_SIGNATURE}"
        bot.reply_to(message, msg, parse_mode='HTML')
    elif text == "📢 REPORT ISSUE":
        bot.reply_to(message, "📢 REPORT ISSUE\n\nDescribe your issue. You can also send a screenshot.\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML')
        user_sessions[user_id] = {'state': 'report_issue'}
    elif text == "🤖 EXPERT SUPPORT":
        bot.reply_to(message, "🤖 EXPERT SUPPORT\n\nDescribe your issue or question in detail.\n\nType /cancel to cancel.\n\n💎 {MY_SIGNATURE}", parse_mode='HTML', reply_markup=expert_support_keyboard())
        user_sessions[user_id] = {'state': 'expert_support'}
    else:
        # Auto-extract emails for admin
        if is_admin(user_id) and ('@' in text or any(c.isdigit() for c in text)):
            extracted = extract_emails_from_text(text)
            if extracted:
                items_msg = ""
                for item in extracted:
                    email = item['email']
                    followers = item['followers'] if item['followers'] else "???"
                    has_pass = "🔐" if item.get('password') else "📧"
                    items_msg += f"{has_pass} {email} - {followers} followers\n"
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("✅ ADD ALL TO STOCK", callback_data="confirm_extract_add"),
                    types.InlineKeyboardButton("❌ CANCEL", callback_data="confirm_extract_cancel")
                )
                bot.reply_to(message, f"📧 **EXTRACTED EMAILS:**\n\n{items_msg}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nDo you want to add these to IG stock?\n\n💎 {MY_SIGNATURE}", parse_mode='HTML', reply_markup=markup)
                user_sessions[user_id] = {'extracted_items': extracted}
                return
        
        bot.reply_to(message, "🏠 MAIN MENU", parse_mode='HTML', reply_markup=main_keyboard(user_id))

# =================================================================================
# BACKGROUND THREADS
# =================================================================================

def start_background_tasks():
    def low_stock_loop():
        while True:
            check_low_stock()
            time.sleep(3600)  # Check every hour
    
    def daily_report_loop():
        while True:
            now = datetime.datetime.now()
            report_time = get_setting('auto_report_time', '08:00')
            target_hour = int(report_time.split(':')[0])
            target_minute = int(report_time.split(':')[1]) if ':' in report_time else 0
            if now.hour == target_hour and now.minute == target_minute:
                generate_daily_report()
                time.sleep(60)
            time.sleep(30)
    
    threading.Thread(target=low_stock_loop, daemon=True).start()
    threading.Thread(target=daily_report_loop, daemon=True).start()
    print("✅ Background tasks started (Low stock alerts, Daily reports)")

# =================================================================================
# RUN BOT
# =================================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🔥 HAMZZY MARKETPLACE BOT - COMPLETE PROFESSIONAL VERSION 🔥")
    print("=" * 80)
    print(f"👑 Master Admin: {MASTER_ADMIN_ID}")
    print(f"🤖 Bot: @{BOT_USERNAME}")
    print(f"💎 Created by: {MY_SIGNATURE}")
    print("=" * 80)
    print("✅ FEATURES INCLUDED:")
    print("   • BUY IG (with/without password)")
    print("   • BUY FACEBOOK (with categories & screenshots)")
    print("   • Full Admin Panel (IG/FB management)")
    print("   • Wallet Control (Add/Remove/Set balance)")
    print("   • Payment System with Admin Approval")
    print("   • Withdrawal System")
    print("   • Referral System (Bonus on first purchase)")
    print("   • Order History & Transaction History")
    print("   • Notifications System")
    print("   • Broadcast (Text & Image)")
    print("   • Auto Email Extraction")
    print("   • Low Stock Alerts")
    print("   • Daily Sales Reports")
    print("   • Database Backup")
    print("=" * 80)
    print("🚀 BOT IS RUNNING...")
    print("=" * 80)
    
    # Start background tasks
    start_background_tasks()
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except KeyboardInterrupt:
            print("\n❌ BOT STOPPED BY USER")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}")
            time.sleep(10)