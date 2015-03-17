__author__ = 'kristjin@github'

from flask import url_for

from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship, backref

from .database import Base


combinations = Table("combinations", Base.metadata,
                     Column("flavor_id", Integer, ForeignKey("flavors.id")),
                     Column("combo_id", Integer, ForeignKey("flavors.id"))
                     )


class Flavor(Base):
    __tablename__ = "flavors"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    combinations = relationship("Flavor",
                                secondary=combinations,
                                primaryjoin=(combinations.c.flavor_id == id),
                                secondaryjoin=(combinations.c.combo_id == id),
                                backref=backref('combinations')
                                )

    def as_dictionary(self):
        return {
            "id": self.id,
            "name": self.name,
            "combinations": self.combinations
        }