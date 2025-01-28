import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from pytest_postgresql import factories

from source.services.database import Base






def load_database(**kwargs):
    kwargs['user'] = 'arman'
    kwargs['host'] = 'localhost'
    kwargs['port'] = 5434
    kwargs['dbname'] = 'test02'
    connection = f"postgresql+psycopg2://{kwargs['user']}:@{kwargs['host']}:5434/{kwargs['dbname']}"
    engine = create_engine(connection)
    Base.metadata.create_all(engine)
    session = scoped_session(sessionmaker(bind=engine))
    # add things to session
    session.commit()

postgresql_proc = factories.postgresql_proc(load=[load_database])

postgresql = factories.postgresql('postgresql_proc') # still need to check if this is actually needed or not

@pytest.fixture
def dbsession(postgresql):
    connection = f'postgresql+psycopg2://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}'
    engine = create_engine(connection)

    session = scoped_session(sessionmaker(bind=engine))

    yield session
    # 'Base.metadata.drop_all(engine)' here specifically does not work. It is also not needed. If you leave out the session.close()
    # all the tests still run, but you get a warning/error at the end of the tests.
    session.close()