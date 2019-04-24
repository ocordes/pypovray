# pypovanimation.py

# wirtten by: Oliver Cordes 2015-07-17
# changed by: Oliver Cordes 2018-04-19

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

        self._fps         = None
        self._duration    = None
        self._frames      = None


    def set_fps(self, fps):
        if fps is not None:
            self._fps = fps


    def set_duration(self, duration):
        if duration is not None:
            self._duration = duration


    def set_frames(self, frames):
        if frames is not None:
            self._frames = frames


    def update_timeline( self, time_abs, time_delta, fnr ):
        for i in self._items:
            i.update_timeline( time_abs, time_delta, fnr )

        if self._camera is not None:
            self._camera.update_timeline( time_abs, time_delta, fnr )


    def update_time(self, time_abs):
        for i in self._items:
            i.update_time(time_abs)

        if self._camera is not None:
            self._camera.update_time(time_abs)


    def update_timedelta(self, time_delta):
        for i in self._items:
            i.update_timedelta(time_delta)

        if self._camera is not None:
            self._camera.update_timedelta(time_delta)


    def update_frame(self, framenr):
        for i in self._items:
            i.update_frame(framenr)

        if self._camera is not None:
            self._camera.update_frame(framenr)


    def _calculate_variables(self):
        if self._frames is None:
            if (self._duration is None) or (self._fps is None):
                print('ERROR: cannot calculate the number of frames')
                return -1, -1
            frames = self._duration * self._fps
            time_delta = 1./self._fps
        else:
            if (self._duration is None) and (self._fps is None):
                print('ERROR: cannot calculate the timedelta between frames')
                return -1, -1
            frames = self._frames
            if self._fps is None:
                # only frames and duration is set
                time_delta = float(self._duration) / self._frames
            else:
                # only frames and fps are set
                time_delta = 1./self._fps

        return frames, time_delta


    def animate(self, frames = None, duration = None, fps = None, submit=False):
        # overwrite given parameters from pypovapp even if the
        # combination of variables are wrong
        self.set_frames(frames)
        self.set_duration(duration)
        self.set_fps(fps)

        # create/check directory
        if not os.path.exists( self._directory ):
            try:
                os.mkdir( self._directory )
            except:
                print('ERROR: Cannot access directory \'%s\' !' % self._directory )
                return False

        # calculate the variables for the animation loop
        frames, time_delta = self._calculate_variables()

        if frames == -1:
            # something wrong
            return False

        time_abs = 0.0

        print('Create an animation for %i frames with a time delta of %.2fs between images' % (frames, time_delta))

        print_skip = frames // 100.
        for fnr in range(frames):
            if (frames < 100):
                print('creating frame %i/%i ...' % ( fnr+1, frames ), end=' ')
            else:
                pass

            fname = '%s/%s%05i.pov' % (self._directory, self._name_prefix, fnr)

            self.write_povfile(fname)
            self.update_timeline(time_abs, time_delta, fnr)

            self.update_time(time_abs)
            self.update_timedelta(time_delta)
            self.update_frame(fnr)

            # prepare the next step
            time_abs += time_delta

            if (frames  < 100):
                print('Done.')
            else:
                if (( fnr % print_skip ) == 0):
                    print('creating %i/%i frames done.' % ( fnr+1, frames))

        return True
