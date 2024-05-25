import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db import BaseModel
from app.helpers import auth


class User(BaseModel):
    """
    Model to store user information
    """

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(sa.String(255), index=True, unique=True)
    password: Mapped[str] = mapped_column(sa.String(500))
    name: Mapped[str] = mapped_column(sa.String(255))

    def set_password_hash(self, password: str) -> None:
        """
        Set hashed password
        """
        self.password = auth.get_hashed_password(password)

    def verify_password(self, plain_password: str) -> bool:
        """
        Verify password
        """
        return auth.verify_password(plain_password, self.password)
