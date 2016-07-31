from . import TestBase, db
from app.models.main import User
from datetime import datetime, timedelta


class TestUserModel(TestBase):
    def test_01_create_user(self):
        """ 测试创建用户"""
        user = User()
        user.c_join = datetime.utcnow()
        db.session.add(user)
        db.session.commit()

        u = db.session.query(User).first()
        self.assertTrue(u is not None)

    def test_02_merge_user(self):
        """ 测试合并用户 """
        user1 = User(
            c_join=datetime.utcnow(),
            c_twi_id=12345,
            c_twi_token='abcde',
            c_twi_secret='aabbccddee',
        )

        user2 = User(
            c_join=datetime.utcnow(),
            c_wei_id=67890,
            c_wei_token='ABCDE',
            c_wei_expire=datetime.utcnow() + timedelta(1000),
        )

        db.session.add_all([user1, user2])
        db.session.commit()
        u1_id = user1.c_id
        u1_join = user1.c_join
        User.merge_user(user1, user2, by_join_order=True)
        users = db.session.query(User).all()
        user = users[0]
        self.assertTrue(len(users) == 1 and
                        user.c_id == u1_id and
                        user.c_join == u1_join and
                        user.c_twi_id == 12345 and
                        user.c_wei_id == 67890)

    def test_03_merge_and_update_user(self):
        """ 测试合并用户和更新用户信息"""
        user1 = User(
            c_join=datetime.utcnow(),
            c_twi_id=12345,
            c_twi_token='abcde',
            c_twi_secret='aabbccddee',
        )

        user2 = User(
            c_join=datetime.utcnow(),
            c_wei_id=67890,
            c_wei_token='ABCDE',
            c_wei_expire=datetime.utcnow() + timedelta(1000),
        )

        db.session.add_all([user1, user2])
        db.session.commit()
        u1_id = user1.c_id
        u1_join = user1.c_join
        User.merge_user(user1, user2, update_fields={'c_twi_id': 54321, 'c_wei_id': 9876}, by_join_order=True)
        users = db.session.query(User).all()
        user = users[0]
        self.assertTrue(len(users) == 1 and
                        user.c_id == u1_id and
                        user.c_join == u1_join and
                        user.c_twi_id == 54321 and
                        user.c_wei_id == 9876)
