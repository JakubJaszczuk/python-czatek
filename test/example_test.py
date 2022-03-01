import pytest


def test_example_1():
    assert 2 == 1 + 1


def test_example_2():
    with pytest.raises(ZeroDivisionError):
        1 / 0


@pytest.mark.parametrize('a, b, c', [(1, 2, 3), (0, 0, 0), (-1, 1, 0)])
def test_add(a, b, c):
    assert a + b == c


@pytest.fixture(scope='class')
def setup():
    return [1, 2]


class TestScopes1:

    def test_1(self, setup):
        setup.append(3)
        assert setup == [1, 2, 3]

    def test_2(self, setup):
        setup[1] = 8
        assert setup == [1, 8, 3]


class TestScopes2:

    def test_1(self, setup):
        setup.extend(range(1, 3))
        assert setup == [1, 2, 1, 2]

    def test_2(self, setup):
        del setup[1:]
        assert setup == [1]


class Owo:
    def __init__(self):
        self.x = 1


@pytest.fixture(scope='class')
def set_and_tear():
    x = 1
    yield x
    del x


class TestSetupTeardown:

    def test_1(self, set_and_tear):
        print(f'Enter first -> {set_and_tear}')
        x = set_and_tear
        x += 1
        assert x == 2

    def test_2(self, set_and_tear):
        print(f'Enter second -> {set_and_tear}')
        x = set_and_tear
        assert x == 1
