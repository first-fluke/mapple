"""Auth FastAPI dependencies.

get_current_user_id: Bearer JWS 검증 후 user_id(sub claim) 반환.
src.lib.auth.get_current_user_id와 동일한 구현을 재-export합니다.
새 코드에서는 이 모듈을 import하세요.
"""

from src.lib.auth import get_current_user_id

__all__ = ["get_current_user_id"]
