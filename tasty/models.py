__author__ = 'kristjin@github'

from flask import url_for

from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship, backref

from .database import Base


flavor_to_flavor = Table("flavor_to_flavor", Base.metadata,
                         Column("parent_flavor_id", Integer, ForeignKey("flavors.id"), primary_key=True),
                         Column("child_flavor_id", Integer, ForeignKey("flavors.id"), primary_key=True)
                         )


class Flavor(Base):
    __tablename__ = "flavors"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    matches = relationship("Flavor",
                           secondary=flavor_to_flavor,
                           primaryjoin=id == flavor_to_flavor.c.parent_flavor_id,
                           secondaryjoin=id == flavor_to_flavor.c.child_flavor_id,
                           backref='flavor'
                           )

    def as_dictionary(self):
        return {
            "id": self.id,
            "name": self.name,
            "matches": [m.id for m in self.matches]
        }

    def match(self, flavor):
        if not self.is_matched(flavor):
            self.matches.append(flavor)
            return self

    def unmatch(self, flavor):
        if self.is_matched(flavor):
            self.matches.remove(flavor)
            return self

    def is_matched(self, flavor):
        print self.matches
        return