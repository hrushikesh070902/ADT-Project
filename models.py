# models.py

from flask_login import UserMixin
from sqlalchemy.sql import func
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    user_id   = db.Column(db.Integer, primary_key=True)
    email     = db.Column(db.String(100), unique=True, nullable=False)
    password  = db.Column(db.String(255), nullable=False)
    role      = db.Column(db.Enum('Nurse','Doctor','Manager','Admin'), nullable=False)

    # Relationships
    supply_requests = db.relationship(
        'SupplyRequest',
        back_populates='user',
        cascade='all, delete-orphan'
    )
    reorders = db.relationship(
        'Reorder',
        back_populates='ordered_by_user',
        cascade='all, delete-orphan'
    )
    notifications = db.relationship(
        'Notification',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    def get_id(self):
        # Flask-Login expects this to return a string
        return str(self.user_id)


class Item(db.Model):
    __tablename__ = 'Item'
    item_id       = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), unique=True, nullable=False)
    stock         = db.Column(db.Integer, nullable=False)
    reorder_level = db.Column(db.Integer, nullable=False)

    # Relationships
    supply_requests = db.relationship(
        'SupplyRequest',
        back_populates='item',
        cascade='all, delete-orphan'
    )
    reorders = db.relationship(
        'Reorder',
        back_populates='item',
        cascade='all, delete-orphan'
    )
    vendors = db.relationship(
        'ItemVendor',
        back_populates='item',
        cascade='all, delete-orphan'
    )


class Vendor(db.Model):
    __tablename__ = 'Vendor'
    vendor_id    = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), unique=True, nullable=False)
    contact_info = db.Column(db.Text)

    # Relationships
    item_vendors = db.relationship(
        'ItemVendor',
        back_populates='vendor',
        cascade='all, delete-orphan'
    )
    reorders = db.relationship(
        'Reorder',
        back_populates='vendor',
        cascade='all, delete-orphan'
    )


class ItemVendor(db.Model):
    __tablename__ = 'ItemVendor'
    item_vendor_id = db.Column(db.Integer, primary_key=True)
    item_id        = db.Column(
                        db.Integer,
                        db.ForeignKey('Item.item_id', ondelete='CASCADE'),
                        nullable=False
                     )
    vendor_id      = db.Column(
                        db.Integer,
                        db.ForeignKey('Vendor.vendor_id', ondelete='CASCADE'),
                        nullable=False
                     )

    # Relationships
    item   = db.relationship('Item', back_populates='vendors')
    vendor = db.relationship('Vendor', back_populates='item_vendors')


class SupplyRequest(db.Model):
    __tablename__ = 'SupplyRequest'
    request_id   = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(
                       db.Integer,
                       db.ForeignKey('User.user_id', ondelete='CASCADE'),
                       nullable=False
                   )
    item_id      = db.Column(
                       db.Integer,
                       db.ForeignKey('Item.item_id', ondelete='CASCADE'),
                       nullable=False
                   )
    quantity     = db.Column(db.Integer, nullable=False)
    reason       = db.Column(db.Text)
    status       = db.Column(
                       db.Enum('Waiting for Approval','Approved','Not Approved'),
                       nullable=False,
                       default='Waiting for Approval'
                   )
    requested_at = db.Column(
                       db.DateTime,
                       server_default=func.current_timestamp()
                   )

    # Relationships
    user = db.relationship('User', back_populates='supply_requests')
    item = db.relationship('Item', back_populates='supply_requests')


class Notification(db.Model):
    __tablename__ = 'Notification'
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(
                          db.Integer,
                          db.ForeignKey('User.user_id', ondelete='CASCADE'),
                          nullable=False
                      )
    message         = db.Column(db.Text, nullable=False)
    created_at      = db.Column(
                          db.DateTime,
                          server_default=func.current_timestamp()
                      )

    # Relationship
    user = db.relationship('User', back_populates='notifications')


class Reorder(db.Model):
    __tablename__ = 'Reorder'
    reorder_id  = db.Column(db.Integer, primary_key=True)
    item_id     = db.Column(
                     db.Integer,
                     db.ForeignKey('Item.item_id', ondelete='CASCADE'),
                     nullable=False
                 )
    vendor_id   = db.Column(
                     db.Integer,
                     db.ForeignKey('Vendor.vendor_id', ondelete='CASCADE'),
                     nullable=False
                 )
    ordered_by  = db.Column(
                     db.Integer,
                     db.ForeignKey('User.user_id', ondelete='CASCADE'),
                     nullable=False
                 )
    quantity    = db.Column(db.Integer, nullable=False)
    status      = db.Column(
                     db.Enum('Ordered','Delivered','Canceled'),
                     nullable=False,
                     default='Ordered'
                 )
    ordered_at  = db.Column(
                     db.DateTime,
                     server_default=func.current_timestamp()
                 )

    # Relationships
    item            = db.relationship('Item', back_populates='reorders')
    vendor          = db.relationship('Vendor', back_populates='reorders')
    ordered_by_user = db.relationship('User', back_populates='reorders')
