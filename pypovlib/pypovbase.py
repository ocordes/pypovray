# pypovobjects.py

# written by: Oliver Cordes 2015-02-27
# changed by: Oliver Cordes 2018-11-25

import sys

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


# def indent_str( nr ):
#     return ''.join( _indent_char * _indent_nr * nr )
#
#
# def write_indent( ffile, s, indent):
#     ffile.write( '%s%s' % ( indent_str( indent ), s ) )


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

        self._includes   = []
        self._declares   = {}
        self._macro_defs = []


    # handle includes/declares/macros
    def add_include( self, incfile ):
        if incfile in self._includes:
            pass
        else:
            self._includes.append( incfile )


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
