from sqlalchemy import create_engine, Column, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "sqlite:///./images.sqlite3"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ImageProcessing(Base):
    __tablename__ = "image_processing"
    id = Column(String(36), primary_key=True)
    data = Column(JSON, nullable=False)
    status = Column(String(50), nullable=False)


Base.metadata.create_all(bind=engine)
