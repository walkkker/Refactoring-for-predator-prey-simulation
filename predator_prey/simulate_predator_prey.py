from argparse import ArgumentParser
import numpy as np
import random
import time

def args_parser():
    parser=ArgumentParser()
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
    args=parser.parse_args()
    return args

def landscape_generator(landscape_file):
    with open(landscape_file,"r") as f:
        width,height=[int(i) for i in f.readline().split(" ")]
        print("Width: {} Height: {}".format(width,height))
        width_halo=width+2 # Width including halo
        height_halo=height+2 # Height including halo
        landscape=np.zeros((height_halo,width_halo),int)
        row=1
        for line in f.readlines():
            values=line.split(" ")
            # Read landscape into array, padding with halo values.
            landscape[row]=[0]+[int(i) for i in values]+[0]
            row += 1
    return width, height, width_halo, height_halo, landscape

def count_land_only(landscape):
    number_of_land_only=np.count_nonzero(landscape)
    print("Number of land-only squares: {}".format(number_of_land_only))
    return number_of_land_only

def num_of_land_neighbours(height_halo,width_halo,height,width,landscape):    
    land_neighbours=np.zeros((height_halo,width_halo),int)
    for x in range(1,height+1):
        for y in range(1,width+1):
            land_neighbours[x,y]=landscape[x-1,y] \
                + landscape[x+1,y] \
                + landscape[x,y-1] \
                + landscape[x,y+1]
    return land_neighbours

def sim():

    args = args_parser()

    birth_hares=args.birth_hares
    death_hares=args.death_hares
    diffusion_hares=args.diffusion_hares
    birth_pumas=args.birth_pumas
    death_pumas=args.death_pumas
    diffusion_pumas=args.diffusion_pumas
    delta_t=args.delta_t
    time_step=args.time_step
    duration=args.duration
    landscape_file=args.landscape_file
    hare_seed=args.hare_seed
    puma_seed=args.puma_seed

    # width_halo: Width including halo; height_halo: Height including halo
    width, height, width_halo, height_halo, landscape = landscape_generator(landscape_file)

    number_of_land_only = count_land_only(landscape)

    # Pre-calculate number of land neighbours of each land square.
    neibs = num_of_land_neighbours(height_halo,width_halo,height,width,landscape)

    hare_densities = density_generator(landscape, hare_seed, width, height)
    puma_densities = density_generator(landscape, puma_seed, width, height)

    average_of_hares = average_of_density(hare_densities, number_of_land_only)
    average_of_pumas = average_of_density(puma_densities, number_of_land_only)

    print("Averages. Timestep: {} Time (s): {} Hares: {} Pumas: {}".format(0,0,average_of_hares,average_of_pumas))

    with open("averages.csv","w") as f:
        hdr="Timestep,Time,Hares,Pumas\n"
        f.write(hdr)


    # Create copies of initial maps and arrays for PPM file maps.
    # Reuse these so we don't need to create new arrays going round the simulation loop.
    hs_nu=hare_densities.copy() 
    ps_nu=puma_densities.copy() 
    hcols=np.zeros((height,width),int) 
    pcols=np.zeros((height,width),int) # clour matrix
    

    total_time_steps = int(duration / delta_t)
    for i in range(0,total_time_steps):
        if not i%time_step:
            max_hare_density=np.max(hare_densities)
            max_puma_density=np.max(puma_densities)

            average_of_hares = average_of_density(hare_densities, number_of_land_only)
            average_of_pumas = average_of_density(puma_densities, number_of_land_only)

            print("Averages. Timestep: {} Time (s): {} Hares: {} Pumas: {}".format(i,i*delta_t,average_of_hares,average_of_pumas))
            with open("averages.csv".format(i),"a") as f:
                f.write("{},{},{},{}\n".format(i,i*delta_t,average_of_hares,average_of_pumas))



            for x in range(1,height+1):
                for y in range(1,width+1):
                    if landscape[x,y]:
                        if max_hare_density != 0:
                            hcol=(hare_densities[x,y]/max_hare_density)*255  #color of hares 
                        else:
                            hcol = 0
                        if max_puma_density != 0:
                            pcol=(puma_densities[x,y]/max_puma_density)*255 #color of pumas
                        else:
                            pcol = 0
                        hcols[x-1,y-1]=hcol
                        pcols[x-1,y-1]=pcol

            with open("map_{:04d}.ppm".format(i),"w") as f:
                hdr="P3\n{} {}\n{}\n".format(width,x,255)
                f.write(hdr)
                for x in range(0,height):
                    for y in range(0,width):
                        if landscape[x+1,y+1]:
                            f.write("{} {} {}\n".format(hcols[x,y],pcols[x,y],0))
                        else:
                            f.write("{} {} {}\n".format(0,0,255))

        for x in range(1,height+1):
            for y in range(1,width+1):
                if landscape[x,y]:
                    hs_nu[x,y]=hare_densities[x,y]+delta_t*((birth_hares*hare_densities[x,y])-(death_hares*hare_densities[x,y]*puma_densities[x,y])+diffusion_hares*((hare_densities[x-1,y]+hare_densities[x+1,y]+hare_densities[x,y-1]+hare_densities[x,y+1])-(neibs[x,y]*hare_densities[x,y])))
                    if hs_nu[x,y]<0:
                        hs_nu[x,y]=0
                    ps_nu[x,y]=puma_densities[x,y]+delta_t*((birth_pumas*hare_densities[x,y]*puma_densities[x,y])-(death_pumas*puma_densities[x,y])+diffusion_pumas*((puma_densities[x-1,y]+puma_densities[x+1,y]+puma_densities[x,y-1]+puma_densities[x,y+1])-(neibs[x,y]*puma_densities[x,y])))
                    if ps_nu[x,y]<0:
                        ps_nu[x,y]=0
        # Swap arrays for next iteration.
        hare_densities, hs_nu = swap_arrays(hare_densities, hs_nu)
        puma_densities, ps_nu = swap_arrays(puma_densities, ps_nu)






def density_generator(landscape, seed, width, height):
    generated_density = landscape.astype(float).copy() # density of hares in the landscape
    random.seed(seed)
    for x in range(1,height+1):
        for y in range(1,width+1):
            if seed==0:
                generated_density[x,y]=0
            else:
                if landscape[x,y]:
                    generated_density[x,y]=random.uniform(0,5.0)
                else:
                    generated_density[x,y]=0
    return generated_density


def average_of_density(density, number_of_land_only):
    if number_of_land_only != 0:
        avarage = np.sum(density)/number_of_land_only  #calculate the average of dendity
    else:
        avarage = 0
    return avarage


def swap_arrays(array1, array2):
    return array2,array1

if __name__ == "__main__":
    sim()
