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
        self.assertEqual(12, width_halo, msg="Width_halo returned was unexpected")
        self.assertEqual(22, height_halo, msg="Height_halo returned was unexpected") 
        self.assertTrue((expected_landscape == landscape).all(), msg="Landscape returned was unexpected")


    def test_landscape_generator_no_file(self):
        with self.assertRaises(FileNotFoundError):
            simulate_predator_prey.landscape_generator(" ")


    def test_landscape_generator_nonExisting_file(self):
        with self.assertRaises(FileNotFoundError):
            simulate_predator_prey.landscape_generator("1234")
         

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


    def test_density_generator_invalid_width(self):
        width, height, width_halo, height_halo, landscape = simulate_predator_prey.landscape_generator("map.dat")
        seed = 1
        with self.assertRaises(IndexError):      
            width = 12 #invald
            simulate_predator_prey.density_generator(landscape, seed, width, height)
 
    def test_density_generator_invalid_height(self):
        width, height, width_halo, height_halo, landscape = simulate_predator_prey.landscape_generator("map.dat")
        seed = 1
        with self.assertRaises(IndexError):      
            height = 22 #invald
            simulate_predator_prey.density_generator(landscape, seed, width, height)
    
    def test_average_of_density(self):
        width, height, width_halo, height_halo, landscape = simulate_predator_prey.landscape_generator("map.dat")
        seed = 1
        generated_density = simulate_predator_prey.density_generator(landscape, seed, width, height)
        number_of_land_only = simulate_predator_prey.count_land_only(landscape)
        average = simulate_predator_prey.average_of_density(generated_density, number_of_land_only)
        #self.assertEqual(2.4268595788671457, average, msg = "Average returned was unexpected")  
        self.assertAlmostEqual(2.4268595788671457, average, delta=0.00000001, msg = "Average returned was unexpected")
            

    def test_average_of_density_no_land(self):
        number_of_land_only = 0
        densities = np.array([[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]])
        average = simulate_predator_prey.average_of_density(densities, number_of_land_only)
        self.assertEqual(0, average, msg = "Average returned was unexpected")


    def test_single_color_point_max_is_zero(self):
        max_density = 0
        densities_single_point = 0
        col = simulate_predator_prey.single_color_point(max_density, densities_single_point)
        self.assertEqual(0, col, msg = "Single color point returned was unexpected")

    def test_ppm_color_matrix_invalid_width(self):
        width, height, width_halo, height_halo, landscape = simulate_predator_prey.landscape_generator("map.dat")
        hare_densities = simulate_predator_prey.density_generator(landscape, 1, width, height)
        puma_densities = simulate_predator_prey.density_generator(landscape, 1, width, height)
        hare_cols=np.zeros((height,width),int) 
        puma_cols=np.zeros((height,width),int)
        width = 12
        with self.assertRaises(IndexError):
            simulate_predator_prey.ppm_color_matrix(hare_densities, puma_densities, landscape, width, height, hare_cols, puma_cols)


    def test_swap_arrays(self):
        array1 = original_array1 = np.array([[1,2,3,4],[9,8,7,6]])
        array2 = original_array2 = np.array([[6,7,8,9],[4,3,2,1]])
        array1, array2 = simulate_predator_prey.swap_arrays(array1, array2)
        self.assertTrue(((array1 == original_array2).all() and (array2 == original_array1).all()), msg="Swap arrays returned was unexpected")
        




