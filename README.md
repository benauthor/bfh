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
    source = SquarePeg
    target = RoundHole

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
