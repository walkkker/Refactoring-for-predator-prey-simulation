import unittest
import numpy as np

from predator_prey import simulate_predator_prey

class SimulateTest(unittest.TestCase):

    def test_landscape_generator(self):
        width, height, width_halo, height_halo, landscape = landscape_generator("map.dat")
        expected_landscape[0] = expected_landscape[21] = np.zeros(12, int)
        for i in range(1, 21):
            expected_landscape[i] = [0] + np.ones(10, int) + [0]
        assertListEqual(expected_landscape, landscape, msg="Landscape returned was unexpected")
        





    def test_get_nucleotides(self):
        sequence_str = "GATTACCA"
        sequence = Sequence(sequence_str)
        self.assertEqual(sequence_str, sequence.nucleotides,
                         msg="Nucleotides returned were not those given")

    def test_get_weight(self):
        sequence = Sequence("G")
        self.assertAlmostEqual(Sequence.WEIGHTS['G'],
                               sequence.get_weight(),
                               delta=0.01,
                               msg="Weight returned was unexpected")

    def test_calculate_weight(self):
        sequence = Sequence("G")
        self.assertAlmostEqual(Sequence.WEIGHTS['G'],
                               Sequence.calculate_weight(sequence),
                               delta=0.01,
                               msg="Weight returned was unexpected")