from app import *

db.drop_all()
db.create_all()

parente = User('parente')
foo = User('foo')
bar = User('bar')

db.session.add(parente)
db.session.add(foo)
db.session.add(bar)
db.session.commit()

f1 = Flock(name='Jupyter and Drinks',
    description="Let's chat about all things Jupyter",
    where='By the front door',
    when='7 pm',
    leader=parente)

f2 = Flock(name='the life of scipy',
    description="Where are we going next?",
    where='By the front bar',
    when='7 pm',
    leader=foo)

db.session.add(f1)
db.session.add(f2)
db.session.commit()

f1.birds.append(bar)
f1.birds.append(parente)
f2.birds.append(bar)
db.session.commit()
