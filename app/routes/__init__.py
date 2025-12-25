from app.routes.main import bp as main_bp
from app.routes.auth import bp as auth_bp
from app.routes.staff.admin_crud import bp as admin_crud_bp

__all__ = [
    'main_bp',
    'auth_bp',
    'admin_crud_bp'
]