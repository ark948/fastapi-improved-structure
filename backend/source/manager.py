import datetime

from sqlalchemy import desc, or_
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound

from source.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from src.config import SessionLocal


class BaseManager:
    __session = None

    def __init__(self, model):
        self.model = model

    @staticmethod
    def db():
        if BaseManager.__session is None or not BaseManager.__session.is_active:
            BaseManager.__session = SessionLocal()

        return BaseManager.__session

    def persist_db(self, query=None):
        self.db.close()
        return query

    @classmethod
    def rollback(cls):
        cls.db().rollback()

    def save(self, model_object):
        session = self.__class__.db()
        try:
            session.add(model_object)
            session.commit()
            session.refresh(model_object)
            return model_object
        except (IntegrityError, Exception) as e:
            session.rollback()
            raise e

    def query(self):
        return self.__class__.db().query(self.model)

    def get_searchset(self, search_kwargs: dict):
        return [
                getattr(self.model, key).icontains(value, autoescape=True) for key, value in search_kwargs.items()
            ]

    def filter_by(self, **kwargs):
        return self.query().filter_by(**kwargs).order_by(desc(self.model.created))

    def filter_query(self, search_kwargs: dict = None, **kwargs):
        date_from = kwargs.pop('date_from', None)
        date_to = kwargs.pop('date_to', None)
        query = self.query().filter_by(**kwargs).order_by(desc(self.model.created))
        if search_kwargs:
            search_query = self.get_searchset(search_kwargs)
            query = query.filter(or_(*search_query))

        if date_from and date_to:
            if not isinstance(date_to, datetime.datetime):
                date_to += datetime.timedelta(days=1)
            try:
                return query.filter(self.model.created.between(date_from, date_to))
            except KeyError:
                return query

        return query

    def filter(self, **kwargs):
        return self.filter_by(**kwargs).all()

    def filter_exists(self, **kwargs):
        return bool(self.filter_by(**kwargs).all())

    def create(self, **data):
        model_object = self.model(**data)
        return self.save(model_object)

    def bulk_create(self, objs):
        session = self.__class__.db()
        try:
            session.bulk_save_objects(objs)
            session.commit()
            return
        except Exception as e:
            session.rollback()
            raise e

    def all(self):
        return self.filter_query().all()

    def count(self):
        return self.filter_query().count()

    def get(self, **kwargs):
        try:
            return self.filter_by(**kwargs).one()
        except MultipleResultsFound as e:
            self.__class__.db().rollback()
            raise MultipleObjectsReturned(str(e))

        except NoResultFound as e:
            self.__class__.db().rollback()
            raise ObjectDoesNotExist("Object matching query not found")

        except Exception as e:
            self.__class__.db().rollback()
            raise e

    def get_or_create(self, defaults: dict = {}, **kwargs):
        try:
            return self.get(**kwargs), False
        except ObjectDoesNotExist:
            data = {**kwargs, **defaults}
            return self.create(**data), True

    def get_multi(self, query=None, skip: int = 0, limit: int = 10):
        try:
            if query:
                return query.offset(skip).limit(limit).all()
            return self.query().offset(skip).limit(limit).all()

        except Exception as e:
            self.__class__.db().rollback()
            raise e

    def update(self, data: dict, actor_id: int = None, **kwargs):
        db_object = self.get(**kwargs)
        if db_object:
            # to update many-to-many relationship
            if "related_objects" in data:
                related_object: dict = data.pop("related_objects")

                for relationship_name, related_objects in related_object.items():
                    getattr(db_object, relationship_name).clear()
                    # Update the many-to-many relationship
                    setattr(db_object, relationship_name, related_objects)

            for key, value in data.items():
                setattr(db_object, key, value)

            return self.save(db_object, actor_id=actor_id)

    def delete(self, **kwargs):
        db_obj = self.get(**kwargs)
        setattr(db_obj, "is_deleted", True)
        return self.save(db_obj)