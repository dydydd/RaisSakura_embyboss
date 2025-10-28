from bot.sql_helper import Base, Session, engine
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy import or_


class Jellyfin2(Base):
    """
    jellyfin2表，用于非TG用户的jellyfin账户管理
    """
    __tablename__ = 'jellyfin2'
    jellyfinid = Column(String(255), primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=True)
    pwd = Column(String(255), nullable=True)
    pwd2 = Column(String(255), nullable=True)
    lv = Column(String(1), default='d')
    cr = Column(DateTime, nullable=True)
    ex = Column(DateTime, nullable=True)
    expired = Column(Integer, nullable=True)


Jellyfin2.__table__.create(bind=engine, checkfirst=True)


def sql_add_jellyfin2(jellyfinid, name, cr, ex, pwd='5210', pwd2='1234', lv='b', expired=0):
    """
    添加一条jellyfin2记录
    """
    with Session() as session:
        try:
            jellyfin = Jellyfin2(jellyfinid=jellyfinid, name=name, pwd=pwd, pwd2=pwd2, lv=lv, cr=cr, ex=ex, expired=expired)
            session.add(jellyfin)
            session.commit()
        except:
            pass


def sql_get_jellyfin2(name):
    """
    查询一条jellyfin2记录，可以根据jellyfinid或者name来查询
    """
    with Session() as session:
        try:
            jellyfin = session.query(Jellyfin2).filter(or_(Jellyfin2.name == name, Jellyfin2.jellyfinid == name)).first()
            return jellyfin
        except:
            return None


def get_all_jellyfin2(condition):
    """
    查询所有jellyfin2记录
    """
    with Session() as session:
        try:
            jellyfins = session.query(Jellyfin2).filter(condition).all()
            return jellyfins
        except:
            return None


def sql_update_jellyfin2(condition, **kwargs):
    """
    更新一条jellyfin2记录，根据condition来匹配，然后更新其他的字段
    """
    with Session() as session:
        try:
            jellyfin = session.query(Jellyfin2).filter(condition).first()
            if jellyfin is None:
                return False
            for k, v in kwargs.items():
                setattr(jellyfin, k, v)
            session.commit()
            return True
        except:
            return False


def sql_delete_jellyfin2(jellyfinid):
    """
    根据jellyfinid删除一条jellyfin2记录
    """
    with Session() as session:
        try:
            jellyfin = session.query(Jellyfin2).filter_by(jellyfinid=jellyfinid).first()
            if jellyfin:
                session.delete(jellyfin)
                try:
                    session.commit()
                    return True
                except Exception as e:
                    print(e)
                    session.rollback()
                    return False
            else:
                return None
        except Exception as e:
            print(e)
            return False