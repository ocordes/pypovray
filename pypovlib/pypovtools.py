# pypovtools.py

# wirtten by: Oliver Cordes 2015-03-26
# changed by: Oliver Cordes 2018-03-02

from  pypovlib.pypovobjects import *

import numpy as np


# special CSG objects based on unions an differences

class PovCSGHalfSphere( PovCSGDifference ):
    def __init__( self, _xyz, radius, comment=None ):
        xyz = convertarray2vector( _xyz )
        xyz2 = xyz + convertarray2vector( [0,-radius/2,0] )
        PovCSGDifference.__init__( self, comment=comment )
        s = PovCSGSphere( xyz, radius )
        self.add( s )
        b = PovCSGBoxCenter( xyz2, [ (radius*2)+self._D, radius+self._D, radius*2+self._D ] )
        self.add( b )



# special objects based on standard objects

class PovCSGNCorner( PovCSGPrism ):
    def __init__( self, y1, y2, N, radius, comment=None ):
        points = []
        for i in range( N ):
            alpha =  i*2*np.pi/N
            e = [ radius*np.sin( alpha ), radius*np.cos( alpha ) ]
            points.append( e )
        PovCSGPrism.__init__( self, y1, y2, points, comment=comment )



# half cylinder

# easy cylinder in xz-plane with height in y-direction

class PovCSGHalfCylinder( PovCSGDifference ):
    _D = 0.1
    def __init__( self, xyz, height, radius, comment=None ):
        PovCSGDifference.__init__( self )

        cyl = PovCSGCylinder( [0,0,0], [0,height,0], radius )

        box = PovCSGBox( [0,-self._D,-radius-self._D ],
                         [radius+self._D,height+self._D,radius+self._D ])
        self.add( [cyl, box] )

        self.set_translate( xyz )


class PovCSGHalfPipe( PovCSGDifference ):
    _D = 0.1
    def __init__( self, xyz, height, radius, width, comment=None ):
        PovCSGDifference.__init__( self )

        d = PovCSGDifference()
        cyl1 = PovCSGCylinder( [0,0,0], [0,height,0], radius )
        cyl2 = PovCSGCylinder( [0,-self._D,0],
                               [0,height+self._D,0], radius-width )
        d.add( [cyl1, cyl2] )

        box = PovCSGBox( [0,-self._D,-radius-self._D ],
                         [radius+self._D,height+self._D,radius+self._D ])
        self.add( [d, box] )

        self.set_translate( xyz )



# quarter cylinder

# easy cylinder in xz-plane with height in y-direction

class PovCSGQuarterCylinder( PovCSGDifference ):
    _D = 0.1
    def __init__( self, xyz, height, radius, comment=None ):
        PovCSGDifference.__init__( self, comment=comment )

        cyl = PovCSGCylinder( [0,0,0], [0,height,0], radius )

        u = PovCSGUnion()
        box1 = PovCSGBox( [0,-self._D,-radius-self._D ],
                         [radius+self._D,height+self._D,radius+self._D ])
        box2 = PovCSGBox( [self._D,-self._D, 0],
                         [-radius-self._D,height+self._D,radius+self._D ])
        u.add( [box1, box2] )
        self.add( [cyl, u] )

        self.set_translate( xyz )


class PovCSGQuarterPipe( PovCSGDifference ):
    _D = 0.1
    def __init__( self, xyz, height, radius, width, comment=None ):
        PovCSGDifference.__init__( self, comment=comment )

        d = PovCSGDifference()
        cyl1 = PovCSGCylinder( [0,0,0], [0,height,0], radius )
        cyl2 = PovCSGCylinder( [0,-self._D,0],
                               [0,height+self._D,0], radius-width )
        d.add( [cyl1, cyl2] )

        u = PovCSGUnion()
        box1 = PovCSGBox( [0,-self._D,-radius-self._D ],
                         [radius+self._D,height+self._D,radius+self._D ])
        box2 = PovCSGBox( [self._D,-self._D, 0],
                         [-radius-self._D,height+self._D,radius+self._D ])

        u.add( [box1, box2] )
        self.add( [d, u] )

        self.set_translate( xyz )


class PovImagePlate( PovCSGBox ):
    def __init__( self, imagename, comment=None ):
        PovCSGBox.__init__( self, [-0.5,-0.5,0.], [0.5,0.5,0.0001] )

        # define all imagemaps, pigments, textures
        im = PovImageMap( imagename, 0, True )
        pigment = PovPigment( image_map=im )
        pigment.set_translate( [-0.5,-0.5,-0.5] )
        texture = PovTexture()
        texture.set_pigment( pigment )
        self.set_texture( texture )

    def do_statistics( self ):
        self.add_stat_count( 'ImagePlate' )
