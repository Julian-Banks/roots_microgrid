from microgrid.solar import Solar
import unittest


class TestSolarSimulator(unittest.TestCase):

    def setUp(self):
        self.solar = Solar()

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
