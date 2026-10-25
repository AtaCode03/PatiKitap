from datetime import datetime, timezone
from sqlalchemy import (MetaData, String, Text, Integer, Boolean, DateTime, Uuid,
                        ForeignKey, UniqueConstraint, CheckConstraint, Index)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def now(): return datetime.now(timezone.utc)
class Base(DeclarativeBase):
    metadata = MetaData(schema='app')
class Profile(Base):
    __tablename__ = 'profiles'
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(80))
    city: Mapped[str] = mapped_column(String(100), default='Konya')
    bio: Mapped[str] = mapped_column(String(500), default='')
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
class Book(Base):
    __tablename__ = 'books'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    author: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(50))
    kind: Mapped[str] = mapped_column(String(20))
    publisher: Mapped[str] = mapped_column(String(160), default='')
    price: Mapped[int] = mapped_column(default=0)
    condition: Mapped[str] = mapped_column(String(40))
    location: Mapped[str] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String, default='#005f86')
    owner_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey('app.profiles.id'), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    isbn: Mapped[str] = mapped_column(String(13), default='')
    image_url: Mapped[str] = mapped_column(String(1000), default='')
    status: Mapped[str] = mapped_column(String(20), default='active', index=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (CheckConstraint("status in ('active','reserved','completed','archived','hidden')", name='book_status'),)
class Request(Base):
    __tablename__ = 'requests'
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey('app.books.id'), index=True)
    requester_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey('app.profiles.id'), index=True)
    offered_book_id: Mapped[int | None] = mapped_column(ForeignKey('app.books.id'), index=True)
    message: Mapped[str] = mapped_column(String(1000), default='')
    status: Mapped[str] = mapped_column(String(20), default='pending', index=True)
    delivery_method: Mapped[str] = mapped_column(String(20), default='campus')
    shipping_payer: Mapped[str] = mapped_column(String(20), default='recipient')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (CheckConstraint("status in ('pending','accepted','rejected','cancelled')", name='request_status'),
        Index('one_pending_request', 'book_id', 'requester_id', unique=True,
              postgresql_where=__import__('sqlalchemy').text("status='pending'"), sqlite_where=__import__('sqlalchemy').text("status='pending'")))
class Transaction(Base):
    __tablename__ = 'transactions'
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey('app.requests.id'), unique=True)
    book_id: Mapped[int] = mapped_column(ForeignKey('app.books.id'), index=True)
    offered_book_id: Mapped[int | None] = mapped_column(ForeignKey('app.books.id'),index=True)
    owner_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey('app.profiles.id'), index=True)
    requester_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey('app.profiles.id'), index=True)
    kind: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default='accepted', index=True)
    price_cents: Mapped[int] = mapped_column(Integer, default=0)
    fee_cents: Mapped[int] = mapped_column(Integer, default=0)
    support_cents: Mapped[int] = mapped_column(Integer, default=0)
    support_rate_bps: Mapped[int] = mapped_column(Integer, default=2000)
    owner_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    requester_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint("status in ('accepted','in_delivery','completed','cancelled','disputed')", name='transaction_status'),
        CheckConstraint('price_cents >= 0 and support_cents >= 0 and fee_cents >= 0 and support_cents + fee_cents <= price_cents',name='transaction_amounts'))
class Delivery(Base):
    __tablename__ = 'deliveries'
    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey('app.transactions.id'), index=True)
    sender_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey('app.profiles.id'),index=True)
    recipient_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey('app.profiles.id'),index=True)
    method: Mapped[str] = mapped_column(String(20))
    shipping_payer: Mapped[str] = mapped_column(String(20))
    cost_cents: Mapped[int] = mapped_column(Integer, default=0)
    tracking_number: Mapped[str] = mapped_column(String(100), default='')
    carrier: Mapped[str] = mapped_column(String(80), default='')
    meeting_point: Mapped[str] = mapped_column(String(200), default='')
    status: Mapped[str] = mapped_column(String(20), default='pending')
    __table_args__ = (UniqueConstraint('transaction_id','sender_id'),CheckConstraint('cost_cents >= 0',name='shipping_cost'))
class SupportRecord(Base):
    __tablename__ = 'support_records'
    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey('app.transactions.id'), unique=True)
    amount_cents: Mapped[int] = mapped_column(Integer)
    mode: Mapped[str] = mapped_column(String(20), default='simulation')
    status: Mapped[str] = mapped_column(String(20), default='recorded')
    organization: Mapped[str] = mapped_column(String(160), default='')
    document_url: Mapped[str] = mapped_column(String(1000), default='')
    note: Mapped[str] = mapped_column(String(1000), default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (CheckConstraint("mode = 'simulation'",name='support_simulation_only'),CheckConstraint('amount_cents > 0',name='support_positive'))
class Favorite(Base):
    __tablename__ = 'favorites'
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey('app.profiles.id'), primary_key=True)
    # Deliberately no FK to books: a saved listing remains visible to its followers
    # as "removed" after the owner permanently deletes it.
    book_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    saved_price: Mapped[int | None] = mapped_column(Integer)
    snapshot_title: Mapped[str | None] = mapped_column(String(160))
    snapshot_author: Mapped[str | None] = mapped_column(String(120))
    snapshot_kind: Mapped[str | None] = mapped_column(String(20))
    snapshot_status: Mapped[str | None] = mapped_column(String(20))
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
class Notification(Base):
    __tablename__ = 'notifications'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey('app.profiles.id'), index=True)
    message: Mapped[str] = mapped_column(String(500))
    transaction_id: Mapped[int | None] = mapped_column(ForeignKey('app.transactions.id'),index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
class Complaint(Base):
    __tablename__ = 'complaints'
    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey('app.profiles.id'), index=True)
    book_id: Mapped[int | None] = mapped_column(ForeignKey('app.books.id'),index=True)
    transaction_id: Mapped[int | None] = mapped_column(ForeignKey('app.transactions.id'),index=True)
    reason: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(20), default='open', index=True)
    resolution: Mapped[str] = mapped_column(String(1000), default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey('app.profiles.id'), index=True)
    action: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str] = mapped_column(String(40))
    entity_id: Mapped[str] = mapped_column(String(80))
    detail: Mapped[str] = mapped_column(String(1000), default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
