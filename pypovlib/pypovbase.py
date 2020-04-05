# pypovobjects.py

# written by: Oliver Cordes 2015-02-27
# changed by: Oliver Cordes 2019-08-16

import sys, os

try:
    import numpy as np
except:
    print( 'Please install numpy to use with pypovlib!!' )
    sys.exit( 1 )



# constants

_indent_char = ' '
_indent_nr   = 4

_fmt_key_float  = '{:s} {:6f}\n'
_fmt_key_int    = '{:s} {:d}\n'
_fmt_key_vector = '{:s} <{:6f},{:6f},{:6f}>\n'


# helper funtions

rot_axis_X = np.array([1.,0.,0.])
rot_axis_Y = np.array([0.,1.,0.])
rot_axis_Z = np.array([0.,0.,1.])

def create_rotation_matrix(vector, angle):
    angle = angle * np.pi / 180.
    matrix = np.zeros(9).reshape((3,3))

    u_x = vector[0]
    u_y = vector[1]
    u_z = vector[2]
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)

    matrix[0,0] = cos_a + u_x**2 * (1.-cos_a)
    matrix[0,1] = u_x * u_y * (1.-cos_a) - u_z * sin_a
    matrix[0,2] = u_x * u_z * (1.-cos_a) + u_y * sin_a
    matrix[1,0] = u_y * u_x * (1.-cos_a) + u_z * sin_a
    matrix[1,1] = cos_a + u_y**2 * (1.-cos_a)
    matrix[1,2] = u_y * u_z * (1.-cos_a) - u_x * sin_a
    matrix[2,0] = u_z * u_x * (1.-cos_a) - u_y * sin_a
    matrix[2,1] = u_z * u_y * (1.-cos_a) + u_x * sin_a
    matrix[2,2] = cos_a + u_z**2 * (1.-cos_a)

    return Matrix3D(rotation=matrix)


def get_rot_axes(x1, x2, y1, y2):
    # first get the normal vector for both planes
    x_n = np.cross(x1, x2)
    y_n = np.cross(y1, y2)

    test_dot = np.dot(x_n, y_n)
    if np.isclose(test_dot, 1.):
        rot_axis = -x_n
        rot_axis = x1
    elif np.isclose(test_dot, -1):
        rot_axis = x1
    else:
        rot_axis = np.cross(x_n, y_n)

    return rot_axis


def angle_Z(angle):
    angle = angle * np.pi / 180.
    return Matrix3D(np.array([[np.cos(angle), -np.sin(angle), 0., 0.],
                     [np.sin(angle), np.cos(angle), 0., 0.],
                     [0., 0., 1., 0.],
                     [0., 0., 0., 1.]]))


def angle_Y(angle):
    angle = angle * np.pi / 180.
    return Matrix3D(np.array([[np.cos(angle), 0., np.sin(angle), 0.],
                     [0., 1., 0., 0.],
                     [-np.sin(angle), 0., np.cos(angle), 0.],
                     [0., 0., 0., 1.]]))


def angle_X(angle):
    angle = angle * np.pi / 180.
    return Matrix3D(np.array([[1., 0., 0., 0.],
                     [0., np.cos(angle), -np.sin(angle), 0.],
                     [0., np.sin(angle), np.cos(angle), 0.],
                     [0., 0., 0., 1.]]))


def convert2vector( val ):
    if isinstance( val, Point3D ):
        return val.xyz
    if isinstance( val, float ):
        return np.array( [ val, val, val ], dtype=float )
    if ( isinstance( val, list ) or isinstance( val, tuple ) ) and ( len( val ) == 3 ):
        return np.array( val, dtype=float )
    if isinstance( val, np.ndarray ):
        return val.copy()
    raise TypeError( 'val is not float, int, list, tuple or numpy.ndarray with 3 elemets' )


def convertarray2vector( val ):
    if ( isinstance( val, Point3D ) ):
        return val.xyz
    if ( isinstance( val, list ) or isinstance( val, tuple ) ) and ( len( val ) == 3 ):
        return np.array( val, dtype=float )
    if isinstance( val, np.ndarray ):
        return val.copy()
    raise TypeError( 'val is not list, tuple or numpy.ndarray with 3 elemets' )


def convertarray2matrix( val ):
    if isinstance( val, np.ndarray ) and ( val.shape == (3,3) ):
        return val.copy()
    raise TypeError( 'val is not a numpy.ndarray with 3x3 elemets' )


def convertarray2full_matrix( val ):
    if isinstance( val, np.ndarray ) and ( val.shape == (12,) ):
        return val.copy()
    elif isinstance( val, list ) and ( len( val ) == 12 ):
        return np.array( val )
    elif isinstance( val, str ):
        s = val.split( ',' )
        if len( s ) == 12:
            ss = [ float(i) for i in s ]
            return np.array( ss )
    raise TypeError( 'val is not any value with 12 elements' )


# objects

class Point3D( object ):
    def __init__( self, xyz, atol=1e-6,rtol=1e-10 ):
        self.__xyz = convertarray2vector( xyz )
        self.__atol = atol
        self.__rtol = rtol


    def copy(self):
        return Point3D(self.__xyz, atol=self.__atol, rtol=self.__rtol)


    @property
    def xyz( self ):
        return self.__xyz


    @property
    def width( self ):
        return self.__xyz[0]


    @property
    def height( self ):
        return self.__xyz[1]


    @property
    def length( self ):
        return self.__xyz[2]


    @width.setter
    def width( self, val ):
        self.__xyz[0] = val


    @height.setter
    def height( self, val ):
        self.__xyz[1] = val


    @length.setter
    def length( self, val ):
        self.__xyz[2] = val


    def __getitem__( self, key ):
        return self.__xyz[key]


    def __str__( self ):
        return '<{:6f},{:6f},{:6f}>'.format( self.__xyz[0], self.__xyz[1], self.__xyz[2] )


    def __repr__(self):
        return 'Point3D([{},{},{}])'.format(self.__xyz[0], self.__xyz[1], self.__xyz[2])


    def __add__( self, val ):
        if isinstance( val, Point3D):
            return Point3D( self.__xyz + val.xyz )
        else:
            return Point3D( self.__xyz + val )

    __radd__ = __add__


    def __sub__( self, val ):
        if isinstance( val, Point3D):
            return Point3D( self.__xyz - val.xyz )
        else:
            return Point3D( self.__xyz - val )

    def __rsub__( self, val ):
        if isinstance( val, Point3D):
            return Point3D( val.xyz - self.__xyz  )
        else:
            return Point3D( - self.__xyz + val )

    def __mul__( self, val ):
        if isinstance( val, Point3D):
            return Point3D( self.__xyz * val.xyz )
        else:
            return Point3D( self.__xyz * val )

    __rmul__ = __mul__

    def __truediv__( self, val ):
        if isinstance( val, Point3D):
            return Point3D( self.__xyz / val.xyz )
        else:
            return Point3D( self.__xyz / val )

    def __rtruediv__( self, val ):
        if isinstance( val, Point3D):
            return Point3D( val.xyz / self.__xyz)
        else:
            return Point3D( val / self.__xyz )

    def __eq__( self, val ):
        return np.allclose( self.__xyz, val.xyz, atol=self.__atol, rtol=self.__rtol )


class Matrix3D(object):
    def __init__(self, value=None, rotation=None, translation=None):
        self.reset()

        if value is None:
            if rotation is not None:
                self._rotation = rotation
            if translation is not None:
                self.translate(translation)
        else:
            self._set_value(value)


    def _set_value(self, val):
        if isinstance(val, Matrix3D):
            self._rotation = val._rotation
            self._translation = val._translation
        else:
            full_matrix = convertarray2full_matrix(val)
            self._rotation    = full_matrix[:9].reshape((3,3))
            self._translation = full_matrix[9:]


    @property
    def rotation(self):
        return self._rotation


    @property
    def translation(self):
        return self._translation


    def _zero(self):
        return np.array([[1., 0., 0.],
                         [0., 1., 0.],
                         [0., 0., 1.]])


    def reset(self):
        self._rotation = self._zero()
        self._translation = np.zeros(3)


    def rotate(self, angle):
        self._rotation = np.dot(self._rotation, angle)


    def translate(self, translation):
        translation = convertarray2vector(translation)
        self._translation += translation


    def __str__(self):
        return ','.join([str(i) for i in np.append(self.rotation.flatten(), self.translation)])


    def __mul__(self, val):
        if isinstance(val, Point3D):
            return Point3D(np.dot(self.rotation, val.xyz) + self.translation)
        else:
            return val.copy()



# Povray basic object

class PovWriterObject( object ):
    # helper functios
    def _indent_str( self, nr ):
        return ''.join( _indent_char * _indent_nr * nr )


    def _write_indent( self, ffile, s, indent):
        ffile.write( self._indent_str( indent ) + s )
        #ffile.write( '%s%s' % ( self._indent_str( indent ), s ) )



class PovBasicObject( PovWriterObject ):
    def __init__( self, comment=None ):
        self._comment = comment

        self._includes    = []
        self._declares    = {}
        self._macro_defs  = []
        self._extra_files = []


    # handle includes/declares/macros
    def add_include(self, incfile):
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
        if self._declares.has_key( key ):
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


    # helper functios
    def _write_comment( self, ffile, indent=0 ):
        if self._comment is None: return
        self._write_indent( ffile, '// %s\n' % self._comment, indent )


    def _write_vector( self, ffile, key, v, indent=0 ):
        self._is_vector( v )
        self._write_indent( ffile, _fmt_key_vector.format( key, v[0], v[1], v[2] ), indent=indent )


    def _write_float( self, ffile, key, v , indent=0 ):
        self._is_float( v )
        self._write_indent( ffile, _fmt_key_float.format( key, v ), indent=indent )


    def _write_int( self, ffile, key, v , indent=0 ):
        self._is_int( v )
        self._write_indent( ffile, _fmt_key_int.format( key, v ), indent=indent )


    def write_pov( self, ffile, indent=0 ):
        self._write_comment( ffile, indent=indent )


    # some type check functions
    def _is_vector( self, val ):
        return True


    def _is_float( self, val ):
        if ( val is None or isinstance( val, float ) ):
            return True
        raise TypeError( 'val is not a float' )


    def _is_int( self, val ):
        if ( val is None or isinstance( val, int ) ):
            return True
        raise TypeError( 'val is not an int' )


    def _is_number( self, val ):
        if ( val is None or isinstance( val, int ) or  isinstance( val,float ) ):
            return True
        raise TypeError( 'val is not an int or a float' )


    def _is_string( self, val ):
        if ( val is None or isinstance( val, str ) ):
            return True
        raise TypeError( 'val is is not a string' )


    def _is_bool( self, val ):
        if ( val is None or isinstance( val, bool ) ):
            return True
        raise TypeError( 'val is not a bool' )


    def _is_number_string( self, val ):
        if ( val is None or isinstance( val, int ) or
            isinstance( val,float ) or isinstance( val, str ) ):
            return True
        raise TypeError( 'val is not an int or a float or a string')



class PovGeometry(object):
    def __init__(self):
        self.__rotate_before_translate = True

        self.__full_matrix             = []
        self.__rotate                  = []
        self.__translate               = []
        self.__scale                   = []
        self.__rotation_matrix         = None


    def set_rotate_before_translate(self, val):
        self.__rotate_before_translate = val


    @property
    def full_matrix(self):
        return self.__full_matrix


    @full_matrix.setter
    def full_matrix(self, val):
        if val is None:
            self.__full_matrix = []
        elif isinstance(val, (list, tuple)):
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


    def full_matrix_list(self, val):
        if isinstance(val, (list, tuple)):
            for m in val:
                self.__full_matrix.append(convertarray2full_matrix(m))


    @property
    def rotate(self):
        return self.__rotate


    @rotate.setter
    def rotate(self, new_rotate):
        if new_rotate is None:
            self.__rotate = []
        else:
            rotate = Point3D(new_rotate)
            self.__rotate.append(rotate)

            self.update_rotate(rotate)


    def set_rotation_matrix(self, new_matrix):
        self.__rotation_matrix = convertarray2matrix(new_matrix)

        self.update_rotation_matrix(self.__rotation_matrix)


    @property
    def translate(self):
        t = Point3D([0., 0., 0.])
        for i in self.__translate:
            t += i

        return t


    @translate.setter
    def translate(self, val):
        translate = Point3D( val )
        self.__translate.append(translate)

        self.update_translate(translate)


    @property
    def scale(self):
        # combine all scalings
        sc = np.array([1., 1., 1.])
        for i in self.__scale:
            sc *= i

        return sc


    @scale.setter
    def scale(self, new_scale):
        if isinstance(new_scale, (int, float)):
            self.__scale.append(new_scale)
        else:
            self.__scale.append(Point3D(new_scale))

        self.update_scale(new_scale)


    def update_rotate(self, rotate):
        pass


    def update_rotation_matrix(self, rotation_matrix):
        pass


    def update_translate(self, translate):
        pass


    def update_scale(self, scale):
        pass


    def _write_full_matrix(self, ffile, indent=0):
        for m in self.__full_matrix:
            self._write_indent(ffile, 'matrix <{}>\n'.format(m), indent)


    def _write_scale(self, ffile, indent=0):
        if len(self.__scale) == 0: return
        for sc in self.__scale:
            self._write_indent(ffile, 'scale %s\n' % sc, indent)


    def _write_translate(self, ffile, indent=0):
        if self.__translate is None: return
        for t in self.__translate:
           self._write_indent(ffile, 'translate %s\n' % t, indent)


    def _write_rotate(self, ffile, indent=0):
        for r in self.__rotate:
           self._write_indent(ffile, 'rotate %s\n' % r, indent)


    def _write_rotation_matrix(self, ffile, indent=0):
        if self.__rotation_matrix is None: return
        self._write_indent( ffile,
             'matrix <%f,%f,%f,%f,%f,%f,%f,%f,%f,0,0,0>\n' % (self.__rotation_matrix[0][0],
                       self.__rotation_matrix[0][1],
                       self.__rotation_matrix[0][2],
                       self.__rotation_matrix[1][0],
                       self.__rotation_matrix[1][1],
                       self.__rotation_matrix[1][2],
                       self.__rotation_matrix[2][0],
                       self.__rotation_matrix[2][1],
                       self.__rotation_matrix[2][2]),
                       indent)


    def _write_geometrics(self, ffile, indent=0):
        self._write_full_matrix(ffile, indent=indent)
        self._write_scale(ffile, indent=indent)
        if self.__rotate_before_translate:
            self._write_rotate(ffile, indent=indent)
            self._write_rotation_matrix(ffile, indent=indent)
            self._write_translate(ffile, indent=indent)
        else:
            self._write_translate(ffile, indent=indent)
            self._write_rotate(ffile, indent=indent)
            self._write_rotation_matrix(ffile, indent=indent)




if __name__== "__main__":
    p = Point3D( [1,10,1] )

    print( p.height )
    p.height = 1
    print( p )

    q = Point3D( [1,2,3] )

    q = p
    print( p+q )
    print( 2+p )
    q /= 70
    print( q )
    q *= 10
    q *= 7

    print( q, p == q )
    print( p[0:-1] )

    #p = Point3D( [10,11,12] )
    #q = p
