#!/usr/bin/env python3
"""
Script to index allegedly leaked domain data from Company.List.txt into a SQLite database
for Oracle breach checking. This uses the list of domains that were reportedly part of
the Oracle breach.
"""
import sqlite3
import os
import sys

# Ensure data directory exists
os.makedirs('./data', exist_ok=True)

# Path to the database
DB_PATH = './data/oracle_breach.db'

# Create database connection
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


def index_data(domains_file):
    """
    Index domain data from a file into the SQLite database.

    Args:
        domains_file (str): Path to the file containing domains, one per line.
    """
    print(f"Indexing data from file: {domains_file}")

    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS breached_domains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT UNIQUE
    )
    ''')

    # Read domains from file
    try:
        with open(domains_file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]

        print(f"Found {len(domains)} domains to index")

        # Insert domains into database
        for domain in domains:
            try:
                cursor.execute("INSERT OR IGNORE INTO breached_domains (domain) VALUES (?)", (domain,))
            except sqlite3.Error as e:
                print(f"Error inserting {domain}: {e}")

        # Commit changes
        conn.commit()
        print(f"Successfully indexed {cursor.rowcount} domains")

    except Exception as e:
        print(f"Error indexing data: {e}")
        conn.rollback()
        return False

    return True


def index_hardcoded_data():
    """
    Index hardcoded domain data into the SQLite database.
    Used as a fallback if no file is provided.
    """
    print("Indexing hardcoded domain data")

    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS breached_domains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT UNIQUE
    )
    ''')

    # Hardcoded domains
    domains = [
        "cloudspm.com",
        "rsnortheast.com",
        "projecttechgroup.com",
        "wtorre.com.br",
        "spmstrategic.com",
        "waterworks.com",
        "calacademy.org",
        "alaristechnology.com",
        "ironmountain.com",
        "qatarcool.com",
        "scrippshealth.org",
        "jabong.com",
        "bbam.com",
        "terillium.com",
        "wavebroadband.com",
        "amplitone.com.ar",
        "eagle.org",
        "sunedison.com",
        "test2.com"
    ]

    # Insert domains into database
    for domain in domains:
        try:
            cursor.execute("INSERT OR IGNORE INTO breached_domains (domain) VALUES (?)", (domain,))
        except sqlite3.Error as e:
            print(f"Error inserting {domain}: {e}")

    # Commit changes
    conn.commit()
    print(f"Successfully indexed {len(domains)} hardcoded domains")

    return True

def index_column():
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_domain ON breached_domains (domain)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        domains_file = sys.argv[1]
        index_data(domains_file)
    else:
        print("No domains file provided, using hardcoded domains")
        index_hardcoded_data()

    index_column() # does the actual indexing :)

    print(f"Data indexing complete. Database stored at {DB_PATH}")

    # Close connection
    conn.close()
