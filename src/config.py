import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration for BANK_RATS CC CHECKER BOT🐀"""
    
    # Bot Information
    BOT_NAME = "BANK_RATS"
    BOT_EMOJI = "🐀💳"
    BOT_USERNAME = "@Bank_Rats"
    OWNER_USERNAME = "@Bank_Rats"
    OWNER_DISPLAY_NAME = "𝓑𝓐𝓝𝓚_𝓡𝓐𝓣𝓢 𝓥𝓮𝓻𝓲𝓯𝓲𝓮𝓭"
    ADMIN_ID = 7200774078  # User's Telegram ID
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', "7808962933:AAEvQ_KG0Au24RK_Btez7rMvI_n1ozwWW9A")
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', None)
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///bank_rats_checker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'bank_rats_cc_checker_secret_2025')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_bank_rats_2025')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Payment Configuration
    MPESA_NUMBER = "+254746362427"
    BINANCE_EMAIL = "migosblazer4@gmail.com"
    
    # Pricing (USD)
    PRICING = {
        'monthly': 3.0,
        'lifetime': 5.0
    }
    
    # Credit System & Points
    REGISTRATION_BONUS_CREDITS = 50
    CREDITS_PER_CHECK = {
        'free': 5,
        'monthly': 2,
        'lifetime': 1
    }
    
    # Tier System Configuration
    TIER_NAMES = {
        'free': 'FREE',
        'monthly': 'PREMIUM (Monthly)',
        'lifetime': 'LIFETIME'
    }
    
    TIER_COSTS = {
        'free': '$0',
        'monthly': '~$3 (Ksh converted)',
        'lifetime': '~$5 (Ksh converted)'
    }
    
    # Tier Limitations
    TIER_LIMITS = {
        'free': {
            'checks_per_day': 5,
            'gateways': 1,
            'allowed_commands': [
                'start', 'register', 'check', 'buy', 'credits', 'referral', 
                'myreferrals', 'me', 'disclaimer'
            ]
        },
        'monthly': {
            'checks_per_day': 50,
            'gateways': 'multiple',
            'allowed_commands': [
                'start', 'register', 'check', 'masschk', 'generate', 'generateinfo',
                'bin', 'buy', 'credits', 'referral', 'myreferrals', 'me', 'disclaimer'
            ]
        },
        'lifetime': {
            'checks_per_day': -1,  # Unlimited
            'gateways': 'all',
            'allowed_commands': [
                'start', 'register', 'check', 'masschk', 'generate', 'generateinfo',
                'bin', 'deepchk', 'binstats', 'vault', 'autocharge', 'binweekly',
                'log', 'buy', 'credits', 'referral', 'myreferrals', 'me', 'disclaimer'
            ]
        }
    }
    
    # Owner-only commands
    OWNER_COMMANDS = ['users', 'broadcast']
    
    # Command Categories with descriptions
    COMMAND_DESCRIPTIONS = {
        'start': 'Begins user session',
        'register': 'One-time per user registration',
        'check': 'Basic CC check (1 gateway for Free)',
        'masschk': 'Multiple CCs checking',
        'generate': 'Fake CC generation',
        'generateinfo': 'Fake profile generation',
        'bin': 'BIN lookup',
        'deepchk': 'Deep CC check',
        'binstats': 'BIN statistics',
        'vault': 'Premium vault',
        'autocharge': 'Auto charge feature',
        'binweekly': 'Weekly BIN drops',
        'log': 'View past checks',
        'buy': 'Payment instructions',
        'credits': 'Show current balance',
        'referral': 'Get referral link',
        'myreferrals': 'Stats on referrals',
        'me': 'User profile',
        'disclaimer': 'Legal notice',
        'users': '🔐OWNER ONLY - List all users',
        'broadcast': '🔐OWNER ONLY - Admin global announcement'
    }
    
    # Styling Configuration - Gothic/Dark Theme
    GOTHIC_STYLE = {
        'separator': '━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        'card_icon': '[そ]',
        'gateway_icon': '[ヸ]',
        'response_icon': '[仝]',
        'info_icon': '[そ]',
        'bank_icon': '[ヸ]',
        'country_icon': '[仝]',
        'footer_start': '╚━━━━━━「 𝑰𝑵𝑭𝑶 」━━━━━━╝',
        'footer_end': '╚━━━━━━「𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐂𝐇𝐄𝐂𝐊𝐄𝐑」━━━━━━╝',
        'proxy_icon': '⚜️',
        'time_icon': '⚜️',
        'checked_by_icon': '⚜️',
        'owner_icon': '⚜️'
    }
    
    # Response Messages
    MESSAGES = {
        'not_registered': """❌ You are not registered yet!
Please type /register to activate your account and start using the bot. 🚀

Need assistance? Contact the owner here: @Bank_Rats""",
        
        'registration_success': """🎉 Welcome to BANK_RATS 🐀💳
You have been registered successfully!

💰 50 free credits have been added to your account.
Use /check to start checking now.
🔥 Use /buy to upgrade for full features & unlimited checks!""",
        
        'tier_restricted': """⛔ You are not allowed to use this command.

💡 Upgrade your tier using /buy to unlock this feature.""",
        
        'owner_only': """🚫 This command is restricted to the Owner Only.

For questions, contact @Bank_Rats.""",
        
        'unknown_command': """❓ Unknown command. Use /allcmdlist to see available commands.""",
        
        'payment_instructions': """💰 <b>Payment Instructions</b> 💰

✅ <b>Accepted Payments:</b>
💳 Binance (Email: migosblazer4@gmail.com)
📲 M-PESA: +254746362427

📸 <b>Upload payment screenshot here ⬇️</b>

💎 <b>Pricing:</b>
• Monthly Premium: $3 USD
• Lifetime Access: $5 USD

💱 <b>KSH Conversion:</b> Automatically calculated at current rates""",
        
        'disclaimer': """⚠️ <b>Disclaimer Notice</b> ⚠️

❌ <i>I do not own, host, or affiliate myself with any of the services, banks, institutions, payment gateways, or platforms used or referenced in this bot.</i>

❌ <i>This bot is solely intended for educational and informational purposes only. Any actions taken by users are their sole responsibility.</i>

❌ <i>I am NOT affiliated with Telegram or any third-party providers integrated in this tool.</i>

🔐 <b>By using this bot, you agree that you understand and accept this disclaimer. Use responsibly.</b>"""
    }
    
    # External APIs for real data
    BIN_LOOKUP_APIS = [
        "https://lookup.binlist.net/",
        "https://api.bintable.com/v1/",
        "https://bin-ip-checker.p.rapidapi.com/"
    ]
    
    # Charged checking endpoints (placeholder - would need real APIs)
    CHARGED_ENDPOINTS = {
        'stripe': 'https://api.stripe.com/v1/',
        'paypal': 'https://api.paypal.com/v1/',
        'braintree': 'https://api.braintreegateway.com/',
        'square': 'https://connect.squareup.com/v2/',
        'adyen': 'https://checkout-test.adyen.com/v1/'
    }
    
    # Rate Limiting
    RATE_LIMITS = {
        'free_user_per_hour': 10,
        'premium_user_per_hour': 100,
        'admin_per_hour': 1000
    }
    
    # File Upload Configuration
    MAX_SCREENSHOT_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_SCREENSHOT_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    
    # Currency Configuration
    CURRENCY_API_TIMEOUT = 10
    CURRENCY_CACHE_DURATION = 3600  # 1 hour
    FALLBACK_USD_TO_KSH_RATE = 130.0
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Security Settings
    BCRYPT_LOG_ROUNDS = 12
    
    # Feature Flags
    REAL_BIN_CHECKING = True
    REAL_CHARGED_CHECKING = True
    MANUAL_PAYMENT_CONFIRMATION = True
    ADMIN_NOTIFICATIONS = True
    
    # Cooldown periods (in seconds)
    COOLDOWNS = {
        'check': 60,        # 1 minute
        'masschk': 300,     # 5 minutes
        'generate': 180,    # 3 minutes
        'bin': 120,         # 2 minutes
        'deepchk': 600      # 10 minutes
    }
    
    # Referral System
    REFERRAL_BONUS_CREDITS = 25
    
    @staticmethod
    def init_app(app):
        """Initialize app with configuration"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        app.config.from_object(Config)
    
    @staticmethod
    def is_admin(user_id):
        """Check if user is admin"""
        return user_id == Config.ADMIN_ID
    
    @staticmethod
    def get_tier_limit(tier, command_type):
        """Get tier limit for specific command type"""
        return Config.TIER_LIMITS.get(tier, {}).get(command_type, 0)
    
    @staticmethod
    def can_use_command(user_tier, command):
        """Check if user tier can use specific command"""
        if command in Config.OWNER_COMMANDS:
            return False  # Only owner can use these
        
        allowed_commands = Config.TIER_LIMITS.get(user_tier, {}).get('allowed_commands', [])
        return command in allowed_commands
    
    @staticmethod
    def format_styled_response(card_data, gateway_data, response_data, user_data, timing_data):
        """Format a styled CC check response"""
        style = Config.GOTHIC_STYLE
        
        response = f"""{style['separator']}
{style['card_icon']} 𝑪𝒂𝒓𝒅- {card_data['number']}|{card_data['month']}|{card_data['year']}|{card_data['cvv']} 
{style['gateway_icon']} 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - {gateway_data['name']} [{gateway_data['amount']}]✅
{style['response_icon']} 𝑹𝒆𝒔𝒑𝒐𝒏𝒔𝐞- ⤿ {response_data['status']}🔥 ⤾
{style['separator']}
{style['info_icon']} 𝑰𝒏𝒇𝒐- {card_data['brand']} - {card_data['type']} - {card_data['level']}
{style['bank_icon']} 𝑩𝒂𝒏𝒌- {card_data['bank']} 
{style['country_icon']} 𝑪𝒐𝒖𝒏𝒕𝒓𝒚- {card_data['country']} - {card_data['flag']} - {card_data['currency']}
{style['separator']}
{style['footer_start']}
{style['proxy_icon']} 𝑷𝒓𝒐𝒙𝒚 -» 𝑷𝒓𝒐𝒙𝒚 𝑳𝒊𝒗𝒆✅
{style['time_icon']} 𝑻𝒊𝒎𝒆 𝑺𝒑𝒆𝒏𝒕 -» {timing_data['duration']} seconds
{style['checked_by_icon']} 𝑪𝒉𝒆𝒌𝒆𝒅 𝒃𝒚:  {Config.BOT_NAME} [ {user_data['tier'].upper()} ]
{style['owner_icon']} 𝑶𝒘𝒏𝒆𝒓: {Config.OWNER_DISPLAY_NAME}
{style['footer_end']}"""
        
        return response

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
