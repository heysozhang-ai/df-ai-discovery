import sqlite3
from pathlib import Path
from datetime import datetime
from models.business import Business


class Storage:

    def __init__(self):

        Path("data").mkdir(exist_ok=True)

        self.conn = sqlite3.connect("data/discovery.db")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS discovery (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,
            maps_url TEXT UNIQUE,
            website TEXT,
            phone TEXT,
            address TEXT,
            email TEXT,

            business_type TEXT,

            source TEXT,

            rule_score INTEGER DEFAULT 0,

            is_open INTEGER DEFAULT 1,

            status TEXT DEFAULT 'pending',

            approved INTEGER DEFAULT 0,

            created_at TEXT,

            updated_at TEXT

        )
        """)

        self.cursor.execute("PRAGMA table_info(discovery)")
        columns = {row["name"] for row in self.cursor.fetchall()}

        upgrades = {
            "phone": "TEXT",
            "address": "TEXT",
            "email": "TEXT",
            "business_type": "TEXT",
            "source": "TEXT",
            "rule_score": "INTEGER DEFAULT 0",
            "is_open": "INTEGER DEFAULT 1",
            "status": "TEXT DEFAULT 'pending'",
            "approved": "INTEGER DEFAULT 0",
            "created_at": "TEXT",
            "updated_at": "TEXT",
        }

        for column, column_type in upgrades.items():
            if column not in columns:
                print(f"Add column: {column}")
                self.cursor.execute(
                    f"ALTER TABLE discovery ADD COLUMN {column} {column_type}"
                )

        self.conn.commit()

    def exists(self, maps_url):

        self.cursor.execute(
            "SELECT id FROM discovery WHERE maps_url=?",
            (maps_url,)
        )

        return self.cursor.fetchone() is not None

    def save(self, business: Business):

        now = datetime.utcnow().isoformat()

        self.cursor.execute(
            """
            INSERT OR IGNORE INTO discovery(

                name,
                maps_url,
                website,
                phone,
                address,
                email,

                business_type,

                source,

                rule_score,

                is_open,

                status,

                approved,

                created_at,

                updated_at

            )

            VALUES(

                ?,?,?,?,?,?,

                ?,

                ?,

                ?,

                ?,

                ?,

                ?,

                ?,

                ?

            )
            """,
            (
                business.name,
                business.maps_url,
                business.website,
                business.phone,
                business.address,
                business.email,

                business.business_type,

                business.source,

                business.rule_score,

                int(business.is_open),

                business.status,

                int(business.approved),

                now,

                now,
            ),
        )

        self.conn.commit()

    def update(self, business: Business):

        now = datetime.utcnow().isoformat()

        self.cursor.execute(
            """
            UPDATE discovery

            SET

                name=?,
                website=?,
                phone=?,
                address=?,
                email=?,

                business_type=?,

                source=?,

                rule_score=?,

                is_open=?,

                status=?,

                approved=?,

                updated_at=?

            WHERE maps_url=?
            """,
            (
                business.name,
                business.website,
                business.phone,
                business.address,
                business.email,

                business.business_type,

                business.source,

                business.rule_score,

                int(business.is_open),

                business.status,

                int(business.approved),

                now,

                business.maps_url,
            ),
        )

        self.conn.commit()

    def get_pending(self):

        self.cursor.execute(
            """
            SELECT *
            FROM discovery
            WHERE status='pending'
            ORDER BY id
            """
        )

        return self.cursor.fetchall()

    def close(self):

        self.conn.close()
