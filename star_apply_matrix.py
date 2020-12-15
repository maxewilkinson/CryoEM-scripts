import numpy as np
import math
import sys
import argparse
import os
from collections import OrderedDict


def load_star(filename):
    # thanks Takanori
    datasets = OrderedDict()
    current_data = None
    current_colnames = None
    
    in_loop=0 # where 0:outside 1: reading colnames 2: reading data
    for line in open(filename):
        line=line.strip()
        
        comment_pos = line.find('#')
        if comment_pos >= 0:
            line = line[:comment_pos]
        if line == "":
            continue
        if line.startswith("data_"):
            in_loop=0
            
            data_name = line[5:]
            print(data_name)
            current_data = OrderedDict()
            datasets[data_name] = current_data
        
        elif line.startswith("loop_"):
            current_colnames = []
            in_loop=1
        
        elif line.startswith("_"):
            if in_loop ==2:
                in_loop = 0
            
            elems = line[1:].split()
            if in_loop == 1:
                current_colnames.append(elems[0])
                current_data[elems[0]] = []
            else:
                current_data[elems[0]] = elems[1]
        
        elif in_loop > 0:
            in_loop = 2
            elems = line.split()
            #print(elems)
            assert len(elems) == len(current_colnames)
            for idx, e in enumerate(elems):
                current_data[current_colnames[idx]].append(e)
        
    return datasets


def Euler_angles2matrix(rot,tilt,psi): #rot = alpha, tilt = beta, psi = gamma
    A=np.zeros((3,3))
    rot=math.radians(rot)
    tilt=math.radians(tilt)
    psi=math.radians(psi)
    
    ca=np.cos(rot)
    cb=np.cos(tilt)
    cg=np.cos(psi)
    sa=np.sin(rot)
    sb=np.sin(tilt)
    sg=np.sin(psi)
    cc = cb*ca
    cs = cb*sa
    sc = sb*ca
    ss = sb*sa
    
    A[0,0] =  cg * cc - sg * sa
    A[0,1] =  cg * cs + sg * ca
    A[0,2] = -cg * sb
    A[1,0] = -sg * cc - cg * sa
    A[1,1] = -sg * cs + cg * ca
    A[1,2] = sg * sb
    A[2,0] =  sc
    A[2,1] =  ss
    A[2,2] = cb
    
    return(A)
    

def Euler_matrix2angles(A):
    if A.shape != (3,3):
        print("Matrix should be 3x3")
    FLT_EPSILON=sys.float_info.epsilon
    if np.abs(A[1,1]) > FLT_EPSILON:
        abs_sb = np.sqrt((-A[2,2]*A[1,2]*A[2,1]-A[0,2]*A[2,0])/A[1,1])
    elif np.abs(A[0,1]) > FLT_EPSILON:
        abs_sb = np.sqrt((-A[2,1]*A[2,2]*A[0,2]+A[2,0]*A[1,2])/A[0,1])
    elif np.abs(A[0,0]) > FLT_EPSILON:
        abs_sb = np.sqrt((-A[2,0]*A[2,2]*A[0,2]-A[2,1]*A[1,2])/A[0,0])
    else:
        print("NOPE")
    if abs_sb > FLT_EPSILON:
        beta = np.arctan2(abs_sb, A[2,2])
        alpha = np.arctan2(A[2,1]/abs_sb, A[2,0] / abs_sb)
        gamma = np.arctan2(A[1,2] / abs_sb, -A[0,2] / abs_sb)
    else:
        alpha=0
        beta=0
        gamma = np.arctan2(A[1,0],A[0,0])
    gamma = math.degrees(gamma)
    beta = math.degrees(beta)
    alpha = math.degrees(alpha)
    return(alpha,beta,gamma)  

    
def write_star(mystar,filename):
    f = open(filename,"w")
    datasets=[data for data in mystar.keys()]
    for data in datasets:
        f.write("data_{}\n".format(data))
        f.write("\n")
        f.write("loop_\n")
        fields=[field for field in mystar[data].keys()]
        i=1
        for field in fields:
            f.write("_{} #{}\n".format(field,i))
            i+=1
        totalN=len(mystar[data][fields[1]])
        for n in range(totalN):
            for field in fields:
                f.write("{}\t".format(mystar[data][field][n]))
            f.write("\n")
        f.write("\n")
    f.close()



def star_apply_matrix(starpath,matrix,classToMove,outstarpath,boxsize,angpix):
    star=load_star(starpath)
    print(classToMove)
    shift=matrix[:,3]
    rotmat=matrix[:,:3]
    #rotmat=Euler_angles2matrix(-90,0,0)
    #shift=np.array([336,0,0])

    Xs=np.array(star['particles']['rlnOriginXAngst']).astype(np.float)
    Ys=np.array(star['particles']['rlnOriginYAngst']).astype(np.float)
    Psis=np.array(star['particles']['rlnAnglePsi']).astype(np.float)
    Rots=np.array(star['particles']['rlnAngleRot']).astype(np.float)
    Tilts=np.array(star['particles']['rlnAngleTilt']).astype(np.float)
    Classes=np.array(star['particles']['rlnClassNumber']).astype(np.int)

    newXs=[]
    newYs=[]
    
    newPsis=[]
    newRots=[]
    newTilts=[]
    
    for n in range(len(Xs)):
        if n % 50000 ==0:
            print(n)
        if Classes[n]==classToMove:
            A3D=Euler_angles2matrix(Rots[n],Tilts[n],Psis[n])
            A3D=A3D.dot(np.linalg.inv(rotmat))
            mapcenter=np.array([boxsize,boxsize,boxsize])*angpix/2
            #mapcenter=np.array([200,200,200])*1.12
            trueshift=shift-(mapcenter-rotmat.dot(mapcenter))
            new_center=A3D.dot(trueshift)
            newX=Xs[n]+new_center[0]
            newY=Ys[n]+new_center[1]
            newrot,newtilt,newpsi=Euler_matrix2angles(A3D)
            newXs.append(str(newX))
            newYs.append(str(newY))
            newPsis.append(str(newpsi))
            newTilts.append(str(newtilt))
            newRots.append(str(newrot))
        
        else:
            newXs.append(str(Xs[n]))
            newYs.append(str(Ys[n]))
            newPsis.append(str(Psis[n]))
            newTilts.append(str(Tilts[n]))
            newRots.append(str(Rots[n]))

    star['particles']['rlnOriginXAngst']=newXs
    star['particles']['rlnOriginYAngst']=newYs
    star['particles']['rlnAnglePsi']=newPsis
    star['particles']['rlnAngleTilt']=newTilts
    star['particles']['rlnAngleRot']=newRots

    write_star(star,outstarpath)


def main():
	usage = """Example: python star_apply_matrix.py --i Class3D/job049/run_it025_data.star --matrix chimeramatrix.txt --class 1 --boxsize 300 --angpix 1.12 --o class1shifted.star
	
	Applies a rotation/translation transformation matrix to the Euler angles and offsets of particles of a particular class in a STAR file. 
    Can be used to align particles based on class orientations.
    """

	#parser = OptionParser(usage=usage)
	parser = argparse.ArgumentParser(description='')
    
	parser.add_argument("--classN", help="Number of the class to move")
	parser.add_argument("--matrix", help="Text file with 3x4 transformation matrix from Chimera")
	parser.add_argument("--boxsize", help="The box size of your reference volume")
	parser.add_argument("--angpix", help="The pixel size of your reference volume")
	parser.add_argument("--i", help="Input STAR file")
	parser.add_argument("--o", help="Output STAR file")
	if len(sys.argv)==1:
		print(usage)
		parser.print_help(sys.stderr)

		sys.exit(1)
	args = parser.parse_args()
    
	inputstar=str(args.i)
	outputstar=str(args.o)
	matrixpath=str(args.matrix)
	classN=int(args.classN)
	angpix=float(args.angpix)
	boxsize=int(args.boxsize)
    
	matrix=np.loadtxt(matrixpath)
	star_apply_matrix(inputstar,matrix,classN,outputstar,boxsize,angpix)


if __name__ == "__main__":
    main()
