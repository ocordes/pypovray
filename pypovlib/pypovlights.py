# pypovlights.py

# wirtten by: Oliver Cordes 2015-05-02
# changed by: Oliver Cordes 2018-04-04

import sys

try:
    import numpy as np
except:
    print( 'Please install numpy to use with pypovobjects.py!' )
    sys.exit( 1 )


from pypovlib.pypovobjects import *

# constants


# basic definitions of the light_source object
#
class PovBasicLights(PovObject):
    def __init__( self, comment=None ):
        PovBasicObject.__init__( self, comment=comment )

        self._translate     = None
        self._rotate        = None
        self._scale         = None
        self._rotate_anchor = np.array( [ 0.0, 0.0, 0.0 ] )
        self.bound_object   = True

        self.fade_distance  = None
        self.fade_power     = None

        self.looks_like     = None


    def set_translate(self, xyz):
        self._translate = Point3D(xyz)


    def set_scale(self, xyz):
        self._scale = Point3D(xyz)


    def delta_translate( self, xyz ):
        dxyz = Point3D( xyz )
        self._translate += dxyz


    def set_rotate( self, new_rotate ):
        self._rotate = Point3D( new_rotate )


    def correct_params( self ):
        pass


    def verify(self):
        pass


    def write_pov( self, ffile, indent=0 ):
        # correct all parameter, including rotation
        self.correct_params()
        self._write_indent( ffile, 'light_source{\n', indent )
        self.write_lights( ffile, indent+1 )
        if self.looks_like is not None:
            self._write_indent( ffile, 'looks_like{\n', indent+1 )
            self._write_indent( ffile, '%s\n' % self.looks_like, indent+2 )
            self._write_indent( ffile, '}\n', indent+1 )
        if self._scale is not None:
            self._write_indent(ffile, 'scale %s\n' % self._scale, indent+1)
        if self._translate is not None:
            self._write_indent( ffile, 'translate %s\n' % self._translate, indent+1 )
        if self.fade_distance is not None:
            self._write_indent( ffile, 'fade_distance %f\n' % self.fade_distance, indent+1 )
        if self.fade_power is not None:
            self._write_indent( ffile, 'fade_power %f\n' % self.fade_power, indent+1 )
        self._write_indent( ffile, '}\n', indent )


    def write_lights( self, ffile, indent=0 ):
        pass


# simple light_source object from raw povray code
#
class PovTextLights( PovBasicLights ):
    def __init__( self, macrocmd, comment=None ):
        PovBasicLights.__init__( self )

        self._macrocmd = macrocmd


    def write_lights( self, ffile, indent=0 ):
        self._write_indent( ffile, '%s\n' % self._macrocmd, indent )


# basic definition of light types
class PovBasicLightObject( PovBasicLights ):
    def __init__( self, xyz, color, comment=None ):
        PovBasicLights.__init__( self, comment )

        self.__xyz   = Point3D( xyz )
        self.__color = color


    @property
    def xyz(self):
        return self.__xyz


    @xyz.setter
    def xyz(self, val):
        self.__xyz = val


    def verify( self ):
        PovBasicLights.verify(self)


    def _correct_position( self, x ):
        if self._rotate is None:
            return x

        # correct for rotation
        zero_delta = (x - self._rotate_anchor).copy()
        x = self._rotate_anchor.copy()  # start with the anchor point

        # correct for rotation
        r = self._rotate * np.pi / 180.0

        # x-axis
        newxyz = zero_delta.copy()
        newxyz[1] =   zero_delta[1] * np.cos( r[0] ) - zero_delta[2] * np.sin( r[0] )
        newxyz[2] =   zero_delta[1] * np.sin( r[0] ) + zero_delta[2] * np.cos( r[0] )

        # y-axis
        zero_delta = newxyz.copy()
        newxyz[0] =   zero_delta[0] * np.cos( r[1] ) + zero_delta[2] * np.sin( r[1] )
        newxyz[2] = - zero_delta[0] * np.sin( r[1] ) + zero_delta[2] * np.cos( r[1] )

        # z-axis
        zero_delta = newxyz.copy()
        newxyz[0] =   zero_delta[0] * np.cos( r[2] ) - zero_delta[1] * np.sin( r[2] )
        newxyz[1] =   zero_delta[0] * np.sin( r[2] ) + zero_delta[1] * np.cos( r[2] )

        x += newxyz

        return Point3D( x )


    def correct_params( self ):
        self.__xyz = self._correct_position( self.__xyz )
        # clear all rotations since this already included
        self._rotate = None


    def write_lights( self, ffile, indent=0 ):
        self._write_indent( ffile, '%s\n' % self.__xyz, indent+1 )
        self._write_indent( ffile, 'color %s\n' % self.__color, indent+1 )


# Spotlight
#
class PovSpotLightBase( PovBasicLightObject ):
    def __init__(self,
                 light_type,
                 xyz,
                 color,
                 point_at,
                 comment=None ):
        PovBasicLightObject.__init__(self, xyz, color)
        self.__point_at = Point3D(point_at)

        self.light_type = light_type
        self.radius     = None
        self.tightness  = None
        self.falloff    = None


    def verify(self):
        PovBasicLightObject.verify(self)
        self._is_number(self.radius)
        self._is_number(self.tightness)
        self._is_number(self.falloff)


    def correct_params( self ):
        PovBasicLightObject.correct_params( self )
        self.__point_at = self._correct_position( self.__point_at )


    def write_lights( self, ffile, indent=0 ):
        self.verify()

        PovBasicLightObject.write_lights( self, ffile, indent )

        self._write_indent( ffile, '%s\n' % self.light_type, indent+1 )

        self._write_indent( ffile, 'point_at %s\n' % self.__point_at, indent+1 )

        if self.radius is not None:
            self._write_indent( ffile, 'radius %f\n' % self.radius, indent+1 )
        if self.tightness is not None:
            self._write_indent( ffile, 'tightness %f\n' % self.tightness, indent+1 )
        if self.falloff is not None:
            self._write_indent( ffile, 'falloff %f\n' % self.falloff, indent+1 )


class PovSpotLight(PovSpotLightBase):
    def __init__(self,
                 xyz,
                 color,
                 point_at,
                 comment=None ):
        PovSpotLightBase.__init__(self, 'spotlight', xyz, color,
                                    point_at, comment=comment)


class PovCylinderLight( PovSpotLightBase ):
    def __init__( self,
                  xyz,
                  color,
                  point_at,
                  comment=None ):
        PovSpotLightBase.__init__( 'cylinder', xyz, color,
                                    point_at, comment=comment )



class PovAreaLight(PovBasicLightObject):
    def __init__(self,
                 xyz,
                 color,
                 axis1,
                 axis2,
                 dim1,
                 dim2,
                 comment=None ):
        PovBasicLightObject.__init__(self, xyz, color)

        self._axis1 = Point3D(axis1)
        self._axis2 = Point3D(axis2)
        self._dim1  = dim1
        self._dim2  = dim2

        self.adaptive  = 1
        self.jitter    = False


    def verify(self):
        PovBasicLightObject.verify(self)
        self._is_number(self.adaptive)


    def write_lights( self, ffile, indent=0 ):
        self.verify()

        PovBasicLightObject.write_lights( self, ffile, indent )

        self._write_indent(ffile, 'area_light %s, %s, %s, %s\n' % (self._axis1,
                                                                 self._axis2,
                                                                 self._dim1,
                                                                 self._dim2 ), indent+1)
        self._write_indent(ffile, 'adaptive %s\n' % self.adaptive, indent+1 )
        if self.jitter:
            self._write_indent(ffile, 'jitter\n', indent+1 )
