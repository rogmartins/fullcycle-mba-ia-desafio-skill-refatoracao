from database import db
from datetime import datetime, timezone
import hashlib
import os

# REFACTORED: utcnow() depreciado substituído por datetime.now(timezone.utc) (AP-10)
def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=_utcnow)

    def to_dict(self):
        # REFACTORED: campo password removido da resposta da API (AP-04)
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at)
        }

    def set_password(self, pwd):
        # REFACTORED: MD5 substituído por PBKDF2-HMAC-SHA256 com sal aleatório (AP-01)
        salt = os.urandom(16).hex()
        dk = hashlib.pbkdf2_hmac('sha256', pwd.encode(), salt.encode(), 100000)
        self.password = f"{salt}:{dk.hex()}"

    def check_password(self, pwd):
        # REFACTORED: verificação compatível com PBKDF2 (AP-01)
        try:
            salt, stored_hash = self.password.split(':', 1)
        except ValueError:
            return False
        dk = hashlib.pbkdf2_hmac('sha256', pwd.encode(), salt.encode(), 100000)
        return dk.hex() == stored_hash

    def is_admin(self):
        return self.role == 'admin'
