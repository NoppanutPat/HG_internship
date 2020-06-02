import math
import argparse

parser = argparse.ArgumentParser(description='Find box inertia.')
parser.add_argument('-H','--height',help="Height of the box")
parser.add_argument('-w','--weight',help="weight of the box")
parser.add_argument('-d','--depth',help="depth of the box")
parser.add_argument('-m','--mass',help="mass of the box")

args = parser.parse_args()
# print(args)

m = float(args.mass)
h = float(args.height)
d = float(args.depth)
w = float(args.weight)

inertia1 = str(m*((h*h)+(d*d))/12)
inertia2 = str(m*((w*w)+(d*d))/12)
inertia3 = str(m*((h*h)+(w*w))/12)

print(inertia1 , inertia2 , inertia3)