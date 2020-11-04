import unittest
import numpy as np

from predator_prey import simulate_predator_prey



class SimulateTest(unittest.TestCase):

    def test_landscape_generator(self):
        width, height, width_halo, height_halo, landscape = simulate_predator_prey.landscape_generator("map.dat")
        expected_landscape = np.zeros((22,12), int)
        for i in range(1, 21):
            expected_landscape[i] = [0,1,1,1,1,1,1,1,1,1,1,0]
        self.assertEqual(10, width, msg="Width returned was unexpected")
        self.assertEqual(20, height, msg="Height returned was unexpected")        
        self.assertTrue((expected_landscape == landscape).all(), msg="Landscape returned was unexpected")

    def test_count_land_only(self):
        width, height, width_halo, height_halo, landscape = simulate_predator_prey.landscape_generator("map.dat")
        number_of_land_only = simulate_predator_prey.count_land_only(landscape)
        self.assertEqual(200, number_of_land_only, msg="Land-only squares number returned was unexpected")

    def test_num_of_land_neighbours(self):
        width, height, width_halo, height_halo, landscape = simulate_predator_prey.landscape_generator("map.dat")
        land_neighbours = simulate_predator_prey.num_of_land_neighbours(height_halo,width_halo,height,width,landscape)
        expected_land_neighbours = np.zeros((22,12), int)
        expected_land_neighbours[1] = expected_land_neighbours[20] = [0,2,3,3,3,3,3,3,3,3,2,0]
        for i in range(2, 20):
            expected_land_neighbours[i] = [0,3,4,4,4,4,4,4,4,4,3,0]
        self.assertTrue((expected_land_neighbours == land_neighbours).all(), msg="Number of land neighbours returned was unexpected")


    def test_swap_arrays(self):
        array1 = [[1,2,3,4],[9,8,7,6]]
        array2 = [[6,7,8,9],[4,3,2,1]]
        array1, array2 = simulate_predator_prey.swap_arrays(array1, array2)
        self.assertTrue((array1 == [[6,7,8,9],[4,3,2,1]] and array2 == [[1,2,3,4],[9,8,7,6]]), msg="arrays returned was unexpected")
        




