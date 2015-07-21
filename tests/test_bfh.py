from unittest import TestCase

import math

from bfh import Schema, Mapping
from bfh.fields import (
    ArrayField,
    IntegerField,
    NumberField,
    Subschema,
    UnicodeField
)
from bfh.transformations import (
    Const,
    Concat,
    Do,
    Get,
    Int,
    Str,
)


class Schema1(Schema):
    my_str = UnicodeField()
    my_int = IntegerField()
    another_str = UnicodeField()


class Schema2(Schema):
    peas = UnicodeField()
    carrots = IntegerField()
    beans = IntegerField()


class Person(Schema):
    first_name = UnicodeField()
    last_name = UnicodeField()


class Ship(Schema):
    name = UnicodeField()
    captain = Subschema(Person)


class Conversation(Schema):
    numbers = ArrayField(IntegerField())
    conversants = ArrayField(Subschema(Person))


class TestSchemas(TestCase):
    def test_can_make_empty_schema(self):
        s = Schema1()
        assert hasattr(s, 'my_str')
        assert hasattr(s, 'my_int')
        assert hasattr(s, 'another_str')
        assert s.my_str is None
        assert s.my_int is None
        assert s.another_str is None

    def test_can_assign_and_retrieve(self):
        s = Schema1()
        some_str = u'wow'
        some_int = 3
        another_str = u'ok'
        s.my_str = some_str
        s.my_int = some_int
        s.another_str = another_str
        assert s.my_str == some_str
        assert s.my_int == some_int
        assert s.another_str == another_str

    def test_can_initialize_names(self):
        some_str = u'woof'
        some_int = 9
        another_str = u'meow'
        s = Schema1(
            my_str=some_str,
            my_int=some_int,
            another_str=another_str
        )
        assert s.my_str == some_str
        assert s.my_int == some_int
        assert s.another_str == another_str

    def test_can_initialize_with_dict(self):
        my_dict = {
            "my_str": u"haha",
            "my_int": 1212,
            "another_str": "okok",
        }
        s = Schema1(my_dict)
        assert s.serialize() == my_dict

    def test_can_nest_subschema(self):
        s = Ship()
        shipname = "Titanic"
        firstname = "Edward"
        lastname = "Smith"
        s.name = shipname
        s.captain.first_name = firstname
        s.captain.last_name = lastname
        assert hasattr(s, 'name')
        assert hasattr(s, 'captain')
        assert s.name == shipname
        assert s.captain.first_name == firstname
        assert s.captain.last_name == lastname

    def test_can_initialize_subschema(self):
        shipname = "Lollipop"
        firstname = "James"
        lastname = "Dunn"
        s = Ship(
            name=shipname,
            captain={
                "first_name": firstname,
                "last_name": lastname
            }
        )
        assert s.name == shipname
        assert s.captain.first_name == firstname
        assert s.captain.last_name == lastname

    def test_can_init_subschemas_with_dict(self):
        my_ship = {
            "name": "Podunk",
            "captain": {
                "first_name": "Steamboat",
                "last_name": "Willie"
            }
        }
        s = Ship(my_ship)
        assert s.serialize() == my_ship

    def test_can_use_arrays(self):
        s = Conversation()
        s.numbers = [1, 2, 3]
        assert s.numbers[0] == 1

        firstname = "Marilyn"
        lastname = "Monroe"
        s.conversants = [Person(first_name=firstname, last_name=lastname)]
        assert s.conversants[0].first_name == firstname

    def test_can_initialize_array(self):
        numbers = [1, 2, 3]
        s = Conversation(
            numbers=[1, 2, 3],
            conversants=[
                Person(first_name="me", last_name="person"),
                Person(first_name="you", last_name="person")
            ])
        assert s.numbers == numbers
        assert s.conversants[0].first_name == 'me'

    def test_can_init_arrays_with_dict(self):
        my_convo = {
            "numbers": [1, 2, 3],
            "conversants": [
                {"first_name": "me", "last_name": "person"},
                {"first_name": "you", "last_name": "person"}
            ]
        }
        # TODO this is not going to validate the inner schema tho
        s = Conversation(my_convo)
        self.assertEqual(s.serialize(), my_convo)


class OneToTwoBase(Mapping):
    peas = Get('my_str')
    carrots = Get('my_int')
    beans = Int(Get('another_str'))


class OneToTwo(OneToTwoBase):
    source = Schema1
    target = Schema2


class TwoToOne(Mapping):
    source = Schema2
    target = Schema1

    my_str = Get('peas')
    my_int = Get('carrots')
    another_str = Str(Get('beans'))


class TestMappings(TestCase):
    def setUp(self):
        self.original = {
            "my_str": u"woof",
            "my_int": 99,
            "another_str": u"123"
        }

        self.expected = {
            "peas": u"woof",
            "carrots": 99,
            "beans": 123
        }

    def test_simple_mapping(self):
        transformed = OneToTwo().apply(self.original).serialize()
        self.assertEqual(self.expected, transformed)

        back_again = TwoToOne().apply(transformed).serialize()
        self.assertEqual(self.original, back_again)

    def test_dont_even_need_schemas(self):
        transformed = OneToTwoBase().apply(self.original).serialize()
        self.assertEqual(self.expected, transformed)

    def test_constants_in_mapping(self):
        class Consistent(Mapping):
            one = Const(1)
            two = Const("two")
            three = Const(3.0)

        source = {
            "one": "doesn't",
            "two": "matter",
            "three": "what's here",
            "four": "amirite"
        }

        transformed = Consistent().apply(source).serialize()
        self.assertEqual({
            "one": 1,
            "two": "two",
            "three": 3.0,
        }, transformed)


class TestInheritance(TestCase):
    """Verify that the metaprogramming tricks didn't go awry"""
    def test_schemas_can_inherit(self):
        class SchemaA(Schema):
            peas = IntegerField()

        class SchemaB(SchemaA):
            turnips = IntegerField()

        assert isinstance(SchemaB.peas, IntegerField)
        assert isinstance(SchemaB.turnips, IntegerField)

        s = SchemaB()
        assert hasattr(s, "peas")
        assert "peas" in s._fields
        assert hasattr(s, "turnips")
        assert "turnips" in s._fields

    def test_mappings_can_inherit(self):
        class SchemaA(Schema):
            beans = IntegerField()
            carrots = IntegerField()

        class SchemaB(Schema):
            legumes = IntegerField()
            root_veg = IntegerField()

        class MappingA(Mapping):
            source = SchemaA
            legumes = Get('beans')

        class MappingB(MappingA):
            target = SchemaB
            root_veg = Get('carrots')

        assert isinstance(MappingB.legumes, Get)
        assert isinstance(MappingB.root_veg, Get)
        assert MappingB.source is SchemaA
        assert MappingB.target is SchemaB

        m = MappingB()
        assert hasattr(m, "legumes")
        assert "legumes" in m._fields
        assert hasattr(m, "root_veg")
        assert "root_veg" in m._fields
        assert m.source is SchemaA
        assert m.target is SchemaB


class SquarePeg(Schema):
    id = IntegerField()
    name = UnicodeField()
    width = NumberField()


class RoundHole(Schema):
    id = UnicodeField()
    name = UnicodeField()
    diameter = NumberField()


def largest_square(width):
    return math.sqrt(2 * width**2)


class SquarePegToRoundHole(Mapping):
    source = SquarePeg
    target = RoundHole

    id = Concat('from_square', ':', Str(Get('id')))
    name = Get('name')
    diameter = Do(largest_square, Get('width'))


class TestReadmeExample(TestCase):
    def test_it_works(self):
        my_peg = SquarePeg(id=1, name="peggy", width=50)

        transformed = SquarePegToRoundHole().apply(my_peg).serialize()

        assert transformed['id'] == u'from_square:1'
        assert transformed['name'] == u'peggy'
        assert 70.71 < transformed['diameter'] < 70.72
