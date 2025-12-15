from app.routes.main import bp as main_bp
from app.routes.auth import bp as auth_bp
from app.routes.staff.brand import bp as brand_bp
from app.routes.staff.body_type import bp as body_type_bp

__all__ = ['main_bp', 'auth_bp', 'brand_bp', 'body_type_bp']