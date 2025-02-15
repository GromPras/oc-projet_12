from datetime import datetime, timedelta, timezone, tzinfo
import enum
import secrets
from typing import Optional
from typing_extensions import List
import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    DeclarativeBase,
    validates,
)
from app import db
from werkzeug.security import check_password_hash, generate_password_hash


class Base(DeclarativeBase):
    pass


class Role(enum.Enum):
    ADMIN = "admin"
    SALES = "sales"
    SUPPORT = "support"


class ContractStatus(enum.Enum):
    PENDING = "pending"
    SIGNED = "signed"


sales_events = db.Table(
    "sales_events",
    db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
    db.Column("event_id", db.ForeignKey("event.id"), primary_key=True),
)


support_events = db.Table(
    "support_events",
    db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
    db.Column("event_id", db.ForeignKey("event.id"), primary_key=True),
)

# TODO: add author on every model for delete permissions
# TODO: add author (will serve for event creation restrictions)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(sa.String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(sa.String(120), index=True, unique=True)
    phone: Mapped[str] = mapped_column(sa.String(12))
    role: Mapped[Role] = mapped_column(nullable=False)
    password: Mapped[Optional[str]] = mapped_column(sa.String(256))
    token: Mapped[Optional[str]] = mapped_column(sa.String(32), index=True, unique=True)
    token_expiration: Mapped[Optional[datetime]]
    clients: Mapped[Optional[List["Client"]]] = relationship(
        back_populates="sales_contact"
    )
    contracts: Mapped[Optional[List["Contract"]]] = relationship(
        back_populates="sales_contact"
    )

    @property
    def serialize(self):
        """The serialize property."""
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            "phone": self.phone,
            "role": self.role.value,
        }

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_token(self, expires_in=3600):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration.replace(
            tzinfo=timezone.utc
        ) > now + timedelta(seconds=60):
            return self.token
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def get_roles(self):
        return self.role.value

    def deserialize(self, data, new_user=False):
        for field in ["fullname", "email", "phone", "role"]:
            if field in data:
                setattr(self, field, data[field])
            if new_user and "password" in data:
                self.set_password(data["password"])

    @staticmethod
    def check_token(token):
        user = db.session.scalar(sa.select(User).where(User.token == token))
        if user is None or user.token_expiration.replace(
            tzinfo=timezone.utc
        ) < datetime.now(timezone.utc):
            return None
        return user

    # event_sales: Mapped[Optional[List["Event"]]] = relationship(
    #     secondary=sales_events, back_populates="sales_contact"
    # )
    # event_support: Mapped[Optional[List["Event"]]] = relationship(
    #     secondary=support_events, back_populates="support_contact"
    # )


class Client(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(sa.String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(sa.String(120), index=True, unique=True)
    phone: Mapped[str] = mapped_column(sa.String(12))
    company: Mapped[str] = mapped_column(sa.String(120))
    sales_contact_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("user.id"))
    sales_contact: Mapped["User"] = relationship(
        back_populates="clients", foreign_keys=[sales_contact_id]
    )
    contracts: Mapped[Optional[List["Contract"]]] = relationship(
        back_populates="client"
    )
    events: Mapped[Optional[List["Event"]]] = relationship(back_populates="client")
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    def get_sales_contact(self):
        return self.sales_contact.serialize if self.sales_contact else None

    @property
    def serialize(self):
        """The serialize property."""
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "sales_contact": self.get_sales_contact(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def deserialize(self, data):
        for field in ["fullname", "email", "phone", "company", "sales_contact"]:
            if field in data:
                setattr(self, field, data[field])


class Contract(db.Model):
    def __init__(self, status=ContractStatus.PENDING, *args, **kwargs) -> None:
        self.status = status
        super().__init__(*args, **kwargs)

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("client.id"))
    client: Mapped["Client"] = relationship(back_populates="contracts")
    sales_contact_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("user.id"))
    sales_contact: Mapped["User"] = relationship(
        back_populates="contracts", foreign_keys=[sales_contact_id]
    )
    total_amount: Mapped[float] = mapped_column(sa.Float)
    remaining_amount: Mapped[float] = mapped_column(sa.Float)
    status: Mapped[ContractStatus] = mapped_column(default=ContractStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    events: Mapped[Optional[List["Event"]]] = relationship(back_populates="contract")

    @validates("total_amount")
    def set_remaining_amount(self, _, total_amount):
        if self.remaining_amount is None:
            self.remaining_amount = total_amount
        return total_amount


class Event(db.Model):
    __tablename__ = "event"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(120))
    contract_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("contract.id"))
    contract: Mapped["Contract"] = relationship(back_populates="events")
    client_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("client.id"))
    client: Mapped["Client"] = relationship(
        back_populates="events", foreign_keys=[client_id]
    )
    sales_contact_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("user.id"))
    sales_contact: Mapped["User"] = relationship(
        secondary=sales_events,
        backref="events_sales",
    )
    # make support contact optional
    support_contact_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("user.id")
    )
    support_contact: Mapped["User"] = relationship(
        secondary=support_events,
        backref="events_support",
    )
    event_start: Mapped[datetime] = mapped_column()
    event_end: Mapped[datetime] = mapped_column()
    location: Mapped[str] = mapped_column(sa.String(120))
    attendees: Mapped[int] = mapped_column(sa.Integer)
    # make notes optional
    notes: Mapped[Optional[str]] = mapped_column(sa.Text())
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
