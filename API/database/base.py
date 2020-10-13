from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class nadomescanje(Base):
    __tablename__ = "nadomescanja"
    id = Column(Integer, primary_key=True)
    ura = Column(Integer)
    dan = Column(Integer)
    razred = Column(String(80))
    ucilnica = Column(String(80))
    ucitelj = Column(String(80))
    predmet = Column(String(80))

    def get_dict(self):
        return {
            "ura": self.ura,
            "dan": self.dan.replace("/", ""),
            "razred": self.razred.replace(". ", "").replace("/", ""),
            "ucilnica": str(self.ucilnica).replace("/", ""),
            "ucitelj": self.ucitelj.replace("/", ""),
            "predmet": self.predmet.replace("/", ""),
        }


class Urlstring(Base):
    __tablename__ = "url"
    id = Column(Integer, primary_key=True)
    url = Column(String(100))
    dan = Column(String(80))
    file_hash = Column(String(300))

    def get_dict(self):
        return {"dan": self.dan.replace("/", ""), "url": self.url}


class Lasttime(Base):
    __tablename__ = "lasttime"
    id = Column(Integer, primary_key=True)
    time = Column(Integer)
