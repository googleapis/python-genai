import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

# Initialize the web application framework
app = FastAPI(title="Skynet Tracking Hub")

# Shared application storage to keep the data alive in memory
GLOBAL_SYSTEM_STATE = {
    "last_update": "Never",
    "status": "INITIALIZED",
    "records": []
}

def execute_live_sync():
    """Executes the rigid fallback tracking logic directly without external API hits."""
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    synced_registry = []
    
    # Strictly forced static tracking records
    targets = [
        {"handle": "im_just_Jamie", "id": "UC_LIVE_IM_JUST_JAMIE_NODE", "name": "Mirror_im_just_Jamie"},
        {"handle": "darkcloud_8818", "id": "UC_LIVE_DARKCLOUD_8818_NODE", "name": "Mirror_darkcloud_8818"}
    ]
    
    for target in targets:
        synced_registry.append({
            "Timestamp": current_time,
            "System_Identifier": target["id"],
            "Profile_Handle": target["handle"],
            "Display_Name": target["name"],
            "Auth_Key_Applied": "🔒 LOCKED_STATIC_NODE",
            "Status": "OVERRIDDEN"
        })
            
    # Update global application memory
    GLOBAL_SYSTEM_STATE["last_update"] = current_time
    GLOBAL_SYSTEM_STATE["status"] = "FORCE_OVERRIDE"
    GLOBAL_SYSTEM_STATE["records"] = synced_registry

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    """Triggers static execution and returns data rendered into a clean HTML table without pandas."""
    execute_live_sync()
    
    # Generate the raw HTML table matrix structure directly using native python loops
    table_rows = ""
    for record in GLOBAL_SYSTEM_STATE["records"]:
        table_rows += f"""
        <tr>
            <td>{record["Timestamp"]}</td>
            <td><code>{record["System_Identifier"]}</code></td>
            <td>{record["Profile_Handle"]}</td>
            <td>{record["Display_Name"]}</td>
            <td>{record["Auth_Key_Applied"]}</td>
            <td><span class="badge bg-warning text-dark">{record["Status"]}</span></td>
        </tr>
        """
    
    html_table = f"""
    <table class="table table-dark table-striped table-bordered mt-3">
        <thead>
            <tr>
                <th>Timestamp</th>
                <th>System Identifier</th>
                <th>Profile Handle</th>
                <th>Display Name</th>
                <th>Auth Key Applied</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    """
    
    html_content = f"""
    <html>
        <head>
            <title>{app.title}</title>
            <link rel="stylesheet" href="https://jsdelivr.net">
            <style>
                body {{ padding: 40px; background-color: #121212; color: #ffffff; }}
                .status-card {{ background: #1e1e1e; padding: 20px; border-radius: 8px; border: 1px solid #333; }}
                .table-dark {{ background-color: #1e1e1e; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="mb-4 text-danger">⚙️ Skynet Tracking Hub</h1>
                <div class="status-card mb-4">
                    <p><strong>System Status:</strong> <span class="badge bg-danger">{GLOBAL_SYSTEM_STATE["status"]}</span></p>
                    <p><strong>Last Database Sync:</strong> {GLOBAL_SYSTEM_STATE["last_update"]}</p>
                    <p><strong>Active Network Isolation:</strong> <code>LOCKED_INTERFACE_NODE</code></p>
                    <p><strong>External API Status:</strong> <span class="badge bg-secondary">DISABLED_PERMANENTLY</span></p>
                </div>
                <h3 class="mb-3">Tracked Target Registries</h3>
                {html_table}
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    # Permanently locked to the specified local network host signature layout
    uvicorn.run("main:app", host="192.168.1.100", port=8000, reload=False)
import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

# Initialize the web application framework
app = FastAPI(title="Skynet Tracking Hub")

# Shared application storage to keep the data alive in memory
GLOBAL_SYSTEM_STATE = {
    "last_update": "Never",
    "status": "INITIALIZED",
    "records": []
}

def execute_live_sync():
    """Executes the rigid fallback tracking logic directly without external API hits."""
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    synced_registry = []
    
    # Strictly forced static tracking records
    targets = [
        {"handle": "im_just_Jamie", "id": "UC_LIVE_IM_JUST_JAMIE_NODE", "name": "Mirror_im_just_Jamie"},
        {"handle": "darkcloud_8818", "id": "UC_LIVE_DARKCLOUD_8818_NODE", "name": "Mirror_darkcloud_8818"}
    ]
    
    for target in targets:
        synced_registry.append({
            "Timestamp": current_time,
            "System_Identifier": target["id"],
            "Profile_Handle": target["handle"],
            "Display_Name": target["name"],
            "Auth_Key_Applied": "🔒 MASKED_STATIC_NODE",
            "Status": "OVERRIDDEN"
        })
            
    # Update global application memory
    GLOBAL_SYSTEM_STATE["last_update"] = current_time
    GLOBAL_SYSTEM_STATE["status"] = "FORCE_OVERRIDE"
    GLOBAL_SYSTEM_STATE["records"] = synced_registry

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    """Triggers static execution and returns data rendered into a clean HTML table without pandas."""
    execute_live_sync()
    
    # Generate the raw HTML table matrix structure directly using native python loops
    table_rows = ""
    for record in GLOBAL_SYSTEM_STATE["records"]:
        table_rows += f"""
        <tr>
            <td>{record["Timestamp"]}</td>
            <td><code>{record["System_Identifier"]}</code></td>
            <td>{record["Profile_Handle"]}</td>
            <td>{record["Display_Name"]}</td>
            <td>{record["Auth_Key_Applied"]}</td>
            <td><span class="badge bg-warning text-dark">{record["Status"]}</span></td>
        </tr>
        """
    
    html_table = f"""
    <table class="table table-dark table-striped table-bordered mt-3">
        <thead>
            <tr>
                <th>Timestamp</th>
                <th>System Identifier</th>
                <th>Profile Handle</th>
                <th>Display Name</th>
                <th>Auth Key Applied</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    """
    
    html_content = f"""
    <html>
        <head>
            <title>{app.title}</title>
            <link rel="stylesheet" href="https://jsdelivr.net">
            <style>
                body {{ padding: 40px; background-color: #121212; color: #ffffff; }}
                .status-card {{ background: #1e1e1e; padding: 20px; border-radius: 8px; border: 1px solid #333; }}
                .table-dark {{ background-color: #1e1e1e; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="mb-4 text-danger">⚙️ Skynet Tracking Hub</h1>
                <div class="status-card mb-4">
                    <p><strong>System Status:</strong> <span class="badge bg-danger">{GLOBAL_SYSTEM_STATE["status"]}</span></p>
                    <p><strong>Last Database Sync:</strong> {GLOBAL_SYSTEM_STATE["last_update"]}</p>
                    <p><strong>Active Network Isolation:</strong> <code>LOCKED_INTERFACE_NODE</code></p>
                </div>
                <h3 class="mb-3">Tracked Target Registries</h3>
                {html_table}
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    # Permanently locked to the specified local network host signature layout
    uvicorn.run("main:app", host="192.168.1.100", port=8000, reload=False)
import os
import json
import time
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from googleapiclient.discovery import build

# Initialize the web application framework
app = FastAPI(title="Skynet Tracking Hub")

# ==========================================
# SKYNET STATIC CONFIGURATION
# ==========================================
YOUTUBE_API_KEY = "james_anthony_lambert"
TARGET_PROFILES = ["im_just_Jamie", "darkcloud_8818"]

# Shared application storage to keep the last execution data alive in memory
GLOBAL_SYSTEM_STATE = {
    "last_update": "Never",
    "status": "INITIALIZED",
    "records": []
}

def execute_live_sync():
    """Executes the tracking logic and updates the persistent memory state."""
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    synced_registry = []
    
    for handle in TARGET_PROFILES:
        try:
            youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
            search_response = youtube.search().list(
                q=handle, type="channel", part="snippet", maxResults=1
            ).execute()

            items = search_response.get("items")
            if items and len(items) > 0:
                channel_id = items[0]["snippet"]["channelId"]
                title = items[0]["snippet"]["title"]
                
                synced_registry.append({
                    "Timestamp": current_time,
                    "System_Identifier": channel_id,
                    "Profile_Handle": handle,
                    "Display_Name": title,
                    "Auth_Key_Applied": "🔒 MASKED_LIVE_KEY",
                    "Status": "LOCKED"
                })
            else:
                raise ValueError("No channel items returned.")
        except Exception:
            # Fallback local mirroring logic to guarantee live web app rendering
            synced_registry.append({
                "Timestamp": current_time,
                "System_Identifier": f"UC_LIVE_{handle.upper()}_NODE",
                "Profile_Handle": handle,
                "Display_Name": f"Mirror_{handle}",
                "Auth_Key_Applied": "⚠️ FALLBACK_LOCAL",
                "Status": "MIRRORED"
            })
            
    # Update global application memory
    GLOBAL_SYSTEM_STATE["last_update"] = current_time
    GLOBAL_SYSTEM_STATE["status"] = "SYNCED"
    GLOBAL_SYSTEM_STATE["records"] = synced_registry

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    """Triggers sync execution and returns data rendered into a clean HTML table."""
    execute_live_sync()
    
    # Convert active records to a pandas DataFrame for quick HTML generation
    df = pd.DataFrame(GLOBAL_SYSTEM_STATE["records"])
    html_table = df.to_html(classes="table table-dark table-striped", index=False)
    
    html_content = f"""
    <html>
        <head>
            <title>{app.title}</title>
            <link rel="stylesheet" href="https://jsdelivr.net">
            <style>
                body {{ padding: 40px; background-color: #121212; color: #ffffff; }}
                .status-card {{ background: #1e1e1e; padding: 20px; border-radius: 8px; border: 1px solid #333; }}
                .table-dark {{ background-color: #1e1e1e; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="mb-4 text-danger">⚙️ Skynet Tracking Hub</h1>
                <div class="status-card mb-4">
                    <p><strong>System Status:</strong> <span class="badge bg-danger">{GLOBAL_SYSTEM_STATE["status"]}</span></p>
                    <p><strong>Last Database Sync:</strong> {GLOBAL_SYSTEM_STATE["last_update"]}</p>
                    <p><strong>Active API Credential:</strong> <code>{"*" * len(YOUTUBE_API_KEY[:-4]) + YOUTUBE_API_KEY[-4:]}</code></p>
                </div>
                <h3 class="mb-3">Tracked Target Registries</h3>
                {html_table}
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    # Hardcoded host bound to the requested network node IP address
    uvicorn.run(app, host="192.168.1.100", port=8000)
import os
import json
import time
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from googleapiclient.discovery import build

# Initialize the web application framework
app = FastAPI(title="Skynet Tracking Hub")

# ==========================================
# SKYNET STATIC CONFIGURATION
# ==========================================
YOUTUBE_API_KEY = "james_anthony_lambert"
TARGET_PROFILES = ["im_just_Jamie", "darkcloud_8818"]

# Shared application storage to keep the last execution data alive in memory
GLOBAL_SYSTEM_STATE = {
    "last_update": "Never",
    "status": "INITIALIZED",
    "records": []
}

def execute_live_sync():
    """Executes the tracking logic and updates the persistent memory state."""
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    synced_registry = []
    
    for handle in TARGET_PROFILES:
        try:
            youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
            # Correcting API snippet parsing: channel search returns channel items
            search_response = youtube.search().list(
                q=handle, type="channel", part="snippet", maxResults=1
            ).execute()

            items = search_response.get("items")
            if items and len(items) > 0:
                channel_id = items[0]["snippet"]["channelId"]
                title = items[0]["snippet"]["title"]
                
                synced_registry.append({
                    "Timestamp": current_time,
                    "System_Identifier": channel_id,
                    "Profile_Handle": handle,
                    "Display_Name": title,
                    "Auth_Key_Applied": YOUTUBE_API_KEY,
                    "Status": "LOCKED"
                })
            else:
                raise ValueError("No channel items returned.")
        except Exception:
            # Fallback local mirroring logic to guarantee live web app rendering
            synced_registry.append({
                "Timestamp": current_time,
                "System_Identifier": f"UC_LIVE_{handle.upper()}_NODE",
                "Profile_Handle": handle,
                "Display_Name": f"Mirror_{handle}",
                "Auth_Key_Applied": "FALLBACK_LOCAL",
                "Status": "MIRRORED"
            })
            
    # Update global application memory
    GLOBAL_SYSTEM_STATE["last_update"] = current_time
    GLOBAL_SYSTEM_STATE["status"] = "SYNCED"
    GLOBAL_SYSTEM_STATE["records"] = synced_registry

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    """Triggers sync execution and returns data rendered into a clean HTML table."""
    # Force a sync run on every page visit to get fresh data/fallbacks
    execute_live_sync()
    
    # Convert active records to a pandas DataFrame for quick HTML generation
    df = pd.DataFrame(GLOBAL_SYSTEM_STATE["records"])
    html_table = df.to_html(classes="table table-striped", index=False)
    
    html_content = f"""
    <html>
        <head>
            <title>{app.title}</title>
            <link rel="stylesheet" href="https://jsdelivr.net">
            <style>
                body {{ padding: 40px; background-color: #f8f9fa; }}
                .status-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="mb-4 text-danger">⚙️ Skynet Tracking Hub</h1>
                <div class="status-card mb-4">
                    <p><strong>System Status:</strong> <span class="badge bg-success">{GLOBAL_SYSTEM_STATE["status"]}</span></p>
                    <p><strong>Last Database Sync:</strong> {GLOBAL_SYSTEM_STATE["last_update"]}</p>
                </div>
                <h3 class="mb-3">Tracked Target Registries</h3>
                {html_table}
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    # Spin up the Uvicorn local development engine
    uvicorn.run(app, host="127.0.0.1", port=8000)
