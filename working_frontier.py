"""Small deterministic economy helpers for Dust & Debt.

No I/O and no extra dependencies. Business stock and job offers are data only;
the game owns transactions, UI, and persistence.
"""
from dataclasses import dataclass

# Work is deliberately lower paying than named bounties but repeatable.
# Coordinates are map positions with interaction radius handled in game.py.
WORK_OFFERS = {
    "Nell the stationmaster": ("courier", "Railway mail delivery", (1575, 1490), 22),
    "Rancher Amos": ("ranch", "Repair a broken fence", (1040, 2250), 19),
    "Prospector Finn": ("mining", "Collect shaft samples", (4520, 2860), 27),
    "Mina the miner": ("mining", "Inspect ore carts", (4230, 2810), 24),
    "Ezra the stablehand": ("stable", "Feed the horses", (1110, 925), 16),
}
# Town residents gain repeatable work without extra hardcoded mission stages.
WORK_ROLES = {
    "Courier": ("courier", "Deliver trading post parcels", (290, 135), 21),
    "Farmer": ("ranch", "Inspect the pasture fences", (300, -160), 18),
    "Watcher": ("patrol", "Inspect the boundary marker", (-330, -120), 20),
}

# Stock is capped by available daily quantity, making restocking meaningful.
# Index maps to an action defined in SHOP_GOODS.
DAILY_STOCK = {
    "store": (5, 3, 6),
    "saloon": (8, 8, 2),
    "doctor": (6, 5),
    "stable": (8, 3),
    "hotel": (8, 8),
    "office": (99,),
    "station": (6,),
}

def work_offer(name, x, y, settlements):
    if name in WORK_OFFERS:
        kind, title, target, reward = WORK_OFFERS[name]
        return (kind, title, tuple(target), reward)
    for role, (kind, title, offset, reward) in WORK_ROLES.items():
        if name.endswith(" " + role):
            return (kind, title, (int(x+offset[0]), int(y+offset[1])), reward)
    return None

def shop_prices(kind, goods, honor, town_key=""):
    """Deterministic prices with a small local and reputation adjustment."""
    discount = 2 if honor >= 75 else 0
    surcharge = 2 if honor < 25 else 0
    regional = 1 if town_key and town_key not in ("drybone", "saltwater") else 0
    return [max(1, int(price) + surcharge + regional - discount)
            for _, price, action in goods]

def daily_stock(kind, goods):
    base = DAILY_STOCK.get(kind, ())
    return [base[i] if i < len(base) else 4 for i in range(len(goods))]
