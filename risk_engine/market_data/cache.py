"""
SQLite-based cache for market data with expiration.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketDataCache:
    """SQLite-based cache for market data with 24-hour expiration."""

    def __init__(self, db_path: str = "market_data_cache.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                asset_id TEXT PRIMARY KEY,
                spot_price REAL NOT NULL,
                volatility REAL NOT NULL,
                risk_free_rate REAL NOT NULL,
                dividend_yield REAL DEFAULT 0.0,
                last_updated TIMESTAMP NOT NULL,
                data_source TEXT DEFAULT 'yfinance'
            )
        """)

        conn.commit()
        conn.close()
        logger.info(f"Market data cache initialized at {self.db_path}")

    def get(self, asset_id: str, max_age_hours: int = 24) -> Optional[Dict]:
        """Get cached market data if not expired."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT asset_id, spot_price, volatility, risk_free_rate,
                   dividend_yield, last_updated, data_source
            FROM market_data
            WHERE asset_id = ?
        """,
            (asset_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        last_updated = datetime.fromisoformat(row[5])
        age = datetime.now() - last_updated

        if age > timedelta(hours=max_age_hours):
            logger.info(f"Cached data for {asset_id} is expired (age: {age})")
            return None

        return {
            "asset_id": row[0],
            "spot": row[1],
            "vol": row[2],
            "rate": row[3],
            "dividend": row[4],
            "last_updated": row[5],
            "source": row[6],
        }

    def set(
        self,
        asset_id: str,
        spot: float,
        vol: float,
        rate: float,
        dividend: float = 0.0,
        source: str = "yfinance",
    ):
        """Store or update market data in cache."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO market_data
            (asset_id, spot_price, volatility, risk_free_rate,
             dividend_yield, last_updated, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (asset_id, spot, vol, rate, dividend, datetime.now().isoformat(), source),
        )

        conn.commit()
        conn.close()
        logger.info(f"Cached market data for {asset_id}")

    def get_all(self) -> Dict[str, Dict]:
        """Get all cached market data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT asset_id, spot_price, volatility, risk_free_rate,
                   dividend_yield, last_updated, data_source
            FROM market_data
        """)

        rows = cursor.fetchall()
        conn.close()

        result = {}
        for row in rows:
            result[row[0]] = {
                "spot": row[1],
                "vol": row[2],
                "rate": row[3],
                "dividend": row[4],
                "last_updated": row[5],
                "source": row[6],
            }

        return result

    def delete(self, asset_id: str) -> bool:
        """Delete market data for an asset."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM market_data WHERE asset_id = ?", (asset_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted

    def clear(self):
        """Clear all cached data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM market_data")

        conn.commit()
        conn.close()
        logger.info("Cleared all cached market data")
