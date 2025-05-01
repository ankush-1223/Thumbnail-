# Telegram Cloner Bot (Keyob Edition)

## Deployment Steps

1. **Fork this repo** (or upload files manually)
2. **On Keyob**:
   - Create new application
   - Connect to your GitHub repo
   - Go to **Environment Variables** and add:
     - `API_ID`, `API_HASH`, `BOT_TOKEN`, `ADMIN_ID`
3. **Start Deployment**:
   - Builder Pack: 
     ```bash
     pip install -r requirements.txt
     python bot.py
     ```
   - Docker: 
     ```bash
     docker build -t clonerbot . && docker run -d clonerbot
     ```

## Post-Deployment
- Configure via Telegram:
