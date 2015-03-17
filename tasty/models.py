__author__ = 'kristjin@github'

from flask import url_for

from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


combinations = Table("combinations", Base.metadata,
                     Column("flavor1_id", Integer,
                            ForeignKey("flavors.id"),
                            primary_key=True),
                     Column("flavor2_id", Integer,
                            ForeignKey("flavors.id"),
                            primary_key=True)
                     )


class Flavor(Base):
    __tablename__ = "flavors"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    combinations = relationship("Flavor",
                                secondary=combinations,
                                primaryjoin=id == combinations.c.flavor1_id,
                                secondaryjoin=id == combinations.c.flavor2_id,
                                )

    def as_dictionary(self):
        return {
            "id": self.id,
            "name": self.name,
            "combinations": self.combinations
        }