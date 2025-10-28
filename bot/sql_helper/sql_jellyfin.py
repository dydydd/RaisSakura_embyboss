"""
Jellyfin的SQL操作
与Emby的SQL操作完全独立
"""
from bot.sql_helper import Base, Session, engine
from sqlalchemy import Column, BigInteger, String, DateTime, Integer, case
from sqlalchemy import func
from sqlalchemy import or_
from bot import LOGGER


class Jellyfin(Base):
    """
    jellyfin表，tg主键，默认值lv，us，iv
    """
    __tablename__ = 'jellyfin'
    tg = Column(BigInteger, primary_key=True, autoincrement=False)
    jellyfinid = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    pwd = Column(String(255), nullable=True)
    pwd2 = Column(String(255), nullable=True)
    lv = Column(String(1), default='d')
    cr = Column(DateTime, nullable=True)
    ex = Column(DateTime, nullable=True)
    us = Column(Integer, default=0)
    iv = Column(Integer, default=0)
    ch = Column(DateTime, nullable=True)


Jellyfin.__table__.create(bind=engine, checkfirst=True)


def sql_add_jellyfin(tg: int):
    """
    添加一条jellyfin记录，如果tg已存在则忽略
    """
    with Session() as session:
        try:
            jellyfin = Jellyfin(tg=tg)
            session.add(jellyfin)
            session.commit()
        except:
            pass


def sql_delete_jellyfin(tg=None, jellyfinid=None, name=None):
    """
    根据tg, jellyfinid或name删除一条jellyfin记录
    """
    with Session() as session:
        try:
            condition = or_(Jellyfin.tg == tg, Jellyfin.jellyfinid == jellyfinid, Jellyfin.name == name)
            jellyfin = session.query(Jellyfin).filter(condition).with_for_update().first()
            if jellyfin:
                session.delete(jellyfin)
                session.commit()
                return True
            else:
                return None
        except:
            return False


def sql_update_jellyfins(some_list: list, method=None):
    """根据list中的tg值批量更新一些值，此方法不可更新主键"""
    with Session() as session:
        if method == 'iv':
            try:
                mappings = [{"tg": c[0], "iv": c[1]} for c in some_list]
                session.bulk_update_mappings(Jellyfin, mappings)
                session.commit()
                return True
            except:
                session.rollback()
                return False
        if method == 'ex':
            try:
                mappings = [{"tg": c[0], "ex": c[1]} for c in some_list]
                session.bulk_update_mappings(Jellyfin, mappings)
                session.commit()
                return True
            except:
                session.rollback()
                return False
        if method == 'bind':
            try:
                mappings = [{"tg": c[0], "name": c[1], "jellyfinid": c[2]} for c in some_list]
                session.bulk_update_mappings(Jellyfin, mappings)
                session.commit()
                return True
            except Exception as e:
                print(e)
                session.rollback()
                return False


def sql_get_jellyfin(tg):
    """
    查询一条jellyfin记录，可以根据tg, jellyfinid或者name来查询
    """
    with Session() as session:
        try:
            jellyfin = session.query(Jellyfin).filter(or_(Jellyfin.tg == tg, Jellyfin.name == tg, Jellyfin.jellyfinid == tg)).first()
            return jellyfin
        except:
            return None


def get_all_jellyfin(condition):
    """
    查询所有jellyfin记录
    """
    with Session() as session:
        try:
            jellyfins = session.query(Jellyfin).filter(condition).all()
            return jellyfins
        except:
            return None


def sql_update_jellyfin(condition, **kwargs):
    """
    更新一条jellyfin记录，根据condition来匹配，然后更新其他的字段
    """
    with Session() as session:
        try:
            jellyfin = session.query(Jellyfin).filter(condition).first()
            if jellyfin is None:
                return False
            for k, v in kwargs.items():
                setattr(jellyfin, k, v)
            session.commit()
            return True
        except Exception as e:
            LOGGER.error(e)
            return False


def sql_count_jellyfin():
    """
    检索有tg和jellyfinid的jellyfin记录的数量，以及Jellyfin.lv =='a'条件下的数量
    :return: int, int, int
    """
    with Session() as session:
        try:
            count = session.query(
                func.count(Jellyfin.tg).label("tg_count"),
                func.count(Jellyfin.jellyfinid).label("jellyfinid_count"),
                func.count(case((Jellyfin.lv == "a", 1))).label("lv_a_count")
            ).first()
        except Exception as e:
            return None, None, None
        else:
            return count.tg_count, count.jellyfinid_count, count.lv_a_count