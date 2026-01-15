import unittest

import pydantic

from ... import _transformers


class TestIsDuckTypeOf(unittest.TestCase):

  class FakePydanticModel(pydantic.BaseModel):
    field1: str
    field2: int
    field3: str
    field4: str
    field5: str

  class FakePydanticModelWithLessFields(pydantic.BaseModel):
    field1: str
    field2: int
    field3: str
    field4: str

  def test_is_duck_type_of_true_for_pydantic_object(self):
    obj = self.FakePydanticModel(
        field1="a",
        field2=1,
        field3="b",
        field4="c",
        field5="d",
    )
    self.assertTrue(_transformers._is_duck_type_of(obj, self.FakePydanticModel))

  def test_is_duck_type_of_true_for_duck_typed_object(self):
    class DuckTypedObject:

      def __init__(self):
        self.field1 = "a"
        self.field2 = 1
        self.field3 = "b"
        self.field4 = "c"
        self.field5 = "d"

    obj = DuckTypedObject()
    self.assertTrue(_transformers._is_duck_type_of(obj, self.FakePydanticModel))

  def test_is_duck_type_of_false_for_different_many_fields(self):
    class DifferentFieldsObject:

      def __init__(self):
        self.fielda = "a"

    obj = DifferentFieldsObject()
    self.assertFalse(
        _transformers._is_duck_type_of(obj, self.FakePydanticModel)
    )

  def test_is_duck_type_of_false_for_missing_fields(self):

    obj = self.FakePydanticModelWithLessFields(
        field1="a", field2=1, field3="b", field4="c"
    )
    self.assertFalse(_transformers._is_duck_type_of(obj, self.FakePydanticModel))

  def test_is_duck_type_of_false_for_dict(self):
    obj = {"field1": "a", "field2": 1}
    self.assertFalse(
        _transformers._is_duck_type_of(obj, self.FakePydanticModel)
    )

  def test_is_duck_type_of_false_for_non_pydantic_class(self):
    class NonPydanticModel:
      pass

    class SomeObject:
      pass

    obj = SomeObject()
    self.assertFalse(_transformers._is_duck_type_of(obj, NonPydanticModel))

  def test_is_duck_type_of_true_with_extra_fields(self):
    class ExtraFieldsObject:

      def __init__(self):
        self.field1 = "a"
        self.field2 = 1
        self.field3 = "extra"
        self.field4 = "extra"
        self.field5 = "extra"
        self.field6 = "extra"

    obj = ExtraFieldsObject()
    self.assertTrue(_transformers._is_duck_type_of(obj, self.FakePydanticModel))


if __name__ == "__main__":
  unittest.main()
