from fastapi import FastAPI
from telemetry import TelemetryManager
import sqlite3
import threading
from contextlib import contextmanager

telem = TelemetryManager()
app = FastAPI()

@contextmanager
def get_db():
    conn = sqlite3.connect('telemetry_data.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@app.get('/')
def root():
    """Startup CAN message logging services and list data sources."""
    threading.Thread(target=telem.queue_can, daemon=True).start()
    threading.Thread(target=telem.log_can, daemon=True).start()

    with get_db() as conn:
        cursor = conn.cursor()

        data = {}
        tables = [
            "PEI_Diagnostic_BMS_Data",
            "PEI_Status",
            "M160_Temperature_Set_1",
            "M162_Temperature_Set_3",
            "M171_Fault_Codes",
            "Dashboard_Vehicle_State",
            "M169_Internal_Voltages",
        ]

        for table in tables:
            cursor.execute(f"SELECT * FROM {table} ORDER BY Timestamp")
            data[table] = [dict(row) for row in cursor.fetchall()]

        return data

@app.get("/data/{table_name}")
def get_data(table_name: str):
    """Get data from SQL table."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY Timestamp")
        rows = cursor.fetchall()
    return [dict(row) for row in rows]