from src.app import create_app
from src.db.client import Base, engine

Base.metadata.create_all(bind=engine)
app = create_app()
