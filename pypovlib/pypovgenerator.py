# pypovgenerator.py

# wirtten by: Oliver Cordes 2016-02-26
# changed by: Oliver Cordes 2016-05-24

import sys, os

try:
    import numpy as np
except:
    print( 'Please install numpy to use with pypovobjects.py!' )
    sys.exit( 1 )


from pypovlib.pypovobjects import *


import pickle, gzip

# constants

_version = 1000

# classes

class PovGenerator( object ):
    def __init__( self ):
        self._items = {}

        
    def add( self, name, new_obj ):
        #if ( isinstance( new_obj, list ) == True ) or  ( isinstance( new_obj, tuple ) == True ):
        #    for i in new_obj:
        #        self.add( i )
        #else:
        #    if self._verify_object( new_obj ) == True:
        #        self._items.append( new_obj )
        self._items[name] = new_obj


    def save( self, filename, zip=False ):
        fname = filename
        if ( zip == True ):
            fname += '.gz'

        try:
            if ( zip == True ):
                f = gzip.open( fname, 'w' )
            else:
                f = open( fname ,'w' )
            pickle.dump( _version, f )
            pickle.dump( self._items, f )
            f.close()
        except IOError as  s:
            print( 'Can\'t write file \'%s\' (%s)!' % ( fname, s ) )


    def load( self, filename ):
        fname = filename  + '.gz'
        if ( os.access( fname, os.R_OK ) == True ):
            f = gzip.open( fname, 'r' )
        else:
            fname = filename
            if ( os.access( fname, os.R_OK ) == True ):
                f = open( fname, 'r' )
            else:
                print( 'Can\'t open  file \'%s\' !' )
                return
        print( 'Loading %s ... ' % fname )

        version = cPickle.load( f )
        items   = cPickle.load( f )

        self._items = items

        print( 'Done.' )

        f.close()

        
    def get( self, key ):
        if self._items.has_key( key ):
            return self._items[key]
        else:
            return None
