__author__ = 'kristjin@github'

from flask import url_for
from flask.ext.login import UserMixin

from sqlalchemy import Column, Integer, String, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship

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
    creator_id = Column(Integer, ForeignKey('users.id'))

    def matched_html(self):
        h = "<ul>\n"
        for m in self.matches:
            h += '  <li display="inline">{}</li>\n'.format(m.name)
        h += "</ul>"
        return h

    def matched_ids(self):
        if self.matches:
            return [m.id for m in self.matches]
        else:
            return []

    def as_dictionary(self):
        return {
            "id": self.id,
            "name": self.name,
            "match_ids": [m.id for m in self.matches]
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
        return flavor.id in self.matched_ids()



class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    admin = Column(Boolean())
    name = Column(String(128))
    email = Column(String(128), unique=True)
    password = Column(String(128))
    flavors = relationship("Flavor", backref="creator")
    # Following should be JSON strings of personal matches
    # and strings of ints for favorites
    favorites = Column(String())
    matches = Column(String())