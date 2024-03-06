from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from gitee_ranking.config import settings

engine = create_engine(settings.sqlalchemy_database_uri, echo=False, pool_recycle=3600)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base_ = declarative_base()


class Base(Base_):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class Class(Base):
    __tablename__ = "class"
    name = Column(String(50), unique=True)


class ClassMember(Base):
    __tablename__ = "class_member"
    name = Column(String(50), nullable=True)
    email = Column(String(50), nullable=True)

    class_id = Column(Integer, ForeignKey("class.id"))
    group_id = Column(Integer, ForeignKey("group.id"))


class Group(Base):
    __tablename__ = "group"
    name = Column(String(50))
    repo_url = Column(String(100), nullable=True)

    commit_count = Column(Integer, nullable=True)
    pull_request_count = Column(Integer, nullable=True)
    issue_count = Column(Integer, nullable=True)

    class_id = Column(Integer, ForeignKey("class.id"))


class Log(Base):
    __tablename__ = "log"

    class_id = Column(Integer, ForeignKey("class.id"))
