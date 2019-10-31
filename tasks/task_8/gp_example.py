
import numpy as np
from scipy import stats
from mayavi import mlab
import multiprocessing

import json
import pandas as pd
import numpy as np
from numpy import linspace

from gp_tools import GpRegressor


print('starting')

with open('simulation_results2.json') as f:
    results = json.load(f)

results_df = pd.DataFrame(results)
flibe = results_df[results_df['breeder_material_name']=='Flibe']


x=10*np.array(flibe['enrichment_fraction'])
print('x',x)
y=0.01*np.array(flibe['thickness'])
print('y',y)
z=0.01*np.array(flibe['inner_radius'])
print('z',z)
vals=np.array(flibe['tbr_tally'])

print('vals',vals)


coords = list(zip(x,y,z))

GP = GpRegressor(coords, vals)#,scale_lengths=[140,60])#,hyperpars=[0.6,3])

bins = 30

x_gp = linspace( min(x), max(x), bins)
y_gp = linspace( min(y), max(y), bins)
z_gp = linspace( min(z), max(z), bins)
coords_gp = [ (i,j,k) for i in x_gp for j in y_gp for k in z_gp]

results, gp_sigma = GP(coords_gp)


xmin, ymin, zmin = min(x), min(y), min(z)
xmax, ymax, zmax = max(x), max(y), max(z)

xi, yi, zi = np.mgrid[xmin:xmax:30j, ymin:ymax:30j, zmin:zmax:30j]
coords = np.vstack([item.ravel() for item in [xi, yi, zi]]) 





# # Plot scatter with mayavi
figure = mlab.figure('DensityPlot')

grid = mlab.pipeline.scalar_field(xi, yi, zi, (results).reshape(xi.shape) )
min = 1.0
max=1.2
mlab.pipeline.volume(grid)

mlab.axes(xlabel='enrichment_fraction',ylabel='thickness',zlabel='tbr')
mlab.show()

