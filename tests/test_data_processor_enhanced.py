
import unittest

from data_processor_enhanced import EnhancedTSMDataProcessor


class GetProviderDatasetTypeTests(unittest.TestCase):
    def setUp(self):
        self.data_processor = EnhancedTSMDataProcessor()

    def test_get_lcra_dataset_type(self):
        lcra_example_name = "Hilldale Housing Association Limited - LCRA"
        lcra_example_code = "4760"
        self.assertEqual(self.data_processor.get_provider_dataset_type(lcra_example_code, lcra_example_name), "LCRA", "Failed to fetch provider type for LCRA provider")

    def test_get_lcro_data_type(self):
        lcho_example_name = "Cross Keys Homes Limited - LCHO"
        lcho_example_code = "LH4428"
        self.assertEqual(self.data_processor.get_provider_dataset_type(lcho_example_code, lcho_example_name), "LCHO", "Failed to fetch provider type for LCHO provider")

    def test_get_combined_dataset_type(self):
        combined_example_name = "North London Muslim Housing Association Limited - COMBINED"
        combined_example_code = "LH3859"
        self.assertEqual(self.data_processor.get_provider_dataset_type(combined_example_code, combined_example_name), "COMBINED", "Failed to fetch provider type for Combined provider")

if __name__ == "__main__":
    unittest.main()
