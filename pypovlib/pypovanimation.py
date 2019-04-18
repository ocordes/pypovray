# pypovanimation.py

# wirtten by: Oliver Cordes 2015-07-17
# changed by: Oliver Cordes 2018-04-18

#
import sys

try:
    import numpy as np
except:
    print( 'Please install numpy to use with pypovobjects.py!' )
    sys.exit( 1 )


from pypovlib.pypovobjects import *

import sys, os

# constants


# class

class PovAnimation( PovFile ):
    def __init__(self, directory='.',
                       name_prefix='animation',
                       camera_optimize=False,
                       verbose=False,):
        PovFile.__init__(self, camera_optimize=camera_optimize, verbose=verbose)

        self._directory   = directory
        self._name_prefix = name_prefix


    def update_timeline( self, time_abs, time_delta, fnr ):
        for i in self._items:
            i.update_timeline( time_abs, time_delta, fnr )

        if self._camera is not None:
            self._camera.update_timeline( time_abs, time_delta, fnr )


    def update_time( self, time_abs ):
        for i in self._items:
            i.update_time( time_abs )

        if self._camera is not None:
            self._camera.update_time( time_abs )


    def update_timedelta( self, time_delta ):
        for i in self._items:
            i.update_timedelta( time_delta )

        if self._camera is not None:
            self._camera.update_timedelta( time_delta )


    def update_frame( self, framenr ):
        for i in self._items:
            i.update_frame( framenr )

        if self._camera is not None:
            self._camera.update_frame( framenr )


    def animate( self, frames = None, duration = None, time_delta = None ):

        # create/check directory
        if not os.path.exists( self._directory ):
            try:
                os.mkdir( self._directory )
            except:
                print('ERROR: Cannot access directory \'%s\' !' % self._directory )
                return

        if frames is None:
            print('ERROR: No frames given!')
            return

        if (duration is None) and (time_delta is None):
            print('ERROR: Neither duration or time_delta is given!')
            return

        if duration is None :
            time_delta = time_delta
        else:
            time_delta = float( duration ) / frames

        time_abs = 0.0

        print_skip = int( frames / 100. )
        for fnr in range( frames ):
            if ( frames < 100 ):
                print( 'creating frame %i/%i ...' % ( fnr+1, frames )),
            else:
                pass

            fname = '%s/%s%05i.pov' % ( self._directory, self._name_prefix, fnr )

            self.write_povfile(fname)
            self.update_timeline(time_abs, time_delta, fnr)

            self.update_time(time_abs)
            self.update_timedelta(time_delta)
            self.update_frame(fnr)

            # prepare the next step
            time_abs += time_delta

            if ( frames  < 100 ):
                print( 'Done.' )
            else:
                if ( ( fnr % print_skip ) == 0 ):
                    print( 'creating %i/%i frames done.' % ( fnr+1, frames) )
