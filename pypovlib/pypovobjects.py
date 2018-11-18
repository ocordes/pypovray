# pypovobjects.py

# wirtten by: Oliver Cordes 2015-02-27
# changed by: Oliver Cordes 2018-11-01

import sys, os

try:
    import numpy as np
except:
    print( 'Please install numpy to use with pypovobjects.py!' )
    sys.exit( 1 )


from pypovlib.pypovbase import *
from pypovlib.pypovtextures import *

# constants

__libname = 'pypovlib'
__version = '0.1.10'
__author =  'Oliver Cordes (C) 2015-2018'


# variables
pypovstatistics = {}


# open variables
norm_x  = np.array( [1.,0.,0.] )
norm_y  = np.array( [0.,1.,0.] )
norm_z  = np.array( [0.,0.,1.] )
norm_xy = np.array( [1.,1.,0.] )
norm_xz = np.array( [1.,0.,1.] )
norm_yz = np.array( [0.,1.,1.] )


# helper funtions

def deprecated( s ):
    print( 'warning: Use of %s is deprecated!' % s )


def print_statistics():
    print( 'Statistics:' )
    total = 0
    for i in pypovstatistics:
        print( ' %-12s: %i' % ( i, pypovstatistics[i] ) )
        total += pypovstatistics[i]
    print( '-------------------------------------' )
    print( 'Total        : %i POVRay objects' % total )
    print( '' )

def reset_statistics():
    pypovstatistics = {}


def _write_prefix_file( ffile ):
    ffile.write( '// this file is generated\n// from %s V%s written by %s\n\n' % ( __libname,
                                                                                    __version,
                                                                                    __author ) )


def _write_postfix_file( ffile ):
    ffile.write( '\n// end of generated file\n' )


def _copy_file( ffile, filename, comment ):
    with open( filename, 'r' ) as f:
        ffile.write( '// %s %s\n' % ( comment, filename ) )
        for line in f:
            ffile.write( line )


# objects



class PovObject( PovBasicObject ):
    def __init__( self, comment=None ):
        PovBasicObject.__init__( self, comment=comment )
        self._texture = None

        self._lights = None

        # variables for collecting external data
        self._global_data = None
        self._image_data  = None

        # timeline Variables
        self.time_abs     = 0.
        self.time_delta   = 0.
        self.frame_number = 0


    def _write_texture( self, ffile, indent=0 ):
        if self._texture is None: return

        for texture in self._texture:
            if ( isinstance( texture, PovTexture ) ) or ( isinstance( texture, PovPigment ) ):
                self._texture.write_pov( ffile, indent )
            else:
                self._write_indent( ffile, 'texture{\n', indent )
                self._write_indent( ffile, '%s\n' % texture, indent+1 )
                self._write_indent( ffile, '}\n', indent )


    def set_texture( self, texture ):
        if self._texture is None:
            self._texture = []
        self._texture.append( texture )


    def set_texture_color( self, color ):
        self.set_texture( 'pigment { color %s }' % color )


    def set_lights( self, lights ):
        if ( self._lights is None ):
            self._lights = [ lights ]
        else:
            self._lights.append( lights )

    def write_lights( self, ffile, indent=0 ):
        if ( self._lights is not None):
            for l in self._lights:
                l.write_pov( ffile, indent=indent )

    def add_stat_count( self, cat ):
        if cat in pypovstatistics.keys():
            pypovstatistics[cat] += 1
        else:
            pypovstatistics[cat] = 1

    def do_statistics( self ):
        pass


    def update_timeline( self, time_abs, time_delta, fnr ):
        self.time_abs     = time_abs
        self.time_delta   = time_delta
        self.frame_number = fnr

    def update_time( self, time_abs ):
        pass

    def update_timedelta( self, time_delta ):
        pass

    def update_frame( self, framenr ):
        pass


    def add_global_data( self, filename ):
        if ( isinstance( filename, list ) == True ) or  ( isinstance( filename, tuple ) == True ):
            for i in filename:
                self.add_global_data( i )
        else:
            if ( os.access( filename, os.R_OK ) == False ):
                print( 'WARNING: file \'%f\' is not accessable! Ignore this file!' % filename )
            else:
                if self._global_data is None:
                    self._global_data = []
                self._global_data.append( filename )


    def add_image_data( self, filename ):
        if ( isinstance( filename, list ) == True ) or  ( isinstance( filename, tuple ) == True ):
            for i in filename:
                self.add_image_data( i )
        else:
            if ( os.access( filename, os.R_OK ) == False ):
                print( 'WARNING: file \'%f\' is not accessable! Ignore this file!' % filename )
            else:
                if self._image_data is None:
                    self._image_data = []
                self._image_data.append( filename )



class PovCSGObject( PovObject ):
    def __init__( self, comment=None ):
        PovObject.__init__( self, comment=comment )
        self.__macros                  = []
        self.__full_matrix             = []
        self.__rotate                  = []
        self.__rotation_matrix         = None
        self.__translate               = None
        self.__scale                   = None
        self.__rotate_before_translate = True


    @property
    def macros( self ):
        return self.__macros


    @macros.setter
    def macros( self, new_macro ):
        self.__macros.append( new_macro )


    @property
    def full_matrix( self ):
        return self.__full_matrix


    @full_matrix.setter
    def full_matrix( self, val ):
        self.__full_matrix.append( convertarray2full_matrix( val ) )


    @property
    def rotate( self ):
        return self.__rotate


    @rotate.setter
    def rotate( self, new_rotate ):
        rotate = Point3D( new_rotate )
        self.__rotate.append( rotate )

        if ( self._lights is not None):
            # do the rotation also for bounded light objects
            for l in self._lights:
                if l.bound_object:
                    l.rotate = rotate


    def set_rotate( self, new_rotate ):
        deprecated( 'set_rotate' )
        rotate = Point3D( new_rotate )
        self.__rotate.append( rotate )

        if ( self._lights is not None):
            # do the rotation also for bounded light objects
            for l in self._lights:
                if l.bound_object:
                    l.set_rotate( rotate )


    def set_rotation_matrix( self, new_matrix ):
        self.__rotation_matrix = convertarray2matrix( new_matrix )
        if ( self._lights is not None):
            # do the rotation also for bounded light objects
            for l in self._lights:
                if l.bound_object:
                    l.set_rotation_matrix( self.__rotate )


    def set_translate( self, new_translate ):
        deprecated( 'set_translate' )
        translate = Point3D( new_translate )
        self.__translate = [ translate ]

        if ( self._lights is not None):
            # do the translation also for bounded light objects
            for l in self._lights:
                if l.bound_object:
                    l.set_translate( translate )


    @property
    def translate( self ):
        t = Point3D( [ 0., 0., 0.] )
        for i in self.__translate:
            t += i

        return t


    @translate.setter
    def translate( self, val ):
        translate = Point3D( val )
        self.__translate = [ translate ]
        if ( self._lights is not None ):
            # do the translation also for bounded light objects
            for l in self._lights:
                if l.bound_object:
                    l.translate = translate


    def get_translate( self ):
        deprecated( 'get_translate')
        t = Point3D( [ 0., 0., 0.] )
        for i in self.__translate:
            t += i

        return t


    def delta_translate( self, xyz ):
        dxyz = Point3D( xyz )
        if ( self.__translate is None ):
            self.__translate = [ dxyz ]
        else:
            self.__translate.append( dxyz )

        if ( self._lights is not None):
            # do the translation also for bounded light objects
            for l in self._lights:
                if l.bound_object:
                    l.delta_translate( dxyz )


    def set_rotate_before_translate( self, val ):
        self.__rotate_before_translate = val


    @property
    def scale( self ):
        return self._scale


    @scale.setter
    def scale( self, new_scale ):
        self.__scale = Point3D( new_scale )


    def set_scale( self, new_scale ):
        deprecated( 'set_scale')
        self.__scale = Point3D( new_scale )


    def _write_macros( self, ffile, indent=0 ):
        for m in self.__macros:
            self._write_indent( ffile, '{}\n'.format( m ), indent )


    def _write_full_matrix( self, ffile, indent=0 ):
        for m in self.__full_matrix:
            self._write_indent( ffile,
                                'matrix <{},{},{},{},{},{},{},{},{},{},{},{}>\n'.format( *m ),
                                indent )


    def _write_scale( self, ffile, indent=0 ):
        if self.__scale is None: return
        self._write_indent( ffile, 'scale %s\n' % self.__scale, indent )


    def _write_translate( self, ffile, indent=0 ):
        if self.__translate is None: return
        for t in self.__translate:
           self._write_indent( ffile, 'translate %s\n' % t, indent )


    def _write_rotate( self, ffile, indent=0 ):
        for r in self.__rotate:
           self._write_indent( ffile, 'rotate %s\n' % r, indent )

    def _write_rotation_matrix( self, ffile, indent=0 ):
        if self.__rotation_matrix is None: return
        self._write_indent( ffile,
             'matrix <%f,%f,%f,%f,%f,%f,%f,%f,%f,0,0,0>\n' % ( self.__rotation_matrix[0][0],
                                                               self.__rotation_matrix[0][1],
                                                               self.__rotation_matrix[0][2],
                                                               self.__rotation_matrix[1][0],
                                                               self.__rotation_matrix[1][1],
                                                               self.__rotation_matrix[1][2],
                                                               self.__rotation_matrix[2][0],
                                                               self.__rotation_matrix[2][1],
                                                               self.__rotation_matrix[2][2] ),
                                                               indent )


    def _write_geometrics( self, ffile, indent=0 ):
        self._write_full_matrix( ffile, indent=indent )
        self._write_scale( ffile, indent=indent )
        if self.__rotate_before_translate:
            self._write_rotate( ffile, indent=indent )
            self._write_rotation_matrix( ffile, indent=indent )
            self._write_translate( ffile, indent=indent )
        else:
            self._write_translate( ffile, indent=indent )
            self._write_rotate( ffile, indent=indent )
            self._write_rotation_matrix( ffile, indent=indent )


    def write_pov( self, ffile, indent = 0 ):
        PovObject.write_pov( self, ffile, indent=indent )


class PovCSGBox( PovCSGObject ):
    def __init__( self, xyz1, xyz2, comment=None):
        PovCSGObject.__init__( self,comment=comment )
        self._set_coords( Point3D( xyz1 ), Point3D( xyz2 ) )


    def _set_coords( self, xyz1, xyz2 ):
        self._xyz1 = xyz1
        self._xyz2 = xyz2

    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'box{\n', indent )
        self._write_indent( ffile, '%s %s\n' % ( self._xyz1, self._xyz2 ), indent+1 )
        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )

    def do_statistics( self ):
        self.add_stat_count( 'Box' )


class PovCSGBoxCenter( PovCSGBox ):
    def __init__( self, xyz, dimension, comment=None ):
        PovCSGObject.__init__( self, comment=comment )
        txyz = Point3D( xyz )
        tdim = Point3D( dimension )

        self._set_coords( txyz - (tdim/2), txyz + (tdim/2) )


class PovCSGSphere( PovCSGObject ):
    def __init__( self, xyz, radius, comment=None ):
        PovCSGObject.__init__( self, comment=comment )
        self._xyz    = Point3D( xyz )
        self._radius = radius

    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'sphere{\n', indent )
        self._write_indent( ffile, '%s, %f\n' % ( self._xyz, self._radius ), indent+1 )
        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )

    def do_statistics( self ):
        self.add_stat_count( 'Sphere' )


class PovCSGCylinder( PovCSGObject ):
    def __init__( self, xyz1, xyz2, radius, comment=None ):
        PovCSGObject.__init__( self, comment=comment )
        self._xyz1   = Point3D( xyz1 )
        self._xyz2   = Point3D( xyz2 )
        self._radius = radius

    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'cylinder{\n', indent )
        self._write_indent( ffile, '%s %s, %f\n' % ( self._xyz1, self._xyz2, self._radius ), indent+1 )
        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )

    def do_statistics( self ):
        self.add_stat_count( 'Cylinder' )


class PovCSGTorus( PovCSGObject ):
    def __init__( self, radius_major, radius_minor, comment=None ):
        PovCSGObject.__init__( self, comment=comment )
        self._radius_major = radius_major
        self._radius_minor = radius_minor

    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'torus{\n', indent )
        self._write_indent( ffile, '%f,%f\n' % ( self._radius_major,
                                                 self._radius_minor  ), indent+1 )
        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )

    def do_statistics( self ):
        self.add_stat_count( 'Torus' )


class PovCSGCone( PovCSGObject ):
    def __init__( self, xyz1, radius1, xyz2, radius2, comment=None ):
        PovCSGObject.__init__( self, comment=comment )
        self._xyz1   = Point3D( xyz1 )
        self._xyz2   = Point3D( xyz2 )
        self._radius1 = radius1
        self._radius2 = radius2

    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'cone{\n', indent )
        self._write_indent( ffile, '%s,%f,%s,%f\n' % ( self._xyz1,
                                                    self._radius1,
                                                    self._xyz2,
                                                    self._radius2 ), indent +1 )
        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )

    def do_statistics( self ):
        self.add_stat_count( 'Cone' )


class PovCSGPrism( PovCSGObject ):
    def __init__( self, y1, y2, points, comment=None, closing_point = False ):
        PovCSGObject.__init__( self, comment=comment )
        self._y1            = y1
        self._y2            = y2
        self._points        = points
        self._verify()
        self._closing_point = closing_point

    def _verify( self ):
        if ( isinstance( self._points, (list,tuple) ) == False ):
            raise TypeError( 'points must be given as list or tuple!' )
        for i in self._points:
            if isinstance( i, (list,tuple) ):
                if ( len( i ) != 2 ):
                    raise TypeError( 'individual points must have 2 components' )
            else:
                raise TypeError( 'individual points must be given as list or tuple!' )

    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'prism{\n', indent )
        l = len( self._points )
        if self._closing_point == False:
            l += 1
        self._write_indent( ffile, '%f, %f, %i\n' % ( self._y1,
                                                      self._y2,
                                                      l ),
                                                      indent+1 )
        first = True
        for i in self._points:
            if ( first == False ):
                ffile.write( ',\n' )
            else:
                first = False
            self._write_indent( ffile, '<%f,%f>' % ( i[0], i[1] ), indent+1 )

        if self._closing_point == False:
            ffile.write( ',\n' )
            self._write_indent( ffile, '<%f,%f>' % ( i[0], i[1] ), indent+1 )
        ffile.write( '\n' )
        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )

    def do_statistics( self ):
        self.add_stat_count( 'Prism' )


class PovCSGMacro( PovCSGObject ):
    def __init__( self, comment=None, macrocmd=None ):
        PovCSGObject.__init__( self, comment=comment )
        self._macrocmd = macrocmd

    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'object{\n', indent )
        self._write_indent( ffile, '%s\n' % self._macrocmd, indent+1 )
        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )

    def do_statistics( self ):
        self.add_stat_count( 'Macro' )


class PovDisc( PovCSGObject ):
    def __init__( self, xyz, normal, radius, hole_radius=None, comment=None ):
        PovCSGObject.__init__( self, comment=comment )
        self._xyz         = Point3D( xyz )
        self._normal      = Point3D( normal )
        self._radius      = radius
        self._hole_radius = hole_radius


    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'disc{\n', indent )
        if self._hole_radius is None:
            hole_radius = ''
        else:
            hole_radius = ', %f' % ( self._hole_radius )
        self._write_indent( ffile, '%s, %s, %f %s' % ( self._xyz ,
                                                       self._normal,
                                                       self._radius,
                                                       hole_radius ),
                                                       indent+1 )
        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_indent( ffile, '}\n', indent )

    def do_statistics( self ):
        self.add_stat_count( 'Disc' )


class PovSkySphere( PovCSGObject ):
    def __init__( self, comment=None ):
        PovCSGObject.__init__( self, comment=comment )

    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'sky_sphere{\n', indent )
        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )


# list classes

class PovBaseList( object ):
    def __init__( self ):
        self._items = []

        self._includes  = []
        self._declares  = {}
        self._macro_def = []


    # handle includes/declares
    def add_include( self, incfile ):
        if incfile is None: return

        if not incfile in self._includes:
            self._includes.append( incfile )


    def add_declare( self, key, value ):
        if key in self._declares.keys():
            raise KeyError( 'key %s already in declares!' % key )
        else:
            self._declares[key] = value


    def add_macro( self, macrodef ):
        if ( isinstance( macrodef, ( tuple, list ) ) == True ):
            for i in macrodef:
                self.add_macro( i )
        else:
            self._macro_def.append( macrodef )


    def collect_includes( self ):
        includes = self._includes
        for i in self._items:
            if hasattr( i, 'collect_includes' ):
                incl = i.collect_includes()
            elif hasattr( i, '_includes' ):
                incl = i._includes
            else:
                incl = []

            for i in incl:
                if i not in includes:
                    includes.append( i )

        return includes


    def collect_declares( self ):
        declares = self._declares
        for i in self._items:
            if hasattr( i, 'collect_declares' ):
                decl = i.collect_declares()
            elif hasattr( i, '_declares' ):
                decl = i._declares
            else:
                decl = {}

            if len( decl ) > 0:
                for i,j in decl.items():
                    if i in declares.keys():
                        #raise KeyError( 'key %s already in declares!' % i )
                        pass
                    else:
                        declares[i] = j

        return declares


    def collect_macro_defs( self ):
        macro_defs = self._macro_def
        for i in self._items:
            if hasattr( i, 'collect_macro_defs' ):
                mdefs = i.collect_macro_defs()
            elif hasattr( i, '_macro_def' ):
                mdefs = i._macro_def
            else:
                mdefs = []

            for i in mdefs:
                if i not in macro_defs:
                    macro_defs.append( i )

        return macro_defs


    def _verify_object( self, val ):
        if val is None:
            print( '_verify_object: Ignore this None type object!' )
            return False
        else:
            return True

    def add( self, new_obj ):
        if ( isinstance( new_obj, list ) == True ) or  ( isinstance( new_obj, tuple ) == True ):
            for i in new_obj:
                self.add( i )
        else:
            if self._verify_object( new_obj ) == True:
                self._items.append( new_obj )

    def do_statistics( self ):
        for i in self._items:
            i.do_statistics()


# generator Object for Lists and PovObhects

class PovObjectList( PovBaseList, PovObject ):
    def __init__( self, comment=None ):
        PovBaseList.__init__( self )
        PovObject.__init__( self, comment=comment )

    def _verify_object( self, new_obj ):
        if isinstance( new_obj, PovObject ) == False:
            raise TypeError( 'new_obj must be PovObject or a derivative of PovObject' )
        return True


class PovCSGObjectList( PovBaseList, PovCSGObject ):
    _D = 0.001
    def __init__( self, comment=None ):
        PovBaseList.__init__( self )
        PovCSGObject.__init__( self, comment=comment )

    def _verify_object( self, new_obj ):
        if isinstance( new_obj, PovCSGObject ) == False:
            raise TypeError( 'new_obj must be PovObject or a derivative of PovCSGObject' )
        return True

    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )


    def write_lights( self, ffile, indent=0 ):
        # write own light definitions
        PovCSGObject.write_lights( self, ffile, indent=indent )
        # write recursive all definitions of the subobjects
        for i in self._items:
            i.write_lights( ffile, indent=indent )

    # animation handling
    def update_time( self, time_abs ):
        for i in self._items:
            i.update_time( time_abs )


    def update_timedelta( self, time_delta ):
        for i in self._items:
            i.update_timedelta( time_delta )


    def update_frame( self, framenr ):
        for i in self._items:
            i.update_frame( framenr )


class PovCSGContainer( PovCSGObjectList ):
    def __init__( self, comment=None ):
        PovCSGObjectList.__init__( self, comment=comment )

    def write_pov( self, ffile, indent = 0 ):
        PovCSGObjectList.write_pov( self, ffile, indent=indent )

        nr = 1
        for i in self._items:
            self._write_indent( ffile,
                                '// Container Item #%i\n' % nr,
                                indent=indent )
            i.write_pov( ffile, indent=indent )
            nr += 1


    def do_statistics( self ):
        PovBaseList.do_statistics( self )
        self.add_stat_count( 'Container' )


class PovCSGUnion( PovCSGObjectList ):
    def __init__( self, comment=None ):
        PovCSGObjectList.__init__( self, comment=comment )

    def write_pov( self, ffile, indent = 0 ):
        if len(  self._items ) == 0:
            raise TypeError( 'Union structure needs at least one item to proceed!' )
        PovCSGObjectList.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'union{\n', indent )

        nr = 1
        for i in self._items:
            self._write_indent( ffile,
                                '// Union Item #%i\n' % nr,
                                indent=indent+1 )
            i.write_pov( ffile, indent=indent+1 )
            nr += 1

        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )

    def do_statistics( self ):
        PovBaseList.do_statistics( self )
        self.add_stat_count( 'Union' )


class PovCSGMerge( PovCSGObjectList ):
    def __init__( self, comment=None ):
        PovCSGObjectList.__init__( self, comment=comment )

    def write_pov( self, ffile, indent = 0 ):
        if len(  self._items ) == 0:
            raise TypeError( 'Merge structure needs at least one item to proceed!' )
        PovCSGObjectList.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'merge{\n', indent )

        nr = 1
        for i in self._items:
            self._write_indent( ffile,
                                '// Merge Item #%i\n' % nr,
                                indent=indent+1 )
            i.write_pov( ffile, indent=indent+1 )
            nr += 1

        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )

    def do_statistics( self ):
        PovBaseList.do_statistics( self )
        self.add_stat_count( 'Merge' )


class PovCSGDifference( PovCSGObjectList ):
    def __init__( self, comment=None ):
        PovCSGObjectList.__init__( self, comment=comment )


    def write_pov( self, ffile, indent = 0 ):
        if len(  self._items ) > 2:
            raise TypeError( 'Difference structure can have max 2 itemms to proceed!' )
        PovCSGObjectList.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'difference{\n', indent )

        nr = 1
        for i in self._items:
            self._write_indent( ffile,
                                '// Difference Item #%i\n' % nr,
                                indent=indent+1 )
            i.write_pov( ffile, indent=indent+1 )
            nr += 1

        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )

    def do_statistics( self ):
        PovBaseList.do_statistics( self )
        self.add_stat_count( 'Difference' )


# height fields
class PovHeightField( PovCSGObject ):
    def __init__( self, image_name, smooth=False, comment=None):
        PovCSGObject.__init__( self,comment=comment )
        self._image_name = image_name
        self._smooth     = smooth


    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'height_field{\n', indent )
        self._write_indent( ffile, '"%s"\n' % self._image_name, indent+1 )
        if ( self._smooth ):
            self._write_indent( ffile, 'smooth\n', indent+1 )
        self._write_macros( ffile, indent+1 )
        self._write_texture( ffile, indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )

    def do_statistics( self ):
        self.add_stat_count( 'HeightField' )


# a simple PovFile generator

class PovFile( PovBaseList ):
    def __init__( self, filename = None, verbose = False, camera_optimze = False ):
        PovBaseList.__init__( self )
        self._filename = filename

        self._camera       = None
        self._lights       = None

        self._prefix_file  = None
        self._postfix_file = None


    def set_prefix_file( self, filename ):
        self._prefix_file = filename


    def set_postfix_file( self, filename ):
        self._postfix_file = filename


    def set_filename( self, filename ):
        self._filename = filename


    def set_camera( self, camera ):
        self._camera = camera


    def set_lights( self, lights ):
        if ( ( isinstance( lights, tuple ) == True ) or ( isinstance( lights, list ) == True ) ):
            for i in lights:
                self.set_lights( i )
        else:
            if ( self._lights is None ):
                self._lights = [ lights ]
            else:
                self._lights.append( lights )


    def collect_includes( self ):
        incl = PovBaseList.collect_includes( self )

        if self._camera is not None:
            for i in self._camera._includes:
                if i not in incl:
                    incl.append( i )

        return incl


    # generate povfile
    def write_povfile( self, filename = None ):
        if filename != None:
            self.set_filename( filename )

        f = open(  self._filename, 'w' )
        _write_prefix_file( f )

        if self._prefix_file is not None:
            _copy_file( f, self._prefix_file, 'PovPreFile' )


        # collect declares
        declares = self.collect_declares()


        # collect includes
        includes = self.collect_includes()    # these are normal object includes

        # collect macros
        macro_defs = self.collect_macro_defs()

        # check for includes/macro_defs in declare objects
        for key in declares:
            if hasattr( declares[key], 'collect_includes' ):
                incl = declares[key].collect_includes()
                includes += incl

            if hasattr( declares[key], 'collect_macro_defs' ):
                mdefs = declares[key].collect_macro_defs()
                macro_defs += mdefs


        # write includes
        if ( len( includes ) > 0 ):
            for i in includes:
                f.write( '#include "%s"\n' % i )
            f.write( '\n' )


        # write macros
        i = 0

        for macro in macro_defs:
            f.write( '// macro definition #%i' % i)
            f.write( '%s\n\n' % macro )
            i += 1

        # write declares
        for key in declares:
            f.write( '#declare %s = ' % key )
            if hasattr( declares[key], 'write_pov' ):
                declares[key].write_pov( f, indent=0 )
            else:
                f.write( '%s;\n' % ( declares[key] ) )
            #try:
            #    self._declares[key].write_pov( f, indent=0 )
            #except AttributeError:
            #    f.write( '%s;\n' % ( self._declares[key] ) )
        f.write( '\n' )

        # write camera
        if self._camera is None:
            print( 'Warning: No camera defined!' )
        else:
            self._camera.write_pov( f, indent=0 )
            f.write( '\n' )

        # write objects
        for i in self._items:
            i.write_pov( f, indent=0 )
        f.write( '\n' )

        # write ligths

        # global lights
        if self._lights is not None:
            for i in self._lights:
                i.write_pov( f, indent=0 )

        # object related lights
        for i in self._items:
            i.write_lights( f, indent=0 )
        f.write( '\n' )

        _write_postfix_file( f )

        if ( self._postfix_file is not None ):
            _copy_file( f, self._postfix_file, 'PovPostFile' )

        f.close()
