from typing import Generator
from microgrid.generator import Generator
import unittest


class TestGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = Generator(
            capacity=500, cost_diesel=20, litre_diesel_per_kWh=0.3
        )

    def tearDown(self):
        del self.generator

    def test_run_generators(self):

        time_interval: float = 1
        requested_power: float = 250

        # Expected cost is kWh*hour*cost/litre*litre/(hour*kWh)
        expected_cost: float = 250 * 1 * 20 * 0.3

        generated_power, cost = self.generator.run_generators(
            requested_power, time_interval
        )

        self.assertEqual(
            expected_cost,
            cost,
            'The expected cost of running the diesel generator was not equal to the actual cost',
        )
        self.assertEqual(
            generated_power,
            requested_power,
            'The generated power was not equal to the requested_power',
        )

    def test_max_capacity(self):

        time_interval: float = 1
        requested_power: float = 600

        # Expected cost is kWh*hour*cost/litre*litre/(hour*kWh)
        expected_cost: float = 500 * 1 * 20 * 0.3

        generated_power, cost = self.generator.run_generators(
            requested_power, time_interval
        )

        self.assertEqual(
            expected_cost,
            cost,
            'The expected cost of running the diesel generator was not equal to the actual cost',
        )
        self.assertEqual(
            generated_power,
            500,
            'The generated power was not equal to the max capacity as expected.',
        )
