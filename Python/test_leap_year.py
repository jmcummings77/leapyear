import pytest
from .leap_year import leap_year_modulos

@pytest.mark.parametrize("start,finish,expected", [(1582, 1582, [])])
def test_generate_defaults(self, start, finish, expected):
    """
    test cases:
        start
            not divisible by 4
                1582
            divisible by 4
                1584
            divisible by 4 and 100 but not 400
                1700
            divisible by 4 and 400
                1600
        finish
            not divisible by 4
                1582
            divisible by 4
                1584
            divisible by 4 and 100 but not 400
                1700
            divisible by 4 and 400
                1600
        start > finish?
        what if we give it a string instead of numbers?
        what if we give it floats instead of ints?


    :return:
    """
    # Arrange
    # parameterized

    # Act
    result = leap_year_modulos(start, finish)

    #Assert
    assert result == expected

