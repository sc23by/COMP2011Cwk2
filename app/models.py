from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Relationships
    posts = db.relationship('Post', backref='author', cascade="all, delete-orphan")
    reactions = db.relationship('Reaction', backref='user', cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='author', cascade="all, delete-orphan")

    followed = db.relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        backref='follower', lazy='dynamic'
    )
    followers = db.relationship(
        'Follow',
        foreign_keys='Follow.followed_id',
        backref='followed', lazy='dynamic'
    )

# Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    # Relationships
    reactions = db.relationship('Reaction', backref='post', cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='post', cascade="all, delete-orphan")

# Reaction model
class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reaction_type = db.Column(db.String(10), nullable=False)  # "like" or "dislike"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)

    # Unique constraint: user can react to a post only once
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_reaction'),)

# Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)

# Follow model
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete="CASCADE"),  # Cascade deletion for follower
        nullable=False
    )
    followed_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete="CASCADE"),  # Cascade deletion for followed
        nullable=False
    )
