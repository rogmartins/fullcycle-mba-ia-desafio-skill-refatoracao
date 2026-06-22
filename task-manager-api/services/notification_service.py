import smtplib
from datetime import datetime, timezone
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

# REFACTORED: utcnow() depreciado substituído por datetime.now(timezone.utc) (AP-10)
def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class NotificationService:
    def __init__(self):
        self.notifications = []
        # REFACTORED: credenciais lidas de variáveis de ambiente via config.py (AP-01)
        self.email_host = SMTP_HOST
        self.email_port = SMTP_PORT
        self.email_user = SMTP_USER
        self.email_password = SMTP_PASSWORD

    def send_email(self, to, subject, body):
        if not self.email_user or not self.email_password:
            return False
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            return True
        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\nPrioridade: {task.priority}\nStatus: {task.status}"
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': _utcnow()
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n['user_id'] == user_id]
