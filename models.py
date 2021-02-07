from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, DateTime

Base = declarative_base()


class IdMixin:
    id = Column(Integer, autoincrement=True, primary_key=True)


class UrlMixin:
    url = Column(String, unique=True, nullable=False)


class NameMixin:
    name = Column(String, nullable=False)


tag_post = Table(
    "tag_post",
    Base.metadata,
    Column('post_id', Integer, ForeignKey("post.id")),
    Column('tag_id', Integer, ForeignKey("tag.id")),
)


class Post(IdMixin, UrlMixin, Base):
    __tablename__ = "post"
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("author.id"))
    url_image = Column(String, nullable=False)
    date_public = Column(DateTime, nullable=False)
    author = relationship("Author")
    tags = relationship("Tag", secondary=tag_post)
    comments = relationship("Comment")


class Author(IdMixin, UrlMixin, NameMixin, Base):
    __tablename__ = "author"
    posts = relationship("Post")


class Tag(IdMixin, UrlMixin, NameMixin, Base):
    __tablename__ = "tag"
    posts = relationship("Post", secondary=tag_post)


class Comment(IdMixin, Base):
    __tablename__ = "comment"
    post_id = Column(Integer, ForeignKey("post.id"))
    author = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    posts = relationship("Post")
