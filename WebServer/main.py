# uvicorn main:app --reload --host 0.0.0.0 --port 8000

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import io
import os
import matplotlib.pyplot as plt
import datagrapher

app = FastAPI()
root_dir = os.path.dirname(os.path.dirname(__file__))
logs_dir = os.path.join(root_dir, "Logs")

@app.get("/")
def root():
    os.makedirs(logs_dir, exist_ok=True)

    files = [f for f in os.listdir(logs_dir) if f.endswith(".csv")]

    base_url = "/{category}/{can_id}?file="
    file_links = {f: base_url + f for f in files}

    return {
        "message": "Data Grapher API",
        "logs": files,
        "endpoints": file_links
    }

@app.get("/{category}/{can_id}")
def graph_data(category: str, can_id: str, file: str = Query("log.csv")):
    """
    Example: http://10.9.141.1:8000/INV_Motor_Speed/A5?file=your_log.csv
    """
    filename = os.path.join(logs_dir, file)

    if not os.path.exists(filename):
        return {"error": f"File {file} not found"}

    can_id_int = int(can_id, 16)

    signal_data = datagrapher.extract_from_csv(filename, category, can_id_int)
    if not signal_data:
        return {"error": f"No data found for {category} on CAN ID {can_id}"}

    times = [t for (v, t) in signal_data]
    values = [v for (v, t) in signal_data]

    fig, ax = plt.subplots(figsize=(14, 6), dpi=150)
    vmax, vmin = max(values), min(values)
    ax.set_title(f"{category} (Max={vmax:.2f}, Min={vmin:.2f})")
    ax.set_facecolor("#1a1a23")
    ax.set(xlabel="Timestamp (s)", ylabel=category)
    ax.plot(times, values, marker="o", markersize=2, linewidth=1, c="#02d0f5")
    fig.subplots_adjust(left=0.06, right=0.98, bottom=0.1, top=0.9)

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    return StreamingResponse(buf, media_type="image/png")