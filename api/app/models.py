import enum
from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from app import db


class Role(enum.Enum):
    ADMIN = "admin"
    SALES = "sales"
    SUPPORT = "support"


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(sa.String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(sa.String(120),index=True, unique=True)
    phone: Mapped[str] = mapped_column()
    role: Mapped[Role] = mapped_column(nullable=False)
    password: Mapped[Optional[str]] = mapped_column(sa.String(256))


