try:
    from app.database.database import Base, engine
    from app.database.models import Consultation
except ModuleNotFoundError:
    from backend.app.database.database import Base, engine
    from backend.app.database.models import Consultation

Base.metadata.create_all(bind=engine)

print(f"Base de donnees creee. Table disponible: {Consultation.__tablename__}")
