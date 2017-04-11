from sqlalchemy import schema, types

metadata = schema.MetaData()

projects = schema.Table('projects', metadata,
    schema.Column('id', types.Integer, primary_key=True, unique=True),
    schema.Column('num', types.Integer(), default=0),
    schema.Column('loc', types.Text(), default=u''),
    schema.Column('geo', types.Text(), default=u''),
)

updates = schema.Table('updates', metadata,
    schema.Column('id', types.Integer),
    schema.Column('date', types.Integer(), default=0),
    schema.Column('update', types.Text(), default=u''),
)

from sqlalchemy.engine import create_engine

db = create_engine('sqlite:///water_alert.db', echo=False)
metadata.bind = db

metadata.create_all(checkfirst=True)