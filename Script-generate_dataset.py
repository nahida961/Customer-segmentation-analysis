"""
generate_dataset.py
Generates a synthetic customer dataset with 500 records and saves to data/customers.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

FIRST_NAMES = [
    "James","Mary","John","Patricia","Robert","Jennifer","Michael","Linda",
    "William","Barbara","David","Elizabeth","Richard","Susan","Joseph","Jessica",
    "Thomas","Sarah","Charles","Karen","Daniel","Nancy","Matthew","Lisa","Anthony",
    "Betty","Mark","Margaret","Donald","Sandra","Steven","Ashley","Paul","Dorothy",
    "Andrew","Kimberly","Joshua","Emily","Kenneth","Donna","Kevin","Michelle",
    "Brian","Carol","George","Amanda","Timothy","Melissa","Ronald","Deborah",
    "Edward","Stephanie","Jason","Rebecca","Jeffrey","Sharon","Ryan","Laura",
    "Jacob","Cynthia","Gary","Kathleen","Nicholas","Amy","Eric","Angela","Jonathan",
    "Shirley","Stephen","Anna","Larry","Brenda","Justin","Pamela","Scott","Emma",
    "Brandon","Nicole","Raymond","Helen","Frank","Samantha","Gregory","Katherine",
    "Samuel","Christine","Benjamin","Debra","Patrick","Rachel","Jack","Carolyn",
    "Dennis","Janet","Jerry","Maria","Alexander","Heather","Tyler","Diane","Aaron"
]

LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
    "Rodriguez","Martinez","Hernandez","Lopez","Gonzalez","Wilson","Anderson",
    "Thomas","Taylor","Moore","Jackson","Martin","Lee","Perez","Thompson","White",
    "Harris","Sanchez","Clark","Ramirez","Lewis","Robinson","Walker","Young",
    "Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores","Green",
    "Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts"
]

CITIES = [
    "New York","Los Angeles","Chicago","Houston","Phoenix","Philadelphia",
    "San Antonio","San Diego","Dallas","San Jose","Austin","Jacksonville",
    "Fort Worth","Columbus","Charlotte","San Francisco","Indianapolis","Seattle",
    "Denver","Nashville","Oklahoma City","El Paso","Washington","Boston","Memphis",
    "Louisville","Portland","Las Vegas","Baltimore","Milwaukee","Albuquerque",
    "Tucson","Fresno","Sacramento","Mesa","Kansas City","Atlanta","Omaha","Raleigh"
]

STATES = {
    "New York": "NY", "Los Angeles": "CA", "Chicago": "IL", "Houston": "TX",
    "Phoenix": "AZ", "Philadelphia": "PA", "San Antonio": "TX", "San Diego": "CA",
    "Dallas": "TX", "San Jose": "CA", "Austin": "TX", "Jacksonville": "FL",
    "Fort Worth": "TX", "Columbus": "OH", "Charlotte": "NC", "San Francisco": "CA",
    "Indianapolis": "IN", "Seattle": "WA", "Denver": "CO", "Nashville": "TN",
    "Oklahoma City": "OK", "El Paso": "TX", "Washington": "DC", "Boston": "MA",
    "Memphis": "TN", "Louisville": "KY", "Portland": "OR", "Las Vegas": "NV",
    "Baltimore": "MD", "Milwaukee": "WI", "Albuquerque": "NM", "Tucson": "AZ",
    "Fresno": "CA", "Sacramento": "CA", "Mesa": "AZ", "Kansas City": "MO",
    "Atlanta": "GA", "Omaha": "NE", "Raleigh": "NC"
}

CATEGORIES = ["Electronics", "Clothing", "Groceries", "Sports & Outdoors",
               "Home & Garden", "Beauty & Health", "Books", "Toys & Games"]

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def generate_customers(n=500):
    today = datetime(2024, 12, 31)
    start_date = datetime(2020, 1, 1)

    records = []
    for i in range(1, n + 1):
        # Assign customer tier randomly (skewed realistic distribution)
        tier_roll = random.random()
        if tier_roll < 0.08:
            tier = "Premium"
        elif tier_roll < 0.25:
            tier = "Loyal"
        elif tier_roll < 0.45:
            tier = "Regular"
        elif tier_roll < 0.62:
            tier = "New"
        elif tier_roll < 0.78:
            tier = "Budget"
        else:
            tier = "At-Risk"

        first = random.choice(FIRST_NAMES)
        last  = random.choice(LAST_NAMES)
        age   = int(np.clip(np.random.normal(38, 13), 18, 75))
        gender = random.choice(["Male", "Female", "Other"])
        city  = random.choice(CITIES)
        state = STATES[city]

        # Join date depends on tier
        if tier == "New":
            join_date = random_date(datetime(2024, 7, 1), today)
        elif tier == "At-Risk":
            join_date = random_date(datetime(2020, 1, 1), datetime(2022, 12, 31))
        else:
            join_date = random_date(start_date, today)

        # Last purchase date
        if tier == "At-Risk":
            last_purchase = random_date(join_date, datetime(2023, 6, 30))
        elif tier == "New":
            last_purchase = random_date(join_date, today)
        else:
            last_purchase = random_date(datetime(2024, 1, 1), today)

        # Total purchases
        purchases_map = {
            "Premium":  (60,  200),
            "Loyal":    (40,  120),
            "Regular":  (10,  50),
            "New":      (1,   10),
            "Budget":   (5,   25),
            "At-Risk":  (8,   40),
        }
        lo, hi = purchases_map[tier]
        total_purchases = random.randint(lo, hi)

        # Total spent
        aov_map = {
            "Premium":  (120, 600),
            "Loyal":    (60,  200),
            "Regular":  (30,  120),
            "New":      (20,  100),
            "Budget":   (10,  50),
            "At-Risk":  (25,  100),
        }
        aov_lo, aov_hi = aov_map[tier]
        avg_order_value = round(random.uniform(aov_lo, aov_hi), 2)
        total_spent = round(avg_order_value * total_purchases, 2)

        loyalty_points = int(total_spent * random.uniform(0.8, 1.2))

        preferred_category = random.choice(CATEGORIES)

        days_since_join = (today - join_date).days
        days_since_purchase = (today - last_purchase).days

        records.append({
            "customer_id": f"CUST{i:04d}",
            "full_name": f"{first} {last}",
            "age": age,
            "gender": gender,
            "city": city,
            "state": state,
            "join_date": join_date.strftime("%Y-%m-%d"),
            "last_purchase_date": last_purchase.strftime("%Y-%m-%d"),
            "total_purchases": total_purchases,
            "total_spent": total_spent,
            "avg_order_value": avg_order_value,
            "loyalty_points": loyalty_points,
            "preferred_category": preferred_category,
            "days_since_join": days_since_join,
            "days_since_last_purchase": days_since_purchase,
            "customer_tier": tier
        })

    return pd.DataFrame(records)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate_customers(500)
    df.to_csv("data/customers.csv", index=False)
    print(f"Generated {len(df)} customer records → data/customers.csv")
    print(f"\nTier distribution:")
    print(df["customer_tier"].value_counts().to_string())
    print(f"\nSample:\n{df.head(3).to_string()}")
