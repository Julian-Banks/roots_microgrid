from sim.grid import Grid
import unittest


class TestGrid(unittest.TestCase):

    def setUp(self):
        self.grid = Grid()

    def tearDown(self):
        pass

    def test_purchase_energy(self):
        '''Test
        self.grid_feed_in_simulator.set_timestep(0)

        purchased_energy, cost = self.grid_feed_in_simulator.purchase_energy(
            100
        )

        self.assertEqual(purchased_energy)
        self.assertEqual(cost)
        '''
        pass

    def test_calculate_cost(self):
        '''
        cost = self.grid_feed_in_simulator.calculate_cost(100)
        self.assertEqual(
            cost,
        )
        '''


if __name__ == "__main__":
    unittest.main()
