# Deployment Guide

Instructions for deploying the Risk Engine dashboard.

## Local Deployment

### Running the Dashboard

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Run Streamlit
streamlit run dashboard/app.py
```

Access at `http://localhost:8501`

### Custom Port

```bash
streamlit run dashboard/app.py --server.port 8080
```

### Allow External Access

```bash
streamlit run dashboard/app.py --server.address 0.0.0.0
```

## Streamlit Cloud Deployment

The easiest way to deploy publicly.

### Steps

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `dashboard/app.py` as the main file
5. Deploy

### Requirements

Ensure `requirements.txt` is in the repository root with all dependencies.

## Cloud Platform Deployment

### Heroku

**Procfile:**
```
web: streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0
```

**Deploy:**
```bash
heroku create risk-engine-app
git push heroku main
```

### Railway

1. Connect GitHub repository
2. Set start command:
   ```
   streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0
   ```
3. Deploy

### Render

**render.yaml:**
```yaml
services:
  - type: web
    name: risk-engine
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0
```

## Server Deployment (Linux)

### Using systemd

**1. Setup application:**
```bash
# Create app directory
sudo mkdir -p /opt/risk-engine
cd /opt/risk-engine

# Clone and setup
git clone https://github.com/yourusername/risk-engine.git .
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Create systemd service:**

`/etc/systemd/system/risk-engine.service`:
```ini
[Unit]
Description=Risk Engine Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/risk-engine
ExecStart=/opt/risk-engine/.venv/bin/streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**3. Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable risk-engine
sudo systemctl start risk-engine
```

### Nginx Reverse Proxy

`/etc/nginx/sites-available/risk-engine`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/risk-engine /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Configuration

### Environment Variables

```bash
# Market data cache duration (hours)
export MARKET_DATA_CACHE_HOURS=24

# Default risk-free rate
export DEFAULT_RISK_FREE_RATE=0.045
```

### Streamlit Configuration

Create `.streamlit/config.toml`:
```toml
[server]
headless = true
port = 8501
enableCORS = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
```

## Monitoring

### Health Check

The dashboard root URL can serve as a health check endpoint.

### Logs

**systemd logs:**
```bash
journalctl -u risk-engine -f
```

**Streamlit logs:**
Check console output or redirect to file.

## Security Considerations

1. **HTTPS**: Use SSL certificates (Let's Encrypt)
2. **Firewall**: Only expose necessary ports
3. **Updates**: Keep dependencies updated
4. **Access**: Consider adding authentication for production

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8501
# Kill it
kill -9 <PID>
```

### Memory Issues

Streamlit caches data. If memory grows:
```python
# In your app, periodically clear cache
st.cache_data.clear()
```

### Slow Cold Starts

Numba JIT compilation causes slow first load. Consider:
- Warming up the cache on startup
- Using persistent deployment (not serverless)
