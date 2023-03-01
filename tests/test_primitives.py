from _pytest.python_api import raises

from tempren.primitives import CategoryName, TagName


class TestTagName:
    @property
    def _name_instance(self):
        return TagName

    def test_empty(self):
        with raises(ValueError):
            self._name_instance("")

    def test_invalid(self):
        with raises(ValueError):
            self._name_instance("Foo-Bar")

    def test_number_start(self):
        with raises(ValueError):
            self._name_instance("3D")


class TestCategoryName(TestTagName):
    @property
    def _name_instance(self):
        return CategoryName
