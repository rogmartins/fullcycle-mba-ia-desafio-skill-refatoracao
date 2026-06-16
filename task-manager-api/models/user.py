from database import db
from datetime import datetime
# REFACTORED: werkzeug.security substitui hashlib.md5 — pbkdf2_sha256 com salt automático
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        # REFACTORED: campo 'password' removido — hash nunca deve ser exposto na API
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at)
        }

    def set_password(self, pwd):
        # REFACTORED: pbkdf2_sha256 com salt automático substitui MD5 sem salt
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def is_admin(self):
        return self.role == 'admin'
