import unittest

from icgparser.ModelResourcesUtilities import ModelResources, from_model_resources_to_ir_names_version1, \
    ModelResourcesUtilities


class MyTestCase(unittest.TestCase):
    def test_ModelResources_returns_value_number(self):
        first_enum = ModelResources.STEP_NAME.value
        self.assertEqual(first_enum, 1)

    def test_ModelResources_returns_string_name(self):
        first_enum = ModelResources.STEP_NAME.name
        self.assertIsInstance(first_enum, str)

    def test_get_ir_key_name_from_model_resource_returns_doml_version_1_resourcename(self):
        ir_key = from_model_resources_to_ir_names_version1(ModelResources.STEPS)
        self.assertIsNotNone(ir_key)

    def test_convert_doml_version_into_integer_returns_float(self):
        doml_version = "1.0"
        model_resources = ModelResourcesUtilities(doml_version)
        self.assertEqual(model_resources.convert_doml_version_into_integer(), 1)


if __name__ == '__main__':
    unittest.main()
