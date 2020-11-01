from argparse import ArgumentParser
import numpy as np
import random
import time

def sim():
    par=ArgumentParser()
    par.add_argument("-r","--birth-hares",type=float,default=0.08,help="Birth rate of hares")
    par.add_argument("-a","--death-hares",type=float,default=0.04,help="Rate at which pumas eat hares")
    par.add_argument("-k","--diffusion-hares",type=float,default=0.2,help="Diffusion rate of hares")
    par.add_argument("-b","--birth-pumas",type=float,default=0.02,help="Birth rate of pumas")
    par.add_argument("-m","--death-pumas",type=float,default=0.06,help="Rate at which pumas starve")
    par.add_argument("-l","--diffusion-pumas",type=float,default=0.2,help="Diffusion rate of pumas")
    par.add_argument("-dt","--delta-t",type=float,default=0.4,help="Time step size")
    par.add_argument("-t","--time_step",type=int,default=10,help="Number of time steps at which to output files")
    par.add_argument("-d","--duration",type=int,default=500,help="Time to run the simulation (in timesteps)")
    par.add_argument("-f","--landscape-file",type=str,required=True,
                        help="Input landscape file")
    par.add_argument("-hs","--hare-seed",type=int,default=1,help="Random seed for initialising hare densities")
    par.add_argument("-ps","--puma-seed",type=int,default=1,help="Random seed for initialising puma densities")
    args=par.parse_args()
    r=args.birth_hares
    a=args.death_hares
    k=args.diffusion_hares
    b=args.birth_pumas
    m=args.death_pumas
    l=args.diffusion_pumas
    dt=args.delta_t
    t=args.time_step
    d=args.duration
    lfile=args.landscape_file
    hseed=args.hare_seed
    pseed=args.puma_seed
    with open(lfile,"r") as f:
        w,h=[int(i) for i in f.readline().split(" ")]
        print("Width: {} Height: {}".format(w,h))
        wh=w+2 # Width including halo
        hh=h+2 # Height including halo
        lscape=np.zeros((hh,wh),int)
        row=1
        for line in f.readlines():
            values=line.split(" ")
            # Read landscape into array,padding with halo values.
            lscape[row]=[0]+[int(i) for i in values]+[0]
            row += 1
    nlands=np.count_nonzero(lscape)
    print("Number of land-only squares: {}".format(nlands))
    # Pre-calculate number of land neighbours of each land square.
    neibs=np.zeros((hh,wh),int)
    for x in range(1,h+1):
        for y in range(1,w+1):
            neibs[x,y]=lscape[x-1,y] \
                + lscape[x+1,y] \
                + lscape[x,y-1] \
                + lscape[x,y+1]
    hs=lscape.astype(float).copy()
    ps=lscape.astype(float).copy()
    random.seed(hseed)
    for x in range(1,h+1):
        for y in range(1,w+1):
            if hseed==0:
                hs[x,y]=0
            else:
                if lscape[x,y]:
                    hs[x,y]=random.uniform(0,5.0)
                else:
                    hs[x,y]=0
    random.seed(pseed)
    for x in range(1,h+1):
        for y in range(1,w+1):
            if pseed==0:
                ps[x,y]=0
            else:
                if lscape[x,y]:
                    ps[x,y]=random.uniform(0,5.0)
                else:
                    ps[x,y]=0
    # Create copies of initial maps and arrays for PPM file maps.
    # Reuse these so we don't need to create new arrays going
    # round the simulation loop.
    hs_nu=hs.copy()
    ps_nu=ps.copy()
    hcols=np.zeros((h,w),int)
    pcols=np.zeros((h,w),int)
    if nlands != 0:
        ah=np.sum(hs)/nlands
        ap=np.sum(ps)/nlands
    else:
        ah=0
        ap=0
    print("Averages. Timestep: {} Time (s): {} Hares: {} Pumas: {}".format(0,0,ah,ap))
    with open("averages.csv","w") as f:
        hdr="Timestep,Time,Hares,Pumas\n"
        f.write(hdr)
    tot_ts = int(d / dt)
    for i in range(0,tot_ts):
        if not i%t:
            mh=np.max(hs)
            mp=np.max(ps)
            if nlands != 0:
                ah=np.sum(hs)/nlands
                ap=np.sum(ps)/nlands
            else:
                ah=0
                ap=0
            print("Averages. Timestep: {} Time (s): {} Hares: {} Pumas: {}".format(i,i*dt,ah,ap))
            with open("averages.csv".format(i),"a") as f:
                f.write("{},{},{},{}\n".format(i,i*dt,ah,ap))
            for x in range(1,h+1):
                for y in range(1,w+1):
                    if lscape[x,y]:
                        if mh != 0:
                            hcol=(hs[x,y]/mh)*255
                        else:
                            hcol = 0
                        if mp != 0:
                            pcol=(ps[x,y]/mp)*255
                        else:
                            pcol = 0
                        hcols[x-1,y-1]=hcol
                        pcols[x-1,y-1]=pcol
            with open("map_{:04d}.ppm".format(i),"w") as f:
                hdr="P3\n{} {}\n{}\n".format(w,x,255)
                f.write(hdr)
                for x in range(0,h):
                    for y in range(0,w):
                        if lscape[x+1,y+1]:
                            f.write("{} {} {}\n".format(hcols[x,y],pcols[x,y],0))
                        else:
                            f.write("{} {} {}\n".format(0,0,255))
        for x in range(1,h+1):
            for y in range(1,w+1):
                if lscape[x,y]:
                    hs_nu[x,y]=hs[x,y]+dt*((r*hs[x,y])-(a*hs[x,y]*ps[x,y])+k*((hs[x-1,y]+hs[x+1,y]+hs[x,y-1]+hs[x,y+1])-(neibs[x,y]*hs[x,y])))
                    if hs_nu[x,y]<0:
                        hs_nu[x,y]=0
                    ps_nu[x,y]=ps[x,y]+dt*((b*hs[x,y]*ps[x,y])-(m*ps[x,y])+l*((ps[x-1,y]+ps[x+1,y]+ps[x,y-1]+ps[x,y+1])-(neibs[x,y]*ps[x,y])))
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
