__author__ = 'kristjin@github'

import json
from flask.ext.login import UserMixin

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .database import Base, session


class Flavor(Base):
    __tablename__ = "flavors"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    creator_id = Column(Integer, ForeignKey('users.id'))
    matches = relationship("Match", backref="parent")

    def get_default_mids(self):
        """ Return a list of all ids default matched to this flavor """
        rows = session.query(Match.matched_id)\
                       .order_by(Match.matched_id)\
                       .filter(Match.owner_id == 0,
                               Match.parent_id == self.id).all()
        dmids = [row[0] for row in rows]
        print "get_default_mids says {}".format(dmids)
        return dmids

    def get_user_mids(self, uid):
        """ Return a list of all ids uid has matched to this flavor """
        print "get_user_mids received {} for the uid.".format(uid)
        rows = session.query(Match.matched_id)\
                       .order_by(Match.matched_id)\
                       .filter(Match.owner_id == uid,
                               Match.parent_id == self.id).all()
        umids = [row[0] for row in rows]
        print "get_user_mids says {}".format(umids)
        return umids

    def get_all_mids(self, uid):
        """ Return a list of all ids (user and defaults) matched to this flavor """
        default_set = set(self.get_default_mids())
        user_set = set(self.get_user_mids(uid))
        return sorted((set(default_set | user_set)))

    def get_unmids(self, uid):
        """ Return a list of all ids NOT matched to this flavor """
        fids = set(row[0] for row in session.query(Flavor.id).all())
        mids = set(self.get_all_mids(uid))
        unmids = sorted(set(fids - mids))
        print "get_unmids says {}".format(unmids)
        unmids.remove(self.id)
        return unmids

    def get_default_mobs(self):
        """ Return a list of all objects default matched to flavor """
        mobs = []
        for mid in self.get_default_mids():
            mobs.append(session.query(Flavor).get(mid))
        return sorted(mobs)

    def get_user_mobs(self, uid):
        """ Return a list of all obj's uid has matched to this flavor """
        mobs = []
        for mid in self.get_user_mids(uid):
            mobs.append(session.query(Flavor).get(mid))
        return sorted(mobs)

    def get_all_mobs(self, uid):
        """ Return a list of all obj's (user and defaults) matched to this flavor """
        d = set(self.get_default_mobs())
        u = set(self.get_user_mobs(uid))
        return sorted(set(d | u))

    def get_unmobs(self, uid):
        """ Return a list of all obj's NOT matched to this flavor """
        unmids = self.get_unmids(uid)
        unmobs = []
        for unmid in unmids:
            unmob = session.query(Flavor).get(unmid)
            unmobs.append(unmob)
        return unmobs


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer,  nullable=True)
    parent_id = Column(Integer, ForeignKey('flavors.id'), nullable=False)
    matched_id = Column(Integer, nullable=False)


class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    admin = Column(Boolean())
    name = Column(String(128))
    email = Column(String(128), unique=True)
    password = Column(String(128))
    flavors = relationship("Flavor", backref="creator")
