from sim.load import Load
import unittest


class TestLoad(unittest.TestCase):

    def setUp(self):
        self.load = Load()

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
