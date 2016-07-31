from sqlalchemy import Column, String, Integer, BigInteger, DateTime

from app import db


class User(db.Model):
    __tablename__ = "users"

    c_id = Column("id", Integer, primary_key=True)
    c_join = Column("join", DateTime)

    c_twi_id = Column("twi_id", BigInteger)
    c_twi_token = Column("twi_token", String(60))
    c_twi_secret = Column("twi_secret", String(120))

    c_wei_id = Column("wei_id", BigInteger)
    c_wei_token = Column("wei_token", String(60))
    c_wei_expire = Column("wei_expire", DateTime)

    def __repr__(self):
        return "<User: %s, join at %s>" % (self.c_username, str(self.c_join))

    @property
    def is_linked_to_twi(self):
        return self.c_twi_id is not None

    @property
    def is_linked_to_wei(self):
        return self.c_wei_id is not None

    def update_fields(self, fields, instant_save=True):
        for field, value in fields.items():
            setattr(self, field, value)
        if instant_save:
            db.session.commit()

    @staticmethod
    def merge_user(del_user, left_user, update_fields=None, by_join_order=False, instant_save=True):
        """ 合并两个 user， del_user 是合并后被删除的 user, left_user 是合并后保存的 user,
            update_fields 是手动更新的 fields， left_user 对应的 fields 会强制更新
            如果 by_join_order 为 True， 则不管传入的 user 顺序， 把加入时间靠后的用户删除
            这个函数的目的是为了简化以后可能会出现的比较复杂的用户合并情景
        """

        if by_join_order:
            del_user, left_user = sorted([del_user, left_user], key=lambda u: u.c_join, reverse=True)

        columns = [c for c in left_user.__dict__ if c.startswith('c_')]
        if update_fields is None:
            update_fields = dict()
        for column in columns:
            # 不在手动更新序列中， 并且 left_user 这个 filed 的 value 为空， 则使用 del_user 的 value
            if column not in update_fields and not getattr(left_user, column):
                if getattr(del_user, column):
                    setattr(left_user, column, getattr(del_user, column))

        left_user.update_fields(update_fields, False)

        if instant_save:
            db.session.delete(del_user)
            db.session.commit()
