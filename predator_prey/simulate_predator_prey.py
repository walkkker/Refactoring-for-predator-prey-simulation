from argparse import ArgumentParser
import numpy as np
import random
import time

def sim():
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

    number_of_land_only=np.count_nonzero(landscape)
    print("Number of land-only squares: {}".format(number_of_land_only))

    # Pre-calculate number of land neighbours of each land square.
    neibs=np.zeros((height_halo,width_halo),int)
    for x in range(1,height+1):
        for y in range(1,width+1):
            neibs[x,y]=landscape[x-1,y] \
                + landscape[x+1,y] \
                + landscape[x,y-1] \
                + landscape[x,y+1]
    
	hs=landscape.astype(float).copy() # density of hares in the landscape
    ps=landscape.astype(float).copy() #density of pumas in the landscape
    random.seed(hare_seed)
    for x in range(1,height+1):
        for y in range(1,width+1):
            if hare_seed==0:
                hs[x,y]=0
            else:
                if landscape[x,y]:
                    hs[x,y]=random.uniform(0,5.0)
                else:
                    hs[x,y]=0
    random.seed(puma_seed)
    for x in range(1,height+1):
        for y in range(1,width+1):
            if puma_seed==0:
                ps[x,y]=0
            else:
                if landscape[x,y]:
                    ps[x,y]=random.uniform(0,5.0)
                else:
                    ps[x,y]=0

    # Create copies of initial maps and arrays for PPM file maps.
    # Reuse these so we don't need to create new arrays going round the simulation loop.
    hs_nu=hs.copy() #should be put at the end
    ps_nu=ps.copy() #should be put at hte end
    hcols=np.zeros((height,width),int) # wrong place, the below is the same
    pcols=np.zeros((height,width),int) # clour matrix
    if number_of_land_only != 0:
        ah=np.sum(hs)/number_of_land_only  #average of hares
        ap=np.sum(ps)/number_of_land_only  #average of pumas
    else:
        ah=0
        ap=0
    print("Averages. Timestep: {} Time (s): {} Hares: {} Pumas: {}".format(0,0,ah,ap))
    with open("averages.csv","w") as f:
        hdr="Timestep,Time,Hares,Pumas\n"
        f.write(hdr)


    tot_ts = int(duration / delta_t) # total_time_steps
    for i in range(0,tot_ts):
        if not i%time_step:
            mh=np.max(hs)
            mp=np.max(ps)
            if number_of_land_only != 0:
                ah=np.sum(hs)/number_of_land_only
                ap=np.sum(ps)/number_of_land_only
            else:
                ah=0
                ap=0
            print("Averages. Timestep: {} Time (s): {} Hares: {} Pumas: {}".format(i,i*delta_t,ah,ap))
            with open("averages.csv".format(i),"a") as f:
                f.write("{},{},{},{}\n".format(i,i*delta_t,ah,ap))

            for x in range(1,height+1):
                for y in range(1,width+1):
                    if landscape[x,y]:
                        if mh != 0:
                            hcol=(hs[x,y]/mh)*255  #color of hares 
                        else:
                            hcol = 0
                        if mp != 0:
                            pcol=(ps[x,y]/mp)*255 #color of pumas
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
                    hs_nu[x,y]=hs[x,y]+delta_t*((birth_hares*hs[x,y])-(death_hares*hs[x,y]*ps[x,y])+diffusion_hares*((hs[x-1,y]+hs[x+1,y]+hs[x,y-1]+hs[x,y+1])-(neibs[x,y]*hs[x,y])))
                    if hs_nu[x,y]<0:
                        hs_nu[x,y]=0
                    ps_nu[x,y]=ps[x,y]+delta_t*((birth_pumas*hs[x,y]*ps[x,y])-(death_pumas*ps[x,y])+diffusion_pumas*((ps[x-1,y]+ps[x+1,y]+ps[x,y-1]+ps[x,y+1])-(neibs[x,y]*ps[x,y])))
                    if ps_nu[x,y]<0:
                        ps_nu[x,y]=0
        # Swap arrays for next iteration.
        tmp=hs
        hs=hs_nu
        hs_nu=tmp
        tmp=ps
        ps=ps_nu
        ps_nu=tmp

if __name__ == "__main__":
    sim()
