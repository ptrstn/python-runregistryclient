import unittest

from runregistry.tracker.utilities import transform_lowstat_to_boolean


class TestTrackerUtilities(unittest.TestCase):
    def test_transform_lowstat_to_boolean(self):
        run_dict = {
            "pixel_lowstat": "LOW_STATS",
            "sistrip_lowstat": "Bla",
            "tracking_lowstat": "LOW_STATS",
        }

        transform_lowstat_to_boolean([run_dict])

        self.assertTrue(run_dict["pixel_lowstat"])
        self.assertFalse(run_dict["sistrip_lowstat"])
        self.assertTrue(run_dict["tracking_lowstat"])

        run_dict = {
            "pixel_lowstat": 123,
            "sistrip_lowstat": "LOW_STATS",
            "tracking_lowstat": None,
        }

        transform_lowstat_to_boolean([run_dict])

        self.assertFalse(run_dict["pixel_lowstat"])
        self.assertTrue(run_dict["sistrip_lowstat"])
        self.assertFalse(run_dict["tracking_lowstat"])
