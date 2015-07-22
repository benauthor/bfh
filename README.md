# BFH

![bfh](http://timberframe-postandbeamhomes.com/media/uploads/galleries/trusses/naked_trusses/iain_with_beatle_hammer.jpg)

Put square pegs in round holes.

```python
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
    source_schema = SquarePeg
    target_schema = RoundHole

    id = Concat('from_square', ':', Str(Get('id')))
    name = Get('name')
    diameter = Do(largest_square, Get('width'))

my_peg = SquarePeg(id=1, name="peggy", width=50)

transformed = SquarePegToRoundHole().apply(my_peg).serialize()
transformed['id']
# u'from_square:1'
transformed['name']
# u'peggy'
transformed['diameter']
# 70.71067811865476
```

BFH is a library for mapping schemas to other schemas. The use of explicit schema objects is *totally optional*... a mapping can be used without input and output schemas. Viz.

```python

class ImpliesSchemas(Mapping):
    id = Concat('author', ':', Get('nom_de_plume'))
    name = Get('nom_de_plume')
    book = Get('best_known_for')

source = {
    "nom_de_plume": "Mark Twain",
    "best_known_for": "Huckleberry Finn"
}
output = ImpliesSchemas().apply(source)

type(output)
# <class 'bfh.GenericSchema'>
output.serialize().keys()
# ['book', 'id', 'name']

```

Explicit schemas, however, can help preserve your sanity when things get complex.


## Validation

It's not really a validation library, OK? There are lots of those out there, so we don't get too fancy here. Just some sanity checking.


## Build Status

[![Build Status](https://travis-ci.org/benauthor/bfh.svg?branch=master)](https://travis-ci.org/benauthor/bfh)

Curretly failing on Py3k ...
