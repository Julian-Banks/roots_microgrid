from solar_simulator import SolarSimulator
import unittest


class TestSolarSimulator(unittest.TestCase):

    def setUp(self):
        self.solar_simulator = SolarSimulator()

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
