"""
Сервис аутентификации для системы генерации профилей А101.

Обеспечивает:
- Проверку учетных данных пользователей
- Генерацию и валидацию JWT токенов
- Управление пользовательскими сессиями
- Хеширование паролей с использованием bcrypt
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from ..models.database import db_manager
from ..models.schemas import LoginRequest, LoginResponse, UserInfo
from ..core.config import config
import logging

logger = logging.getLogger(__name__)

# Настройки JWT из конфигурации
JWT_SECRET_KEY = config.JWT_SECRET_KEY
JWT_ALGORITHM = config.JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

# Настройки хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationService:
    """Сервис аутентификации и авторизации пользователей"""
    
    def __init__(self):
        self.db = db_manager
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля против хеша"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except JWTError:
            return False
    
    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return pwd_context.hash(password)
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по username"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, password_hash, full_name, is_active, created_at, last_login
                FROM users 
                WHERE username = ? AND is_active = TRUE
            """, (username,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row["id"],
                    "username": row["username"],
                    "password_hash": row["password_hash"],
                    "full_name": row["full_name"],
                    "is_active": bool(row["is_active"]),
                    "created_at": datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
                    "last_login": datetime.fromisoformat(row["last_login"]) if row["last_login"] else None
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Аутентификация пользователя по username и password"""
        user = self.get_user_by_username(username)
        
        if not user:
            logger.warning(f"Authentication failed: user {username} not found")
            return None
        
        if not user["is_active"]:
            logger.warning(f"Authentication failed: user {username} is inactive")
            return None
        
        if not self.verify_password(password, user["password_hash"]):
            logger.warning(f"Authentication failed: invalid password for user {username}")
            return None
        
        # Обновляем время последнего входа
        self._update_last_login(user["id"])
        
        logger.info(f"User {username} authenticated successfully")
        return user
    
    def _update_last_login(self, user_id: int):
        """Обновление времени последнего входа пользователя"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (user_id,))
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {e}")
    
    def create_access_token(self, user_data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Создание JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Данные для включения в токен
        token_data = {
            "sub": str(user_data["id"]),  # subject (user ID)
            "username": user_data["username"],
            "full_name": user_data["full_name"],
            "exp": expire,  # expiration time
            "iat": datetime.utcnow(),  # issued at
            "type": "access_token"
        }
        
        encoded_jwt = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка и декодирование JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Проверяем тип токена
            if payload.get("type") != "access_token":
                return None
            
            # Проверяем существование пользователя
            user_id = int(payload.get("sub"))
            user = self.get_user_by_id(user_id)
            
            if not user or not user["is_active"]:
                return None
            
            # КРИТИЧНО: Проверяем наличие активных сессий пользователя
            # Если все сессии инвалидированы (логаут), токен считается недействительным
            if not self._has_active_sessions(user_id):
                logger.warning(f"Token rejected: user {user_id} has no active sessions")
                return None
            
            return {
                "user_id": user_id,
                "username": payload.get("username"),
                "full_name": payload.get("full_name"),
                "exp": payload.get("exp"),
                "user": user
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение пользователя по ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, password_hash, full_name, is_active, created_at, last_login
                FROM users 
                WHERE id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row["id"],
                    "username": row["username"],
                    "password_hash": row["password_hash"],
                    "full_name": row["full_name"],
                    "is_active": bool(row["is_active"]),
                    "created_at": datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
                    "last_login": datetime.fromisoformat(row["last_login"]) if row["last_login"] else None
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    def create_user_session(self, user_id: int, user_agent: str = None, ip_address: str = None) -> str:
        """Создание пользовательской сессии в базе данных"""
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO user_sessions (id, user_id, expires_at, is_active, user_agent, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, expires_at, True, user_agent, ip_address))
            
            conn.commit()
            logger.info(f"Created session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating user session: {e}")
            raise
    
    def invalidate_user_sessions(self, user_id: int):
        """Инвалидация всех сессий пользователя (logout из всех устройств)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE user_sessions 
                SET is_active = FALSE 
                WHERE user_id = ? AND is_active = TRUE
            """, (user_id,))
            
            conn.commit()
            logger.info(f"Invalidated all sessions for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error invalidating user sessions: {e}")
    
    def invalidate_session(self, session_id: str):
        """Инвалидация конкретной сессии"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE user_sessions 
                SET is_active = FALSE 
                WHERE id = ?
            """, (session_id,))
            
            conn.commit()
            logger.info(f"Invalidated session {session_id}")
            
        except Exception as e:
            logger.error(f"Error invalidating session {session_id}: {e}")
    
    async def login(self, login_request: LoginRequest, user_agent: str = None, ip_address: str = None) -> Optional[LoginResponse]:
        """Полный процесс авторизации пользователя"""
        try:
            # Аутентификация
            user = self.authenticate_user(login_request.username, login_request.password)
            if not user:
                return None
            
            # Создание токена
            token_expiration = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 7 if login_request.remember_me else JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(user, expires_delta=token_expiration)
            
            # Создание сессии
            session_id = self.create_user_session(user["id"], user_agent, ip_address)
            
            # Подготовка ответа
            user_info = UserInfo(
                id=user["id"],
                username=user["username"],
                full_name=user["full_name"],
                is_active=user["is_active"],
                created_at=user["created_at"],
                last_login=user["last_login"]
            )
            
            expires_in = int(token_expiration.total_seconds())
            
            response = LoginResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=expires_in,
                user_info=user_info,
                success=True,
                message=f"Добро пожаловать, {user['full_name']}!"
            )
            
            logger.info(f"User {user['username']} logged in successfully")
            return response
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return None
    
    def _has_active_sessions(self, user_id: int) -> bool:
        """Проверка наличия активных сессий у пользователя"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) as active_count
                FROM user_sessions 
                WHERE user_id = ? AND is_active = TRUE AND expires_at > CURRENT_TIMESTAMP
            """, (user_id,))
            
            result = cursor.fetchone()
            active_count = result["active_count"] if result else 0
            
            return active_count > 0
            
        except Exception as e:
            logger.error(f"Error checking active sessions for user {user_id}: {e}")
            # В случае ошибки БД, разрешаем доступ (fail-open)
            return True
    
    def cleanup_expired_sessions(self):
        """Очистка истекших сессий (вызывается периодически)"""
        try:
            self.db.cleanup_expired_sessions()
            logger.info("Expired sessions cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")


# Глобальный экземпляр сервиса аутентификации
auth_service = AuthenticationService()


if __name__ == "__main__":
    # Тестирование сервиса аутентификации
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    async def test_auth_service():
        print("🔐 Тестирование AuthenticationService...")
        
        # Инициализируем базу данных
        db_manager.create_schema()
        db_manager.seed_initial_data()
        
        # Тест аутентификации существующего пользователя
        login_req = LoginRequest(username=config.ADMIN_USERNAME, password=config.ADMIN_PASSWORD)
        
        result = await auth_service.login(login_req, "test-user-agent", "127.0.0.1")
        
        if result:
            print("✅ Аутентификация успешна")
            print(f"📱 Пользователь: {result.user_info.full_name}")
            print(f"🔑 Токен: {result.access_token[:50]}...")
            print(f"⏰ Истекает через: {result.expires_in} секунд")
            
            # Тест проверки токена
            token_data = auth_service.verify_token(result.access_token)
            if token_data:
                print("✅ Токен валиден")
                print(f"👤 Пользователь из токена: {token_data['username']}")
            else:
                print("❌ Токен невалиден")
        else:
            print("❌ Аутентификация не удалась")
        
        # Тест неправильного пароля
        wrong_login = LoginRequest(username="admin", password="wrong_password")
        wrong_result = await auth_service.login(wrong_login)
        
        if wrong_result:
            print("❌ Неправильная аутентификация прошла (ошибка!)")
        else:
            print("✅ Неправильная аутентификация корректно отклонена")
        
        print("🎉 Тестирование завершено!")
    
    # Запуск тестов
    asyncio.run(test_auth_service())