from load_simulator import LoadSimulator
import unittest


class TestLoadSimulator(unittest.TestCase):

    def setUp(self):
        self.load_simulator = LoadSimulator()

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
