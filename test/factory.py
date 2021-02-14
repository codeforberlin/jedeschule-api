import factory

from app.models import School


class SchoolFactory(factory.Factory):
    class Meta:
        model = School

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: 'School %d' % n)
    address = factory.Faker('address')