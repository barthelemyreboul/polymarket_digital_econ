# python
import sqlite3
from typing import Any, Dict, List, Optional, Sequence, Union

Params = Optional[Union[Sequence[Any], Dict[str, Any]]]

def run_sql(db_path: str = "polymarket.db", sql: str = "", params: Params = None, fetch: str = "all") -> Union[int, List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Run a simple SQL statement against `db_path`.
    - For SELECT: returns list[dict] (fetch='all') or dict/None (fetch='one').
    - For non-SELECT: returns cursor.rowcount (number of affected rows).
    """
    is_select = sql.strip().lower().startswith("select")
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql, params or ())
        if is_select:
            if fetch == "one":
                row = cur.fetchone()
                return dict(row) if row is not None else None
            return [dict(r) for r in cur.fetchall()]
        return cur.rowcount

# Example usage:
# rows = run_sql(sql="SELECT * FROM market_data LIMIT 5")
# one = run_sql(sql="SELECT * FROM market_data WHERE id = ?", params=(1,), fetch="one")
# inserted = run_sql(sql="INSERT INTO market_data (event_title) VALUES (?)", params=("Title",))
