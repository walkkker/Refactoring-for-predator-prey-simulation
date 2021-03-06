from argparse import ArgumentParser
import numpy as np
import random
import time


def args_parser():
    parser = ArgumentParser()
    parser.add_argument("-r","--birth-hares",type=float,default=0.08,help="Birth rate of hares")
    parser.add_argument("-a","--death-hares",type=float,default=0.04,help="Rate at which pumas eat hares")
    parser.add_argument("-k","--diffusion-hares",type=float,default=0.2,help="Diffusion rate of hares")
    parser.add_argument("-b","--birth-pumas",type=float,default=0.02,help="Birth rate of pumas")
    parser.add_argument("-m","--death-pumas",type=float,default=0.06,help="Rate at which pumas starve")
    parser.add_argument("-l","--diffusion-pumas",type=float,default=0.2,help="Diffusion rate of pumas")
    parser.add_argument("-dt","--delta-t",type=float,default=0.4,help="Time step size")
    parser.add_argument("-t","--time_step",type=int,default=10,help="Number of time steps at which to output files")
    parser.add_argument("-d","--duration",type=int,default=500,help="Time to run the simulation (in timesteps)")
    parser.add_argument("-f","--landscape-file",type=str,required=True,
                        help="Input landscape file")
    parser.add_argument("-hs","--hare-seed",type=int,default=1,help="Random seed for initialising hare densities")
    parser.add_argument("-ps","--puma-seed",type=int,default=1,help="Random seed for initialising puma densities")  
    args = parser.parse_args()
    return args


def landscape_generator(landscape_file):
    with open(landscape_file,"r") as f:
        width,height = [int(i) for i in f.readline().split(" ")]
        print("Width: {} Height: {}".format(width,height))

        width_halo = width+2 # Width including halo
        height_halo = height+2 # Height including halo
        landscape = np.zeros((height_halo,width_halo),int)
        row = 1
        for line in f.readlines():
            values=line.split(" ")
            # Read landscape into array, padding with halo values.
            landscape[row]=[0]+[int(i) for i in values]+[0]
            row += 1
    return width, height, width_halo, height_halo, landscape


def count_land_only(landscape):
    number_of_land_only = np.count_nonzero(landscape)
    print("Number of land-only squares: {}".format(number_of_land_only))
    return number_of_land_only


def num_of_land_neighbours(height_halo,width_halo,height,width,landscape):
    # Calculate number of land neighbours of each land square.
    land_neighbours = np.zeros((height_halo,width_halo),int)
    for x in range(1,height+1):
        for y in range(1,width+1):
            land_neighbours[x,y] = landscape[x-1,y] \
                + landscape[x+1,y] \
                + landscape[x,y-1] \
                + landscape[x,y+1]
    return land_neighbours


def density_generator(landscape, seed, width, height):
    generated_density = landscape.astype(float).copy()
    random.seed(seed)
    for x in range(1,height+1):
        for y in range(1,width+1):
            if seed == 0:
                generated_density[x,y]=0
            else:
                if landscape[x,y]:
                    generated_density[x,y] = random.uniform(0,5.0)
                else:
                    generated_density[x,y]=0
    return generated_density


def average_of_density(densities, number_of_land_only):
    if number_of_land_only != 0:
        average = np.sum(densities)/number_of_land_only  #calculate the average of dendity
    else:
        average = 0
    return average


def averages_output(i, delta_t, hare_densities, puma_densities, number_of_land_only):  
    average_of_hares = average_of_density(hare_densities, number_of_land_only)
    average_of_pumas = average_of_density(puma_densities, number_of_land_only)
    print("Averages. Timestep: {} Time (s): {} Hares: {} Pumas: {}".format(i,i*delta_t,average_of_hares,average_of_pumas))
    with open("averages.csv".format(i),"a") as f:
        f.write("{},{},{},{}\n".format(i,i*delta_t,average_of_hares,average_of_pumas))


def single_color_point(max_density, densities_single_point):
    if max_density != 0:
        col = (densities_single_point/max_density)*255
    else:
        col = 0
    return col


def ppm_color_matrix(hare_densities, puma_densities, landscape, width, height, hare_cols, puma_cols):
    max_hare_density=np.max(hare_densities)
    max_puma_density=np.max(puma_densities)
    for x in range(1, height+1):
        for y in range(1, width+1):
            if landscape[x, y]:
                hare_cols[x-1, y-1]=single_color_point(max_hare_density, hare_densities[x,y])
                puma_cols[x-1, y-1]=single_color_point(max_puma_density, puma_densities[x,y])
    return hare_cols, puma_cols


def generate_ppm_file(i, landscape, width, height, hare_cols, puma_cols):
    with open("map_{:04d}.ppm".format(i),"w") as f:
        header="P3\n{} {}\n{}\n".format(width, height,255)
        f.write(header)
        for x in range(0, height):
            for y in range(0, width):
                if landscape[x+1, y+1]:
                    f.write("{} {} {}\n".format(hare_cols[x,y], puma_cols[x, y], 0))
                else:
                    f.write("{} {} {}\n".format(0, 0, 255))


def swap_arrays(array1, array2):
    # Swap arrays for next iteration.
    return array2, array1


def simulation():
    args = args_parser()

    birth_hares = args.birth_hares
    death_hares = args.death_hares
    diffusion_hares = args.diffusion_hares
    birth_pumas = args.birth_pumas
    death_pumas = args.death_pumas
    diffusion_pumas = args.diffusion_pumas
    delta_t = args.delta_t
    time_step = args.time_step
    duration = args.duration
    landscape_file = args.landscape_file
    hare_seed = args.hare_seed
    puma_seed = args.puma_seed

    # width_halo: Width including halo; height_halo: Height including halo
    width, height, width_halo, height_halo, landscape = landscape_generator(landscape_file)

    number_of_land_only = count_land_only(landscape)


    hare_densities = density_generator(landscape, hare_seed, width, height)
    puma_densities = density_generator(landscape, puma_seed, width, height)

    average_of_hares = average_of_density(hare_densities, number_of_land_only)
    average_of_pumas = average_of_density(puma_densities, number_of_land_only)

    print("Averages. Timestep: {} Time (s): {} Hares: {} Pumas: {}".format(0,0,average_of_hares,average_of_pumas))

    with open("averages.csv","w") as f:
        header="Timestep,Time,Hares,Pumas\n"
        f.write(header)

    # Create copies of initial maps and arrays for PPM file maps.
    hare_density_copy = hare_densities.copy() 
    puma_density_copy = puma_densities.copy() 
    hare_cols = np.zeros((height, width), int) 
    puma_cols = np.zeros((height, width), int) # colour matrix
    
    # Calculate number of land neighbours of each land square.
    neibs = num_of_land_neighbours(height_halo, width_halo, height, width, landscape)

    total_time_steps = int(duration / delta_t)
    for i in range(0, total_time_steps):
        if not i%time_step:
            
            averages_output(i, delta_t, hare_densities, puma_densities, number_of_land_only) # output for both file and print

            hare_cols, puma_cols = ppm_color_matrix(hare_densities, puma_densities, landscape, width, height, hare_cols, puma_cols)

            generate_ppm_file(i, landscape, width, height, hare_cols, puma_cols)

        for x in range(1, height+1):
            for y in range(1, width+1):
                if landscape[x, y]:
                    hare_density_copy[x, y] = hare_densities[x, y]+delta_t*((birth_hares*hare_densities[x, y])-(death_hares*hare_densities[x, y]*puma_densities[x, y])+diffusion_hares*((hare_densities[x-1, y]+hare_densities[x+1, y]+hare_densities[x, y-1]+hare_densities[x, y+1])-(neibs[x, y]*hare_densities[x, y])))
                    if hare_density_copy[x, y]<0:
                        hare_density_copy[x, y] = 0
                    puma_density_copy[x, y] = puma_densities[x, y]+delta_t*((birth_pumas*hare_densities[x, y]*puma_densities[x, y])-(death_pumas*puma_densities[x, y])+diffusion_pumas*((puma_densities[x-1, y]+puma_densities[x+1, y]+puma_densities[x, y-1]+puma_densities[x, y+1])-(neibs[x, y]*puma_densities[x, y])))
                    if puma_density_copy[x, y]<0:
                        puma_density_copy[x, y] = 0
        # Swap arrays for next iteration.
        hare_densities, hare_density_copy = swap_arrays(hare_densities, hare_density_copy)
        puma_densities, puma_density_copy = swap_arrays(puma_densities, puma_density_copy)

if __name__ == "__main__":
    simulation()
