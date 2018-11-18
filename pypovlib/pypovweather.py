# pypovwearther.py

# wirtten by: Oliver Cordes 2015-09-06
# changed by: Oliver Cordes 2016-09-24

import sys

try:
    import numpy as np
except:
    print( 'Please install numpy to use with pypovobjects.py!' )
    sys.exit( 1 )


from pypovlib.pypovobjects import *
from pypovlib.pypovbase import *


class PovDrop( PovCSGObject ):
    def __init__( self, xyz, top, bottom, v, start=None ):
        PovCSGObject.__init__( self )

        self._xyz    = xyz
        self._top    = top
        self._bottom = bottom
        self._start  = start

        if self._start is None:
            self._start = self._top


class PovRainDrop( PovDrop ):
    def __init__( self, xyz, top, bottom, v, start=None ):
        PovDrop.__init__(  self, xyz, top, bottom, v, start=None )

    def write_pov( self, ffile, indent = 0 ):
        s = PovCSGSphere( self._xyz, 0.1 )
        s.write_pov( ffile, indent = indent )
    

class PovSnowDrop( PovDrop ):
    def __init__( self, xyz, top, bottom, v, start=None ):
        PovDrop.__init__(  self, xyz, top, bottom, v, start=None )

    def write_pov( self, ffile, indent = 0 ):
        pass


class PovDropField( PovCSGUnion ):
    def __init__( self, x1, y1, x2, y2, z1, z2, nx, ny, nz, distribution, comment=None  ):
        PovCSGUnion.__init__( self, comment=comment )

        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        self._z1 = z1
        self._z2 = z2

        self._nx = nx
        self._ny = ny
        self._nz = nz
        self._distribution = distribution

        self._v = 0.1
        
        # create the drops
        self._create_field()


    def _create_field_homogenious( self ):
        x_v = np.linspace( self._x1, self._x2, self._nx )
        y_v = np.linspace( self._y1, self._y2, self._ny )
        z_v = np.linspace( self._z1, self._z2, self._nz )

        for x in x_v:
            for y in y_v:
                for z in z_v:
                    self._create_drop( np.array( [x,y,z] ), self._z2, self._z1, self._v )

                    
    def _create_field( self ):
        if self._distribution == 0:
            self._create_field_homogenious()        # create the drops


    # abstract procedure to create a single drop 
    def _create_drop( self, xyz, top, bottom, v ):
        pass




class PovRainField( PovDropField ):
    def __init__( self, x1, y1, x2, y2, z1, z2, nx, ny, nz, distribution ):
        PovDropField.__init__( self, x1, y2, x2, y2, z1, z2, nx, ny, nz, distribution, comment='Rainfield' )


    def _create_drop( self, xyz, top, bottom, v ):
        drop = PovRainDrop( xyz, top, bottom, v )
        self.add( drop )
