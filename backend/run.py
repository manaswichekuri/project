"""Development entrypoint. In production the app is served by gunicorn via wsgi.py."""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('APP_ENV', 'development') == 'development'
    print(f"🚀 Starting AI Insider Threat Detection API on port {port} (Debug: {debug})...")
    app.run(host='0.0.0.0', port=port, debug=debug)
