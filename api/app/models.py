from datetime import datetime, timezone
import enum
from typing import Optional
from typing_extensions import List
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db


class Role(enum.Enum):
    ADMIN = "admin"
    SALES = "sales"
    SUPPORT = "support"


class Status(enum.Enum):
    PENDING = "pending"
    SIGNED = "signed"


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(sa.String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(sa.String(120),index=True, unique=True)
    phone: Mapped[str] = mapped_column()
    role: Mapped[Role] = mapped_column(nullable=False)
    password: Mapped[Optional[str]] = mapped_column(sa.String(256))
    clients: Mapped[Optional[List["Client"]]] = relationship(back_populates='sales_contact')
    contracts: Mapped[Optional[List["Contract"]]] = relationship(back_populates='sales_contact')


class Client(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(sa.String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(sa.String(120),index=True, unique=True)
    phone: Mapped[str] = mapped_column(sa.String(12))
    company: Mapped[str] = mapped_column(sa.String(120))
    sales_contact_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey('user.id'))
    sales_contact: Mapped['User'] = relationship(back_populates='clients')
    contracts: Mapped[Optional[List["Contract"]]] = relationship(back_populates='client')
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))


class Contract(db.Model):
    def __init__(self, total_amount, status=Status.PENDING, *args, **kwargs) -> None:
        self.remaining_amount = total_amount
        self.status = status
        super().__init__(*args, **kwargs)

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey('client.id'))
    client: Mapped['Client'] = relationship(back_populates='contracts')
    sales_contact_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey('user.id'))
    sales_contact: Mapped['User'] = relationship(back_populates='contracts')
    total_amount: Mapped[float] = mapped_column(sa.Float)
    remaining_amount: Mapped[float] = mapped_column(sa.Float)
    status: Mapped[Status] = mapped_column(default=Status.PENDING)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))



# Relations:
# 1. User[sales] can have many clients
# 1. User[sales] can have many contracts
# 1. User[support] can have many events

# Relations:
# 1. Clients can have many contracts
# 1. Clients must have one sales_contact
#
# Contract:
# 1. id: int/uuid
# 1. client_id: Client.id
# 1. sales_contact: Client.sales_contact
# 1. total_amount: float
# 1. remaining_amount: float
# 1. created_at: date
# 1. status: str(pending/signed)
#
# Relations:
# 1. Contracts belong one event
#
# Event:
# 1. id: int/uuid
# 1. title: str
# 1. contract_id: Contract.id
# 1. client_name: Client.full_name
# 1. sales_contact: User[sales].id
# 1. event_date_start: datetime
# 1. event_date_end: datetime
# 1. support_contact: User[support].id
# 1. location: str
# 1. attendees: int
# 1. notes: str
