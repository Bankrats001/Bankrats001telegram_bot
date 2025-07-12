#!/usr/bin/env python3
"""
BANK_RATS CC CHECKER BOT🐀 - Standalone Runner
This script runs the bot without Flask to avoid threading issues
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Ensure src is in Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
src_path = os.path.join(project_root, 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask app for database context"""
    from flask import Flask
    from src.config import Config  # Corrected import
    from src.models.user import db  # Corrected import
    
    app = Flask(__name__)
    Config.init_app(app)
    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    return app

def main():
    """Main function to run the bot"""
    try:
        # Create Flask app for database
        app = create_app()
        
        # Get bot token
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            return
        
        # Initialize bot
        from src.services.telegram_bot_advanced import BankRatsCCCheckerBot # Corrected import
        bot = BankRatsCCCheckerBot(bot_token, app)
        
        logger.info("Starting BANK_RATS CC CHECKER BOT🐀...")
        
        # Run bot
        bot.run_polling()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise

if __name__ == '__main__':
    main()
