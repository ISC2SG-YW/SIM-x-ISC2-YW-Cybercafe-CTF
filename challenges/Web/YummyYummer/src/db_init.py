# init_db.py
import random
import secrets
import string
import hashlib
import sqlite3

DB_PATH = "./yummy_yummer.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user (
  user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
  username      TEXT NOT NULL UNIQUE,
  email         TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role          TEXT NOT NULL DEFAULT 'customer' CHECK (role IN ('customer','admin')),
  is_active     INTEGER NOT NULL DEFAULT 1,
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS menu (
  item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
  sku         TEXT NOT NULL UNIQUE,
  name        TEXT NOT NULL,
  description TEXT NOT NULL,
  category    TEXT NOT NULL CHECK (category IN ('mains','sides','drinks','desserts','breakfast','salads','soups')),
  price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
  currency    TEXT NOT NULL DEFAULT 'SGD',
  in_stock    INTEGER NOT NULL DEFAULT 0 CHECK (in_stock >= 0),
  image_url   TEXT,
  is_active   INTEGER NOT NULL DEFAULT 1,
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_catalog_items_name ON menu(name);
CREATE INDEX IF NOT EXISTS idx_catalog_items_category ON menu(category);
"""

SEED_ITEMS = [
  ("BURG-001","Triple Cheeseburger","Three beef patties, cheese, pickles, onions, ketchup, mustard","mains",0,"SGD",100,None),
  ("BURG-002","Quarter Pounder with Cheese","Quarter-pound beef, cheese, onions, pickles","mains",0,"SGD",100,None),
  ("BURG-003","Double Quarter Pounder with Cheese","Two quarter-pound patties with cheese","mains",0,"SGD",100,None),
  ("BURG-004","Cheeseburger","Beef patty, cheese, pickles, onions","mains",0,"SGD",100,None),
  ("BURG-005","Double Cheeseburger","Two beef patties with cheese","mains",0,"SGD",100,None),
  ("BURG-006","Hamburger","Classic beef patty with pickles and onions","mains",0,"SGD",100,None),
  ("BURG-007","Big Mac","Two beef patties, special sauce, lettuce, cheese, pickles, onions","mains",0,"SGD",100,None),
  ("BURG-008","McChicken","Crispy chicken patty with lettuce and mayo","mains",0,"SGD",100,None),
  ("BURG-009","McChicken with Cheese","McChicken topped with cheese","mains",0,"SGD",100,None),
  ("BURG-010","Buttermilk Crispy Chicken","Buttermilk crispy chicken with lettuce and mayo","mains",0,"SGD",100,None),
  ("BURG-011","McSpicy","Spicy chicken thigh burger","mains",0,"SGD",100,None),
  ("BURG-012","McSpicy with Cheese","McSpicy with added cheese","mains",0,"SGD",100,None),
  ("BURG-013","Double McSpicy","Double spicy chicken patties","mains",0,"SGD",100,None),
  ("BURG-014","Double McSpicy with Cheese","Double McSpicy with cheese","mains",0,"SGD",100,None),
  ("FISH-001","Filet-O-Fish","Fish patty with tartar sauce on a steamed bun","mains",0,"SGD",100,None),
  ("FISH-002","Double Filet-O-Fish","Two fish patties with tartar sauce","mains",0,"SGD",100,None),
  ("CKNY-001","Chicken McCrispy Signature (2pc)","Crispy chicken pieces (Signature)","mains",0,"SGD",100,None),
  ("CKNY-002","Chicken McCrispy Signature (6pc)","Crispy chicken pieces (Signature)","mains",0,"SGD",100,None),
  ("CKNY-003","Chicken McCrispy Spicy (2pc)","Spicy crispy chicken pieces","mains",0,"SGD",100,None),
  ("CKNY-004","Chicken McCrispy Spicy (6pc)","Spicy crispy chicken pieces","mains",0,"SGD",100,None),
  ("NUG-006","Chicken McNuggets (6pc)","Bite-sized chicken nuggets","sides",0,"SGD",100,None),
  ("NUG-009","Chicken McNuggets (9pc)","Bite-sized chicken nuggets","sides",0,"SGD",100,None),
  ("NUG-020","Chicken McNuggets (20pc)","Bite-sized chicken nuggets","sides",0,"SGD",100,None),
  ("WING-002","McWings (2pc)","Crispy chicken wings","sides",0,"SGD",100,None),
  ("WING-004","McWings (4pc)","Crispy chicken wings","sides",0,"SGD",100,None),
  ("WRAP-001","Buttermilk Chicken McWrap","Buttermilk crispy chicken wrap with veggies and sauce","mains",0,"SGD",100,None),
  ("WRAP-002","Spicy Chicken McWrap","Spicy chicken wrap with veggies and sauce","mains",0,"SGD",100,None),
  ("SALD-001","Garden Side Salad","Lettuce mix with dressing","salads",0,"SGD",100,None),
  ("SALD-002","Buttermilk Chicken Salad","Salad with buttermilk crispy chicken","salads",0,"SGD",100,None),
  ("BRKF-001","Big Breakfast","Scrambled eggs, sausage, muffins, hash brown","breakfast",0,"SGD",100,None),
  ("BRKF-002","Breakfast Deluxe","Hotcakes, scrambled eggs, sausage, hash brown","breakfast",0,"SGD",100,None),
  ("BRKF-003","Hotcakes","Hotcakes with syrup and butter","breakfast",0,"SGD",100,None),
  ("BRKF-004","Hotcakes with Sausage","Hotcakes served with sausage patty","breakfast",0,"SGD",100,None),
  ("BRKF-005","Breakfast Wrap Chicken Sausage","Egg, cheese, chicken sausage wrap","breakfast",0,"SGD",100,None),
  ("BRKF-006","Breakfast Wrap Chicken Ham","Egg, cheese, chicken ham wrap","breakfast",0,"SGD",100,None),
  ("BRKF-007","Egg McMuffin","Egg and cheese on toasted English muffin","breakfast",0,"SGD",100,None),
  ("BRKF-008","Chicken Muffin","Chicken patty on English muffin","breakfast",0,"SGD",100,None),
  ("BRKF-009","Chicken Muffin with Egg","Chicken muffin with egg","breakfast",0,"SGD",100,None),
  ("BRKF-010","Sausage McMuffin","Sausage patty with cheese on muffin","breakfast",0,"SGD",100,None),
  ("BRKF-011","Sausage McMuffin with Egg","Sausage muffin with egg","breakfast",0,"SGD",100,None),
  ("BRKF-012","Scrambled Egg Burger with Sausage","Scrambled egg with sausage in bun","breakfast",0,"SGD",100,None),
  ("BRKF-013","Scrambled Egg Burger with Chicken","Scrambled egg with chicken in bun","breakfast",0,"SGD",100,None),
  ("SIDE-001","French Fries (S)","Crispy golden fries","sides",0,"SGD",100,None),
  ("SIDE-002","French Fries (M)","Crispy golden fries","sides",0,"SGD",100,None),
  ("SIDE-003","French Fries (L)","Crispy golden fries","sides",0,"SGD",100,None),
  ("SIDE-004","Corn (Jr)","Sweet corn cup (Junior)","sides",0,"SGD",100,None),
  ("SIDE-005","Corn","Sweet corn cup","sides",0,"SGD",100,None),
  ("SIDE-006","Hash Brown","Crispy breakfast hash brown","sides",0,"SGD",100,None),
  ("DSRT-001","Apple Pie","Hot crispy pie with apple filling","desserts",0,"SGD",100,None),
  ("DSRT-002","Vanilla Cone","Soft-serve vanilla cone","desserts",0,"SGD",100,None),
  ("DSRT-003","ChocoCone","Chocolate-dipped vanilla cone","desserts",0,"SGD",100,None),
  ("DSRT-004","Hot Fudge Sundae","Soft-serve with hot fudge","desserts",0,"SGD",100,None),
  ("DSRT-005","Strawberry Sundae","Soft-serve with strawberry topping","desserts",0,"SGD",100,None),
  ("DSRT-006","OREO McFlurry","Soft-serve blended with OREO pieces","desserts",0,"SGD",100,None),
  ("DRNK-001","Ice Mountain Drinking Water","Bottled drinking water","drinks",0,"SGD",100,None),
  ("DRNK-002","Coca-Cola Original Taste (S)","Less sugar Coca-Cola (small)","drinks",0,"SGD",100,None),
  ("DRNK-003","Coca-Cola Original Taste (M)","Less sugar Coca-Cola (medium)","drinks",0,"SGD",100,None),
  ("DRNK-004","Coca-Cola Original Taste (L)","Less sugar Coca-Cola (large)","drinks",0,"SGD",100,None),
  ("DRNK-005","Coca-Cola Zero Sugar (S)","Coke Zero (small)","drinks",0,"SGD",100,None),
  ("DRNK-006","Coca-Cola Zero Sugar (M)","Coke Zero (medium)","drinks",0,"SGD",100,None),
  ("DRNK-007","Coca-Cola Zero Sugar (L)","Coke Zero (large)","drinks",0,"SGD",100,None),
  ("DRNK-008","Sprite (S)","Lemon-lime soda (small)","drinks",0,"SGD",100,None),
  ("DRNK-009","Sprite (M)","Lemon-lime soda (medium)","drinks",0,"SGD",100,None),
  ("DRNK-010","Sprite (L)","Lemon-lime soda (large)","drinks",0,"SGD",100,None),
  ("DRNK-011","Iced MILO (S)","Iced chocolate malt drink (small)","drinks",0,"SGD",100,None),
  ("DRNK-012","Iced MILO (M)","Iced chocolate malt drink (medium)","drinks",0,"SGD",100,None),
  ("DRNK-013","Jasmine Green Tea (S)","Iced jasmine green tea (small)","drinks",0,"SGD",100,None),
  ("DRNK-014","Jasmine Green Tea (M)","Iced jasmine green tea (medium)","drinks",0,"SGD",100,None),
  ("DRNK-015","Iced Lemon Tea (S)","Iced lemon tea (small)","drinks",0,"SGD",100,None),
  ("DRNK-016","Iced Lemon Tea (M)","Iced lemon tea (medium)","drinks",0,"SGD",100,None),
  ("DRNK-017","Low-Fat Hi-Calcium Milk","Carton milk","drinks",0,"SGD",100,None),
  ("DRNK-018","Hot MILO","Hot chocolate malt drink","drinks",0,"SGD",100,None),
  ("DRNK-019","Hot Tea","Hot black tea","drinks",0,"SGD",100,None),
  ("CAFE-001","McCafé Premium Roast Coffee","Freshly brewed coffee","drinks",0,"SGD",100,None),
  ("CAFE-002","Americano","Espresso with hot water","drinks",0,"SGD",100,None),
  ("CAFE-003","Iced Americano","Chilled Americano over ice","drinks",0,"SGD",100,None),
  ("CAFE-004","Cappuccino","Espresso with steamed milk foam","drinks",0,"SGD",100,None),
  ("CAFE-005","Latte","Espresso with steamed milk","drinks",0,"SGD",100,None),
  ("CAFE-006","Iced Latte","Chilled latte over ice","drinks",0,"SGD",100,None),
  ("CAFE-007","Mocha Frappe","Blended coffee drink with chocolate","drinks",0,"SGD",100,None),
  ("CAFE-008","Caramel Frappe","Blended coffee drink with caramel","drinks",0,"SGD",100,None),
  ("CAFE-009","Double Chocolate Frappe","Rich chocolate blended drink","drinks",0,"SGD",100,None),
  ("DRNK-020","Kiyo Grape Juice","Packaged grape juice","drinks",0,"SGD",100,None),
  ("DRNK-021","Oatside Oatmilk (Original)","Plant-based oat milk (original)","drinks",0,"SGD",100,None),
  ("DRNK-022","Oatside Oatmilk (Chocolate)","Plant-based oat milk (chocolate)","drinks",0,"SGD",100,None),
  ("SAUC-001","Curry Sauce","Dipping sauce","sides",0,"SGD",100,None),
  ("SAUC-002","Barbeque Sauce","Dipping sauce","sides",0,"SGD",100,None),
  ("SAUC-003","Honey Mustard Sauce","Dipping sauce","sides",0,"SGD",100,None),
  ("SAUC-004","Whipped Butter","Hotcakes butter portion","sides",0,"SGD",100,None),
  ("SAUC-005","Hotcake Syrup","Maple-style syrup portion","sides",0,"SGD",100,None),
  ("SAUC-006","Roasted Sesame Dressing","Salad dressing","sides",0,"SGD",100,None),
]

def gen_random_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def init_db(db_path: str = DB_PATH, num_users: int = 50) -> str:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        conn.executescript(SCHEMA_SQL)

        if conn.execute("SELECT COUNT(*) FROM menu").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO menu (sku,name,description,category,price_cents,currency,in_stock,image_url) VALUES (?,?,?,?,?,?,?,?)",
                SEED_ITEMS,
            )

        if conn.execute("SELECT COUNT(*) FROM user").fetchone()[0] == 0:
            bases = ["alice", "bob", "charlie", "dana", "evan", "fran", "gabe"]
            pool = random.sample(bases, k=min(num_users, len(bases)))
            admin_user = random.choice(pool)
            for u in pool:
                role = "admin" if u == admin_user else "customer"
                pw = gen_random_password()
                hashed_pw = hashlib.sha256(pw.encode("utf-8")).hexdigest()
                conn.execute(
                    "INSERT INTO user (username,email,password_hash,role) VALUES (?,?,?,?)",
                    (u, f"{u}@example.com", hashed_pw, role),
                )
        else:
            conn.execute("UPDATE user SET role='customer'")
            conn.execute(
                "UPDATE user SET role='admin' WHERE user_id = (SELECT user_id FROM user ORDER BY RANDOM() LIMIT 1)"
            )
            admin_user = conn.execute(
                "SELECT username FROM user WHERE role='admin' LIMIT 1"
            ).fetchone()[0]

        conn.commit()
        return admin_user
    finally:
        conn.close()
