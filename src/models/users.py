from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from enum import Enum
import uuid

db = SQLAlchemy()

class SubscriptionType(Enum):
    FREE = "free"
    MONTHLY = "monthly"
    LIFETIME = "lifetime"

class PaymentMethod(Enum):
    MPESA = "mpesa"
    BINANCE = "binance"

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class User(db.Model):
    __tablename__ = \'users\'
    
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), nullable=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    
    # Registration and activity
    is_registered = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Credits and subscription
    credits = db.Column(db.Integer, default=0, nullable=False)
    subscription_type = db.Column(db.Enum(SubscriptionType), default=SubscriptionType.FREE, nullable=False)
    subscription_expires_at = db.Column(db.DateTime, nullable=True)
    
    # Referral system
    referral_code = db.Column(db.String(20), unique=True, nullable=True)
    referred_by_id = db.Column(db.Integer, db.ForeignKey(\'users.id\'), nullable=True)
    total_referrals = db.Column(db.Integer, default=0, nullable=False)
    paid_referrals = db.Column(db.Integer, default=0, nullable=False)
    
    # Usage tracking
    total_checks = db.Column(db.Integer, default=0, nullable=False)
    checks_today = db.Column(db.Integer, default=0, nullable=False)
    last_check_date = db.Column(db.Date, nullable=True)
    
    # Relationships
    credit_transactions = db.relationship(\'CreditTransaction\', backref=\'user\', lazy=\'dynamic\')
    validation_logs = db.relationship(\'ValidationLog\', backref=\'user\', lazy=\'dynamic\')
    payments = db.relationship(\'Payment\', backref=\'user\', lazy=\'dynamic\')
    referrals = db.relationship(\'User\', backref=db.backref(\'referrer\', remote_side=[id]), lazy=\'dynamic\')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
    
    def generate_referral_code(self):
        \"\"\"Generate unique referral code\"\"\"
        return f"BR{str(uuid.uuid4())[:8].upper()}"
    
    def get_tier(self):
        \"\"\"Get user\'s current tier\"\"\"
        if self.subscription_type == SubscriptionType.LIFETIME:
            return "lifetime"
        elif self.subscription_type == SubscriptionType.MONTHLY:
            if self.subscription_expires_at and self.subscription_expires_at > datetime.utcnow():
                return "monthly"
            else:
                # Expired monthly subscription
                self.subscription_type = SubscriptionType.FREE
                db.session.commit()
                return "free"
        else:
            return "free"
    
    def can_use_command(self, command, tier_limits=None):
        \"\"\"Check if user can use a specific command\"\"\"
        from src.config import Config
        
        if not self.is_registered and command != \'register\':
            return False
        
        tier = self.get_tier()
        return Config.can_use_command(tier, command)
    
    def has_credits_for_check(self):
        \"\"\"Check if user has enough credits for a check\"\"\"
        from src.config import Config
        
        tier = self.get_tier()
        credits_needed = Config.CREDITS_PER_CHECK.get(tier, 5)
        return self.credits >= credits_needed
    
    def deduct_credits_for_check(self):
        \"\"\"Deduct credits for a check\"\"\"
        from src.config import Config
        
        tier = self.get_tier()
        credits_needed = Config.CREDITS_PER_CHECK.get(tier, 5)
        
        if self.credits >= credits_needed:
            self.credits -= credits_needed
            
            # Create transaction record
            transaction = CreditTransaction(
                user=self,
                amount=-credits_needed,
                transaction_type=\'check\',
                description=f\'CC check ({tier} tier)\'
            )
            db.session.add(transaction)
            
            # Update daily check count
            today = datetime.utcnow().date()
            if self.last_check_date != today:
                self.checks_today = 0
                self.last_check_date = today
            
            self.checks_today += 1
            self.total_checks += 1
            
            db.session.commit()
            return True
        
        return False
    
    def can_check_today(self):
        \"\"\"Check if user can perform more checks today\"\"\"
        from src.config import Config
        
        tier = self.get_tier()
        daily_limit = Config.TIER_LIMITS.get(tier, {}).get(\'checks_per_day\', 0)
        
        if daily_limit == -1:  # Unlimited
            return True
        
        today = datetime.utcnow().date()
        if self.last_check_date != today:
            return True
        
        return self.checks_today < daily_limit
    
    def add_credits(self, amount, transaction_type=\'bonus\', description=\'\'):
        \"\"\"Add credits to user account\"\"\"
        self.credits += amount
        
        transaction = CreditTransaction(
            user=self,
            amount=amount,
            transaction_type=transaction_type,
            description=description
        )
        db.session.add(transaction)
        db.session.commit()
    
    def upgrade_subscription(self, subscription_type, duration_months=None):
        \"\"\"Upgrade user subscription\"\"\"
        self.subscription_type = SubscriptionType(subscription_type)
        
        if subscription_type == \'monthly\' and duration_months:
            self.subscription_expires_at = datetime.utcnow() + timedelta(days=30 * duration_months)
        elif subscription_type == \'lifetime\':
            self.subscription_expires_at = None
        
        db.session.commit()
    
    def add_referral(self, referred_user_id):
        \"\"\"Add a referral when someone uses this user\'s referral code\"\"\"
        self.total_referrals += 1
        db.session.commit()
    
    def confirm_paid_referral(self):
        \"\"\"Confirm a paid referral and give bonus\"\"\"
        from src.config import Config
        
        self.paid_referrals += 1
        self.add_credits(
            Config.REFERRAL_BONUS_CREDITS,
            \'referral_bonus\',
            \'Referral bonus for paid user\'
        )
    
    def get_referral_link(self):
        \"\"\"Get referral link for this user\"\"\"
        from src.config import Config
        return f"https://t.me/{Config.BOT_USERNAME}?start=ref_{self.referral_code}"
    
    def to_dict(self ):
        \"\"\"Convert user to dictionary\"\"\"
        return {
            \'id\': self.id,
            \'telegram_id\': self.telegram_id,
            \'username\': self.username,
            \'first_name\': self.first_name,
            \'last_name\': self.last_name,
            \'is_registered\': self.is_registered,
            \'credits\': self.credits,
            \'tier\': self.get_tier(),
            \'subscription_type\': self.subscription_type.value,
            \'total_checks\': self.total_checks,
            \'total_referrals\': self.total_referrals,
            \'paid_referrals\': self.paid_referrals,
            \'created_at\': self.created_at.isoformat(),
            \'last_activity\': self.last_activity.isoformat()
        }

class CreditTransaction(db.Model):
    __tablename__ = \'credit_transactions\'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(\'users.id\'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Positive for credit, negative for debit
    transaction_type = db.Column(db.String(50), nullable=False)  # \'bonus\', \'check\', \'referral_bonus\', \'purchase\'
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class ValidationLog(db.Model):
    __tablename__ = \'validation_logs\'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(\'users.id\'), nullable=False)
    card_number = db.Column(db.String(20), nullable=False)  # Masked for security
    gateway = db.Column(db.String(100), nullable=False)
    result = db.Column(db.String(50), nullable=False)  # \'approved\', \'declined\', \'error\'
    response_time = db.Column(db.Float, nullable=False)  # In seconds
    bin_info = db.Column(db.JSON, nullable=True)  # Store BIN lookup results
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Payment(db.Model):
    __tablename__ = \'payments\'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(\'users.id\'), nullable=False)
    payment_id = db.Column(db.String(50), unique=True, nullable=False)
    amount_usd = db.Column(db.Float, nullable=False)
    amount_ksh = db.Column(db.Float, nullable=True)
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False)
    subscription_type = db.Column(db.Enum(SubscriptionType), nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    screenshot_path = db.Column(db.String(500), nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)
        if not self.payment_id:
            self.payment_id = f"PAY_{str(uuid.uuid4())[:12].upper()}"

class AdminNotification(db.Model):
    __tablename__ = \'admin_notifications\'
    
    id = db.Column(db.Integer, primary_key=True)
    notification_type = db.Column(db.String(50), nullable=False)  # \'payment\', \'new_user\', \'error\'
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(\'users.id\'), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class BinCache(db.Model):
    __tablename__ = \'bin_cache\'
    
    id = db.Column(db.Integer, primary_key=True)
    bin_number = db.Column(db.String(8), unique=True, nullable=False, index=True)
    bin_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at

