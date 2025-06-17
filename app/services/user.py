from typing import Optional
from sqlmodel import Session, select

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import BaseService
from app.utils.security import hash_password
from app.core.exceptions import ValidationException

class UserService(BaseService[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return db.exec(statement).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        # Check if user with email already exists
        if self.get_by_email(db, email=obj_in.email):
            raise ValidationException(f"User with email {obj_in.email} already exists")
        
        # Hash password
        hashed_password = hash_password(obj_in.password)
        
        # Create user object
        db_obj = User(
            email=obj_in.email,
            name=obj_in.name,
            role=obj_in.role,
            password_hash=hashed_password
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: UserUpdate
    ) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # If password is being updated, hash it
        if "password" in update_data:
            update_data["password_hash"] = hash_password(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user_service = UserService(User) 