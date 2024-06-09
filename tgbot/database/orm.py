from typing import Generic, List, Type, TypeVar
from sqlalchemy import desc, select, update, delete
from sqlalchemy.orm import selectinload, sessionmaker
from sqlalchemy.exc import NoResultFound
from tgbot.database.database import Base

from .models import User, Notification, TimeZone

T = TypeVar("T", bound=Base)


class CRUD(Generic[T]):
    def __init__(self, model: Type[T], session_factory: sessionmaker):
        self.model = model
        self.session_factory = session_factory

    async def create(self, **kwargs) -> T:
        async with self.session_factory() as session:
            obj = self.model(**kwargs)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def get(self, id: int) -> T | None:
        async with self.session_factory() as session:
            query = select(self.model).filter_by(id=id)
            result = await session.execute(query)
            try:
                return result.scalars().one()
            except NoResultFound:
                return None

    async def get_all(self, **kwargs) -> List[T]:
        async with self.session_factory() as session:
            query = select(self.model).filter_by(**kwargs).order_by(desc(self.model.id))
            result = await session.execute(query)
            users = result.scalars().all()
            return users

    async def update(self, id: int, **kwargs) -> T | None:
        async with self.session_factory() as session:
            query = select(self.model).filter_by(id=id)
            result = await session.execute(query)
            try:
                obj = result.scalars().one()
                for key, value in kwargs.items():
                    setattr(obj, key, value)

                await session.commit()
                await session.refresh(obj)
                return obj
            except NoResultFound:
                return None

    async def delete(self, id: int) -> bool:
        async with self.session_factory() as session:
            query = select(self.model).filter_by(id=id)
            result = await session.execute(query)
            try:
                obj = result.scalars().one()
                await session.delete(obj)
                await session.commit()
                return True
            except NoResultFound:
                return False


class NotificationsRepo(CRUD[Notification]):

    def __init__(self, session):
        super().__init__(Notification, session)

    async def get_filter_by(self, **kwargs):
        async with self.session_factory() as session:
            query = select(self.model).filter_by(**kwargs)
            result = await session.execute(query)
            try:
                return result.scalars().all()
            except NoResultFound:
                return []


class AsyncORM:

    session_factory: sessionmaker

    # models
    users: CRUD[User]
    notifications: NotificationsRepo
    time_zones: CRUD[TimeZone]

    @classmethod
    def set_session_factory(cls, session_factory):
        cls.session_factory = session_factory

    @classmethod
    def init_models(cls):
        cls.users = CRUD(User, cls.session_factory)
        cls.notifications = NotificationsRepo(cls.session_factory)
        cls.time_zones = CRUD(TimeZone, cls.session_factory)

    @classmethod
    async def create_withdrawal_request(cls, requisites: str, user: User):
        async with cls.session_factory() as session:
            obj = WithdrawRequest(
                requisites=requisites, user_id=user.id, amount=user.balance
            )
            session.add(obj)
            update_user_stmt = update(User).values(balance=0).filter_by(id=user.id)
            await session.execute(update_user_stmt)
            await session.commit()
            await session.refresh(obj)
            return obj
