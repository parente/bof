import sys
sys.path.append('./')
from app import *

db.drop_all()
db.create_all()

nobody = User('nobody')
foobar = User('foobar')
parente = User('parente')

db.session.add(nobody)
db.session.add(parente)
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
    leader=nobody)

db.session.add(f1)
db.session.add(f2)
db.session.commit()

f1.birds.append(foobar)
f1.birds.append(nobody)
f2.birds.append(foobar)
db.session.commit()
