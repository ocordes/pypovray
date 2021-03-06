# pypovobjects.py

# wirtten by: Oliver Cordes 2015-02-27
# changed by: Oliver Cordes 2020-02-12

import sys, os

try:
    import numpy as np
except:
    print( 'Please install numpy to use with pypovobjects.py!' )
    sys.exit( 1 )


from pypovlib.pypovbase import *
from pypovlib.pypovtextures import *
from pypovlib.pypovconfig import *

# constants

__libname__ = 'pypovlib'
__version__ = '0.1.22'
__author__ =  'Oliver Cordes (C) 2015-2020'


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
    ffile.write( '// this file is generated\n// from %s V%s written by %s\n\n' % ( __libname__,
                                                                                    __version__,
                                                                                    __author__ ) )


def _write_postfix_file( ffile ):
    ffile.write( '\n// end of generated file\n' )


def _copy_file( ffile, filename, comment ):
    with open( filename, 'r' ) as f:
        ffile.write( '// %s %s\n' % ( comment, filename ) )
        for line in f:
            ffile.write( line )


# objects



class PovObject(PovBasicObject):
    _name = 'PovObject'
    def __init__(self, comment=None):
        PovBasicObject.__init__(self, comment=comment)
        # all objects are active by default
        self.hidden  = False


        self._texture = None
        self._photons = None

        self._lights = None

        # variables for collecting external data
        self._global_data = None
        self._image_data  = None

        # timeline Variables
        self.time_abs     = 0.
        self.time_delta   = 0.
        self.frame_number = 0


    def _write_texture(self, ffile, indent=0):
        if self._texture is None: return

        for texture in self._texture:
            if ( isinstance(texture, (PovTexture, PovPigment, PovTextureRaw))):
                texture.write_pov(ffile, indent)
            else:
                self._write_indent(ffile, 'texture{\n', indent)
                self._write_indent(ffile, '%s\n' % texture, indent+1)
                self._write_indent(ffile, '}\n', indent)


    def set_texture(self, texture):
        if self._texture is None:
            self._texture = []
        self._texture.append(texture)


    def set_texture_color(self, color):
        self.set_texture('pigment { color %s }' % color)



    def _write_photons(self, ffile, indent=0):
        if self._photons:
            self._write_indent(ffile, 'photons{\n', indent)
            self._write_indent(ffile, '%s\n' % self._photons, indent+1)
            self._write_indent(ffile, '}\n', indent)


    def set_photons(self, photons):
        self._photons = photons


    def set_lights(self, lights):
        if self._lights is None:
            self._lights = [lights]
        else:
            self._lights.append(lights)


    def write_lights(self, ffile, indent=0):
        if self._lights is not None:
            for l in self._lights:
                l.write_pov(ffile, indent=indent)

    def add_stat_count(self, cat):
        if cat in pypovstatistics.keys():
            pypovstatistics[cat] += 1
        else:
            pypovstatistics[cat] = 1


    def do_statistics(self):
        self.add_stat_count(self._name)


    def update_timeline(self, time_abs, time_delta, fnr):
        self.time_abs     = time_abs
        self.time_delta   = time_delta
        self.frame_number = fnr


    def update_time(self, time_abs):
        pass


    def update_timedelta(self, time_delta):
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
    _name = 'PovCSGObject'
    def __init__( self, comment=None ):
        PovObject.__init__( self, comment=comment )
        self.__rotation_matrix         = None
        self.__rotate_before_translate = True
        self.__pre_commands            = []
        self.reset_attributes()

    """
    reset_attributes

    resets all povray attributes
    """
    def reset_attributes(self):
        self.__macros                  = []
        self.__full_matrix             = []
        self.__rotate                  = []
        self.__translate               = []
        self.__scale                   = []

    """
    move_attributes

    moves all povray attributes from an object to the calling
    object
    """
    def move_attributes(self, obj):
        self.__macros      = obj.__macros
        self.__full_matrix = obj.__full_matrix
        self.__rotate      = obj.__rotate
        self.__translate   = obj.__translate
        self.__scale       = obj.__scale
        obj.reset_attributes()


    @property
    def macros( self ):
        return self.__macros


    @macros.setter
    def macros( self, new_macro ):
        if new_macro is None:
            self.__macros = []
        else:
            self.__macros.append( new_macro )


    @property
    def full_matrix( self ):
        return self.__full_matrix


    @full_matrix.setter
    def full_matrix( self, val ):
        if val is None:
            self.__full_matrix = []
        elif isinstance( val, ( list, tuple ) ):
            l = True
            if len( val ) == 12:   # check if matrices list or
                                   # single matrix
                try:
                    m = Matrix3D(val[0])
                except:
                    l = False

            if l:
                for m in val:
                    self.__full_matrix.append(Matrix3D(m))
            else:
                self.__full_matrix.append(Matrix3D(val))

        else:
            self.__full_matrix.append(Matrix3D(val))


    def full_matrix_list( self, val ):
        if isinstance( val, ( list, tuple ) ):
            for m in val:
                self.__full_matrix.append( convertarray2full_matrix( m ) )


    @property
    def rotate( self ):
        return self.__rotate


    @rotate.setter
    def rotate( self, new_rotate ):
        if new_rotate is None:
            self.__rotate = []
        else:
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
        self.__translate.append(translate)
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
        if len(self.__scale) == 0:
            return []

        # combine all scalings
        sc = None
        for i in self.__scale:
            if sc is None:
                sc = i
            else:
                sc *= i

        return sc


    @scale.setter
    def scale( self, new_scale ):
        self.__scale.append(Point3D(new_scale))


    def set_scale( self, new_scale ):
        deprecated( 'set_scale')
        self.__scale.append(Point3D(new_scale))


    def add_pre_commands( self, new_command ):
        self.__pre_commands.append( new_command )


    def _write_macros( self, ffile, indent=0 ):
        for m in self.__macros:
            self._write_indent( ffile, '{}\n'.format( m ), indent )


    def _write_full_matrix( self, ffile, indent=0 ):
        for m in self.__full_matrix:
            self._write_indent(ffile, 'matrix <{}>\n'.format(m), indent)
            #self._write_indent( ffile,
            #                    'matrix <{},{},{},{},{},{},{},{},{},{},{},{}>\n'.format( *m ),
            #                    indent )


    def _write_scale( self, ffile, indent=0 ):
        if len(self.__scale) == 0: return
        for sc in self.__scale:
            self._write_indent( ffile, 'scale %s\n' % sc, indent )


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


    def _write_pre_commands( self, ffile, indent=0 ):
        for cmd in self.__pre_commands:
            cmd( ffile, indent=indent )


    def _write_attributes(self, ffile, indent=0):
        self._write_macros(ffile, indent=indent)
        self._write_texture(ffile, indent=indent)
        self._write_photons(ffile, indent=indent)
        self._write_pre_commands(ffile, indent=indent)
        self._write_geometrics(ffile, indent=indent)


    def write_pov( self, ffile, indent = 0 ):
        PovObject.write_pov( self, ffile, indent=indent )


class PovCSGBox( PovCSGObject ):
    _name = 'Box'
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
        self._write_attributes( ffile, indent+1 )
        self._write_indent( ffile, '}\n', indent )


class PovCSGBoxCenter( PovCSGBox ):
    _name = 'BoxCenter'
    def __init__( self, xyz, dimension, comment=None ):
        PovCSGObject.__init__( self, comment=comment )
        txyz = Point3D( xyz )
        tdim = Point3D( dimension )

        self._set_coords( txyz - (tdim/2), txyz + (tdim/2) )


class PovCSGSphere( PovCSGObject ):
    _name = 'Sphere'
    def __init__( self, xyz, radius, comment=None ):
        PovCSGObject.__init__( self, comment=comment )
        self._xyz    = Point3D( xyz )
        self._radius = radius


    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'sphere{\n', indent )
        self._write_indent( ffile, '%s, %f\n' % ( self._xyz, self._radius ), indent+1 )
        self._write_attributes( ffile, indent+1 )
        self._write_indent( ffile, '}\n', indent )


class PovCSGCylinder( PovCSGObject ):
    _name = 'Cylinder'
    def __init__( self, xyz1, xyz2, radius, comment=None ):
        PovCSGObject.__init__( self, comment=comment )
        self._xyz1   = Point3D( xyz1 )
        self._xyz2   = Point3D( xyz2 )
        self._radius = radius


    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'cylinder{\n', indent )
        self._write_indent( ffile, '%s %s, %f\n' % ( self._xyz1, self._xyz2, self._radius ), indent+1 )
        self._write_attributes( ffile, indent+1 )
        self._write_indent( ffile, '}\n', indent )


class PovCSGTorus( PovCSGObject ):
    _name = 'Torus'
    def __init__( self, radius_major, radius_minor, comment=None ):
        PovCSGObject.__init__( self, comment=comment )
        self._radius_major = radius_major
        self._radius_minor = radius_minor


    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'torus{\n', indent )
        self._write_indent( ffile, '%f,%f\n' % ( self._radius_major,
                                                 self._radius_minor  ), indent+1 )
        self._write_attributes( ffile, indent+1 )
        self._write_indent( ffile, '}\n', indent )


class PovCSGCone( PovCSGObject ):
    _name = 'Cone'
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
        self._write_attributes( ffile, indent+1 )
        self._write_indent( ffile, '}\n', indent )


class PovCSGPrism( PovCSGObject ):
    _name = 'Prism'
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
            i = self._points[0]
            ffile.write( ',\n' )
            self._write_indent( ffile, '<%f,%f>' % ( i[0], i[1] ), indent+1 )
        ffile.write( '\n' )
        self._write_attributes( ffile, indent+1 )
        self._write_indent( ffile, '}\n', indent )


class PovCSGMacro( PovCSGObject ):
    _name = 'Macro'
    def __init__( self, comment=None, macrocmd=None ):
        PovCSGObject.__init__( self, comment=comment )
        self._macrocmd = macrocmd


    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'object{\n', indent )
        self._write_indent( ffile, '%s\n' % self._macrocmd, indent+1 )
        self._write_attributes( ffile, indent+1 )
        self._write_indent( ffile, '}\n', indent )


class PovDisc( PovCSGObject ):
    _name = 'Dics'
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


class PovSkySphere( PovCSGObject ):
    _name = 'SkySphere'
    def __init__( self, comment=None ):
        PovCSGObject.__init__( self, comment=comment )


    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'sky_sphere{\n', indent )
        self._write_attributes( ffile, indent+1 )
        self._write_indent( ffile, '}\n', indent )


# list classes

class PovBaseList( object ):
    def __init__( self ):
        self._items       = []

        self._includes    = []
        self._declares    = {}
        self._macro_def   = []
        self._extra_files = []


    # handle includes/declares
    def add_include( self, incfile ):
        if incfile is None: return

        if isinstance(incfile, (tuple, list)) == True:
            for i in incfile:
                self.add_include(i)
        else:
            if incfile in self._includes:
                pass
            else:
                self._includes.append(incfile)


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


    def add_extra_file(self, efile):
        if (isinstance(efile, (tuple, list)) == True):
            for i in efile:
                self.add_extra_file(i)
        else:
            if os.access(efile, os.R_OK):
                if efile not in self._extra_files:
                    self._extra_files.append(efile)
            else:
                print('WARNING: File \'%s\' not found!' % efile)



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


    def collect_extra_files(self):
        extra_files = self._extra_files

        for i in self._items:
            if hasattr(i, 'collect_extra_files'):
                efiles = i.collect_extra_files()
            elif hasattr(i, '_extra_files'):
                efiles = i._extra_files
            else:
                efiles = []

            for i in efiles:
                if i not in extra_files:
                    extra_files.append(i)

        return extra_files


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


# generator Object for Lists and PovObjects

class PovCSGObjectList( PovBaseList, PovCSGObject ):
    _name = 'PovCSGObjectList'
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


    def _write_items(self, ffile, indent=0):
        nr = 1
        for i in self._items:
            if i.hidden == False:
                self._write_indent(ffile,
                                   '// %s Item #%i\n' % (self._name, nr),
                                   indent=indent)
                i.write_pov(ffile, indent=indent)
            nr += 1


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


    def do_statistics( self ):
        PovBaseList.do_statistics(self)
        PovCSGObject.do_statistics(self)


class PovCSGContainer( PovCSGObjectList ):
    _name = 'Container'
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


class PovCSGUnion(PovCSGObjectList):
    _name = 'Union'
    def __init__(self, comment=None, split_union=False):
        PovCSGObjectList.__init__(self, comment=comment)

        self._split_union = split_union


    def set_split_union(self, split_union):
        self._split_union = split_union


    def write_pov(self, ffile, indent = 0):
        if len(self._items) == 0:
            print('Union structure needs at least one item to proceed!')
            #raise TypeError('Union structure needs at least one item to proceed!')
            self._write_indent(ffile, '//empty union\n', indent)
            return
        PovCSGObjectList.write_pov(self, ffile, indent=indent)
        self._write_indent(ffile, 'union{\n', indent)

        self._write_items(ffile, indent=indent+1)
        self._write_attributes(ffile, indent+1)

        if not self._split_union:
            self._write_indent(ffile, 'split_union off\n', indent+1)

        self._write_indent(ffile, '}\n', indent)


class PovCSGMerge( PovCSGObjectList ):
    _name = 'Merge'
    def __init__(self, comment=None):
        PovCSGObjectList.__init__(self, comment=comment)

    def write_pov(self, ffile, indent = 0):
        if len(self._items) == 0:
            raise TypeError('Merge structure needs at least one item to proceed!')
        PovCSGObjectList.write_pov(self, ffile, indent=indent)
        self._write_indent(ffile, 'merge{\n', indent)

        self._write_items(ffile, indent=indent+1)
        self._write_attributes(ffile, indent+1)
        self._write_indent(ffile, '}\n', indent)


class PovCSGDifference( PovCSGObjectList ):
    _name = 'Difference'
    def __init__( self, comment=None ):
        PovCSGObjectList.__init__( self, comment=comment )


    def write_pov( self, ffile, indent = 0 ):
        if len(  self._items ) > 2:
            raise TypeError( 'Difference structure can have max 2 itemms to proceed!' )
        PovCSGObjectList.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'difference{\n', indent )

        self._write_items(ffile, indent=indent+1)
        self._write_attributes( ffile, indent+1 )
        self._write_indent( ffile, '}\n', indent )


# height fields
class PovHeightField( PovCSGObject ):
    _name = 'HeightField'
    def __init__( self, image_name, smooth=False, comment=None):
        PovCSGObject.__init__( self,comment=comment )
        self._image_name = image_name
        self._smooth     = smooth
        self.add_extra_file(self._image_name)


    def write_pov( self, ffile, indent = 0 ):
        PovCSGObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'height_field{\n', indent )
        self._write_indent( ffile, '"%s"\n' % self._image_name, indent+1 )
        if ( self._smooth ):
            self._write_indent( ffile, 'smooth\n', indent+1 )

        self._write_attributes( ffile, indent+1 )
        self._write_indent( ffile, '}\n', indent )


# mesh2 objects
class PovMesh2(PovCSGObject):
    _name = 'Mesh2'
    def __init__(self, vertex_vectors=None,
                       normal_vectors=None,
                       uv_vectors=None,
                       face_indices=None,
                       normal_indices=None,
                       uv_indices=None,
                       comment=None
                        ):
        PovCSGObject.__init__(self, comment=comment)
        self.vertex_vectors = vertex_vectors
        self.normal_vectors = normal_vectors
        self.uv_vectors = uv_vectors
        self.face_indices = face_indices
        self.normal_indices = normal_indices
        self.uv_indices = uv_indices


    def _write_vector_list_int(self, ffile, vlist, indent):
        self._write_indent(ffile, '%i,\n' % vlist.shape[0], indent)
        for i in vlist[:-1]:
            self._write_indent(ffile, '<%i,%i,%i>,\n' % (i[0], i[1], i[2]), indent)
        i = vlist[-1]
        self._write_indent(ffile, '<%i,%i,%i>\n' % (i[0], i[1], i[2]), indent)


    def _write_vector_list_float(self, ffile, vlist, indent):
        self._write_indent(ffile, '%i,\n' % vlist.shape[0], indent)
        for i in vlist[:-1]:
            self._write_indent(ffile, '<%f,%f,%f>,\n' % (i[0], i[1], i[2]), indent)
        i = vlist[-1]
        self._write_indent(ffile, '<%f,%f,%f>\n' % (i[0], i[1], i[2]), indent)


    def write_pov(self, ffile, indent=0):
        PovCSGObject.write_pov(self, ffile, indent)
        self._write_indent(ffile, 'mesh2{\n', indent)
        if self.vertex_vectors is not None:
            self._write_indent(ffile, 'vertex_vectors\n', indent+1)
            self._write_indent(ffile, '{\n', indent+1)
            self._write_vector_list_float(ffile, self.vertex_vectors, indent+2)
            self._write_indent(ffile, '}\n', indent+1)

        if self.normal_vectors is not None:
            self._write_indent(ffile, 'normal_vectors\n', indent+1)
            self._write_indent(ffile, '{\n', indent+1)
            self._write_vector_list_float(ffile, self.normal_vectors, indent+2)
            self._write_indent(ffile, '}\n', indent+1)

        if self.uv_vectors is not None:
            self._write_indent(ffile, 'uv_vectors\n', indent+1)
            self._write_indent(ffile, '{\n', indent+1)
            self._write_vector_list_float(ffile, self.normal_vectors, indent+2)
            self._write_indent(ffile, '}\n', indent+1)

        if self.face_indices is not None:
            self._write_indent(ffile, 'face_indices\n', indent+1)
            self._write_indent(ffile, '{\n', indent+1)
            self._write_vector_list_int(ffile, self.face_indices, indent+2)
            self._write_indent(ffile, '}\n', indent+1)


        self._write_attributes(ffile, indent+1)
        self._write_indent(ffile, '}\n', indent)


# mesh2 objects
class PovTriangle(PovCSGObject):
    _name = 'Triangle'
    def __init__(self, vertex_vectors=None,
                       comment=None
                        ):
        PovCSGObject.__init__(self, comment=comment)
        if isinstance(vertex_vectors, (list, tuple)) and len(vertex_vectors) == 3:
            self.vertex_vectors = vertex_vectors
        else:
            print('Ignoring wrong triangle vertices!')



    def _write_vector_list_float(self, ffile, vlist, indent):
        for i in vlist[:-1]:
            self._write_indent(ffile, '<%f,%f,%f>,\n' % (i[0], i[1], i[2]), indent)
        i = vlist[-1]
        self._write_indent(ffile, '<%f,%f,%f>\n' % (i[0], i[1], i[2]), indent)


    def write_pov(self, ffile, indent=0):
        if self.vertex_vectors:
            PovCSGObject.write_pov(self, ffile, indent)
            self._write_indent(ffile, 'triangle{\n', indent)
            self._write_vector_list_float(ffile, self.vertex_vectors, indent+1)

            self._write_attributes(ffile, indent+1)
            self._write_indent(ffile, '}\n', indent)


# a simple PovFile generator

class PovFile( PovBaseList ):
    def __init__( self, filename = None, verbose = False, camera_optimize = False ):
        PovBaseList.__init__( self )
        self._filename = filename

        self._camera       = None
        self._lights       = None

        self._prefix_file  = None
        self._postfix_file = None

        self.extra_files   = None
        self.settings      = GlobalSettings()

        self._version      = '3.7'


    def set_version(self, version):
        self._version = version


    def config_size(self, width, height):
        self._width = width
        self._height = height


    def config_povray_args(self, povray_args):
        self._povray_args = povray_args


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


    def collect_extra_files(self):
        extra_files = PovBaseList.collect_extra_files(self)

        return extra_files


    # generate povfile
    def write_povfile(self, filename = None, submit=True):
        if filename != None:
            self.set_filename( filename )

        f = open(  self._filename, 'w' )
        _write_prefix_file( f )

        f.write('// set the povray version for this file\n')
        f.write('#version %s;\n\n' % self._version)

        # global settings pre part
        self.settings.write_pov_pre(f)

        if self._prefix_file is not None:
            _copy_file( f, self._prefix_file, 'PovPreFile' )


        # global settings mid part
        self.settings.write_pov_mid(f)

        # collect declares
        declares = self.collect_declares()


        # collect includes
        includes = self.collect_includes()    # these are normal object includes

        # collect macros
        macro_defs = self.collect_macro_defs()

        # collect extra files
        self.extra_files = self.collect_extra_files()


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
            if i.hidden == False:
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


        # global settings post part
        self.settings.write_pov_post(f)

        if ( self._postfix_file is not None ):
            _copy_file( f, self._postfix_file, 'PovPostFile' )

        f.close()
