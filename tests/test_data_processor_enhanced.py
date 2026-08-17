
import unittest

from data_processor_enhanced import EnhancedTSMDataProcessor

import pandas as pd

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

class GetPeerComparisonData(unittest.TestCase):
    def setUp(self):
        self.data_processor = EnhancedTSMDataProcessor()
        lcra_example_name = "Hilldale Housing Association Limited - LCRA"
        lcra_example_code = "4760"
        lcho_example_name = "Cross Keys Homes Limited - LCHO"
        lcho_example_code = "LH4428"
        combined_example_name = "North London Muslim Housing Association Limited - COMBINED"
        combined_example_code = "LH3859"
        self.code_dict = {"LCRA": lcra_example_code, "LCHO": lcho_example_code, "COMBINED": combined_example_code}
        self.name_dict = {"LCRA": lcra_example_name, "LCHO": lcho_example_name, "COMBINED": combined_example_name}

    def wrong_row_check(self, df: pd.DataFrame, column_name: str, expected_value = None):
        # Check for duplicates
        if expected_value == None:
            wrong_rows = df[df.duplicated(subset=[column_name], keep=False)]
            failure_msg = f"Returned DataFrame contains multiple entries for a single {column_name}."
        # Check all rows in column_name take a unique expected value
        else:
            wrong_rows = df[df[column_name] != expected_value]
            failure_msg = f"Expected all rows to have {column_name}={expected_value}, but found {len(wrong_rows)} incorrect rows:\n{wrong_rows}"
        self.assertEqual(len(wrong_rows), 0, failure_msg)
    
    def data_frame_assertations(self, df: pd.DataFrame, provider_code, provider_name, dataset_type):
        # Assert that the selected provider is contained in the returned df
        self.assertFalse(
            df[(df["provider_code"] == provider_code) & (df["provider_name"] == provider_name)].empty,    
            f"Selected provider not contained in DataFrame: no row with provider_code={provider_code} and provider_name={provider_name}."
        ) 
        # Assert all values in dataset_type column are correct
        self.wrong_row_check(df, "dataset_type", dataset_type)
        # Assert each provider is included only once
        self.wrong_row_check(df, "provider_code")

    # Each dataset type is tested for TP01, TP12, and a TP in between. For each, one test uses year 2024. This gives a variety of test cases.

    def build_test(self, dataset_type, tp_measure, year):
        df = self.data_processor.get_peer_comparison_data(self.code_dict[dataset_type], self.name_dict[dataset_type], tp_measure, year)
        self.data_frame_assertations(df, self.code_dict[dataset_type], self.name_dict[dataset_type], dataset_type)

    # LCRA tests
    def test_lcra_entry_tp01_2025(self):
        self.build_test("LCRA", "TP01", 2025)

    def test_lcra_entry_tp03_2025(self):
        self.build_test("LCRA", "TP03", 2025)

    def test_lcra_entry_tp12_2025(self):
        self.build_test("LCRA", "TP12", 2025)

    # LCHO tests
    def test_lcho_entry_tp01_2025(self):
        self.build_test("LCHO", "TP01", 2025)

    def test_lcho_entry_tp09_2025(self):
        self.build_test("LCHO", "TP09", 2025)

    def test_lcho_entry_tp12_2025(self):
        self.build_test("LCHO", "TP12", 2025)

    # COMBINED tests
    def test_combined_entry_tp01_2025(self):
        self.build_test("COMBINED", "TP01", 2025)

    def test_combined_entry_tp06_2025(self):
        self.build_test("COMBINED", "TP06", 2025)

    def test_combined_entry_tp12_2025(self):
        self.build_test("COMBINED", "TP12", 2025)
        


if __name__ == "__main__":
    unittest.main()
