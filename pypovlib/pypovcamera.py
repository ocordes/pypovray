# pypovcamera.py

# written by: Oliver Cordes 2015-06-14
# changed by: Oliver Cordes 2018-03-12


from pypovlib.pypovbase import PovBasicObject, convertarray2vector

from math import *


# camera types
camera_perspective = 1



class PovCamera( PovBasicObject ):
    def __init__( self,
                  location=None,
                  look_at=None,
                  sky=None,
                  angle=None,
                  aspect_ratio=None,
                  vp=False,
                  comment=None ):
        PovBasicObject.__init__( self, comment=comment )

        self._aspect_ratio = aspect_ratio

        self._sequences = []

        self._camera_type = camera_perspective
        if location is None:
            self._location = convertarray2vector( [0,1,-1] )   # some default
        else:
            self._location = convertarray2vector( location )
        if look_at is None:
            self._look_at = convertarray2vector( [0,0,0] )    # some default
        else:
            self._look_at = convertarray2vector( look_at )
        if sky is None:
            self._sky      = convertarray2vector( [0,1,0] )    # uses the default
        else:
            self._sky      = convertarray2vector( sky )
        if angle is None:
            self._angle    = 67.380
        else:
            self._angle    = angle

        self._vp = vp

        self._normal = None

        self._focal_blur   = False
        self._focal_point  = None
        self._aperture     = None
        self._blur_samples = None
        self._confidence   = None
        self._variance     = None

        self._update_camera()


    def _update_camera( self ):
        self._normal = self._look_at - self._location

    def check_visible( self, val ):
        if ( isinstance( val, list ) == True ) or ( isinstance( val, tuple ) == True ):
            for i in val:
                ret = self.check_visible( i )
                if ret:
                    return ret
            return False
        else:
            return True

    def zoom( self, factor ):
        pass

    def set_location( self, location ):
        self._location = convertarray2vector( location )
        self._update_camera()

    def set_look_at( self, look_at ):
        self._look_at = convertarray2vector( look_at )
        self._update_camera()

    def set_sky( self, sky ):
        self._look_at = convertarray2vector( sky )
        self._update_camera()

    #     focal_point <0.20,1.5,-5.25>
    #     aperture 0.7     // 0.05 ~ 1.5
    #     blur_samples 100 // 4 ~ 100
    #     confidence 0.9   // 0 ~ 1
    #     variance 1/128
    def set_focal_blur( self,
                        focal_point,
                        aperture,
                        blur_samples,
                        confidence = 0.9,
                        variance = 128 ):

        self._focal_blur   = True
        self._focal_point  = convertarray2vector( focal_point )
        self._aperture     = aperture
        self._blur_samples = blur_samples
        self._confidence   = confidence
        self._variance     = variance


    # camera sequences for animations
    def add_sequence( self, seq ):
        if ( isinstance( seq, list ) == True ) or  ( isinstance( seq, tuple ) == True ):
            for i in seq:
                self.add_sequene( i )
        else:
            if isinstance( seq, PovCameraSequence) == True:
                # back link to the camera
                seq.set_camera( self )
                self._sequences.append( seq )


    def write_pov( self, ffile, indent=0 ):
        self._write_indent( ffile, 'camera{\n', indent=indent )
        if self._camera_type == camera_perspective:
            self._write_indent( ffile, 'perspective\n', indent=indent+1 )
        else:
            pass

        if self._vp == False:
            self._write_vector( ffile, 'location', self._location, indent=indent+1 )
            #self._write_indent( ffile, 'location <%f,%f,%f>\n' % ( self._location[0],
            #                                                    self._location[1],
            #                                                    self._location[2] ),
            #                                                    indent=indent+1 )
            self._write_indent( ffile, 'look_at <%f,%f,%f>\n' % ( self._look_at[0],
                                                                self._look_at[1],
                                                                self._look_at[2] ),
                                                                indent=indent+1 )
            self._write_indent( ffile, 'sky <%f,%f,%f>\n' % ( self._sky[0],
                                                                self._sky[1],
                                                                self._sky[2] ),
                                                                indent=indent+1 )
            self._write_indent( ffile, 'angle %f\n' % ( self._angle ),
                                                               indent=indent+1 )
        else:
            # taken from: http://www.f-lohmueller.de/pov_tut/camera_light/arc_persp_d1.htm
            ##include "transforms.inc"
            ##declare Cam_V = Camera_Look_At - Camera_Location;
            ##declare Cam_Ho = sqrt(pow(Cam_V.x,2)+pow(Cam_V.z ,2));
            ##declare Cam_Y  = Camera_Look_At.y - Camera_Location.y;
            #//--------------------------------------------------//
            #camera{ angle Camera_Angle
            #        right x*image_width/image_height
            #        location<0,Camera_Look_At.y,-Cam_Ho>
            #        matrix<1,0,0, 0,1,0, 0,Cam_Y/Cam_Ho,1, 0,0,0>
            #        Reorient_Trans(z,<Cam_V.x,0,Cam_V.z>)
            #        translate<Camera_Look_At.x,0,Camera_Look_At.z>
            #      } //------------------------------------------//

            # recalulate the parameters
            Cam_V = self._look_at - self._location
            Cam_Ho = sqrt(pow(Cam_V[0],2)+pow(Cam_V[2] ,2))
            Cam_Y  = self._look_at[1] - self._location[1]

            self._write_indent( ffile, 'location <%f,%f,%f>\n' % ( 0,
                                                               self._look_at[1],
                                                               -Cam_Ho ),
                                                               indent=indent+1 )
            self._write_indent( ffile, 'look_at <%f,%f,%f>\n' % ( self._look_at[0],
                                                               self._look_at[1],
                                                               self._look_at[2] ),
                                                               indent=indent+1 )
            #self._write_indent( ffile, 'sky <%f,%f,%f>\n' % ( self._sky[0],
            #                                                       self._sky[1],
            #                                                       self._sky[2] ),
            #                                                       indent=indent+1 )
            self._write_indent( ffile, 'angle %f\n' % ( self._angle ),
                                                               indent=indent+1 )
            self._write_indent( ffile, 'matrix<1,0,0, 0,1,0, 0,%f,1, 0,0,0>\n' % ( Cam_Y/Cam_Ho ), indent=indent+1 )
            self._write_indent( ffile, 'Reorient_Trans(z,<%f,0,%f>)\n' % ( Cam_V[0], Cam_V[2] ), indent=indent+1 )
            self._write_indent( ffile, 'translate<%f,0,%f>\n' % ( self._look_at[0],
                                                              self._look_at[2] ), indent=indent+1 )
        # end of self._vp

        if self._aspect_ratio is None:
            self._write_indent( ffile, 'right x * image_width/image_height\n', indent=indent+1 )

        if self._focal_blur:
            self._write_vector( ffile, 'focal_point', self._focal_point, indent=indent+1 )
            self._write_float( ffile, 'aperture', self._aperture, indent=indent+1 )
            self._write_int( ffile, 'blur_samples', self._blur_samples, indent=indent+1 )
            self._write_float( ffile, 'confidence', self._confidence, indent=indent+1 )
            self._write_float( ffile, 'variance', 1.0/self._variance, indent=indent+1 )


        self._write_indent( ffile, '}\n', indent=indent )


    # animation routines
    def update_timeline( self, time_abs, time_delta, fnr ):
        pass


    def update_time( self, time_abs ):
        for i in self._sequences:
            i.update_time( time_abs )


    def update_timedelta( self, time_delta ):
        for i in self._sequences:
            i.update_timedelta( time_delta )


    def update_frame( self, framenr ):
        for i in self._sequences:
            i.update_frame( framenr )


# taken from: http://www.f-lohmueller.de/pov_tut/camera_light/arc_persp_d1.htm
##include "transforms.inc"
##declare Cam_V = Camera_Look_At - Camera_Location;
##declare Cam_Ho = sqrt(pow(Cam_V.x,2)+pow(Cam_V.z ,2));
##declare Cam_Y  = Camera_Look_At.y - Camera_Location.y;
#//--------------------------------------------------//
#camera{ angle Camera_Angle
#        right x*image_width/image_height
#        location<0,Camera_Look_At.y,-Cam_Ho>
#        matrix<1,0,0, 0,1,0, 0,Cam_Y/Cam_Ho,1, 0,0,0>
#        Reorient_Trans(z,<Cam_V.x,0,Cam_V.z>)
#        translate<Camera_Look_At.x,0,Camera_Look_At.z>
#      } //------------------------------------------//

class PovCamera2Fluchtpunkt( PovCamera ):
    def __init__( self, location=None, look_at=None, sky=None, angle=None, aspect_ratio=None, comment=None ):
        PovCamera.__init__( self,
                            location=location,
                            look_at=look_at,
                            sky=sky,
                            angle=angle,
                            aspect_ratio=aspect_ratio,
                            comment=comment )
        self.add_include( 'transforms.inc' )

    def write_pov( self, ffile, indent=0 ):
        self._write_indent( ffile, 'camera{\n', indent=indent )
        if self._camera_type == camera_perspective:
            self._write_indent( ffile, 'perspective\n', indent=indent+1 )
        else:
            pass

        # recalulate the parameters
        Cam_V = self._look_at - self._location
        Cam_Ho = sqrt(pow(Cam_V[0],2)+pow(Cam_V[2] ,2))
        Cam_Y  = self._look_at[1] - self._location[1]

        self._write_indent( ffile, 'location <%f,%f,%f>\n' % ( 0,
                                                               self._look_at[1],
                                                               -Cam_Ho ),
                                                               indent=indent+1 )
        self._write_indent( ffile, 'look_at <%f,%f,%f>\n' % ( self._look_at[0],
                                                               self._look_at[1],
                                                               self._look_at[2] ),
                                                               indent=indent+1 )
        #self._write_indent( ffile, 'sky <%f,%f,%f>\n' % ( self._sky[0],
        #                                                       self._sky[1],
        #                                                       self._sky[2] ),
        #                                                       indent=indent+1 )
        self._write_indent( ffile, 'angle %f\n' % ( self._angle ),
                                                               indent=indent+1 )
        self._write_indent( ffile, 'matrix<1,0,0, 0,1,0, 0,%f,1, 0,0,0>\n' % ( Cam_Y/Cam_Ho ), indent=indent+1 )
        self._write_indent( ffile, 'Reorient_Trans(z,<%f,0,%f>)\n' % ( Cam_V[0], Cam_V[2] ), indent=indent+1 )
        self._write_indent( ffile, 'translate<%f,0,%f>\n' % ( self._look_at[0],
                                                              self._look_at[2] ), indent=indent+1 )

        if self._aspect_ratio is None:
            self._write_indent( ffile, 'right x * image_width/image_height\n', indent=indent+1 )
        self._write_indent( ffile, '}\n', indent=indent )




class PovCamera43( PovCamera ):
    def __init__( self, location, look_at, sky=None, angle=None, vp=False, comment=None ):
        PovCamera.__init__( self,
                            location = location,
                            look_at = look_at,
                            sky = sky,
                            angle = angle,
                            aspect_ratio = 4.0/3.0,
                            vp = vp,
                            comment=comment )


class PovCameraHD( PovCamera ):
    def __init__( self, location, look_at, sky=None, angle=None, vp=False, comment=None ):
        PovCamera.__init__( self,
                            location = location,
                            look_at = look_at,
                            sky = sky,
                            angle = angle,
                            aspect_ratio = 16.0/9.0,
                            vp = vp,
                            comment = comment )



# camera sequences
seq_none     = 0
seq_location = 1
seq_look_pos = 2

seq_time_abs   = 0
seq_time_delta = 1
seq_time_frame = 2

class PovCameraSequence( object ):
    def __init__( self, name, seq_type, time_type, data ):
        self._name      = name
        self._seq_type  = seq_type
        self._time_type = time_type
        self._data      = data
        self._camera    = None

        # data helpers
        self._current   = None


    def set_camera( self, camera ):
        self._camera = camera


    def _interpolate_vector( self, x, x1, x2, vec1, vec2 ):
        v1 = convertarray2vector( vec1 )
        v2 = convertarray2vector( vec2 )
        return v1 + (x - x1 )  * ( v2 - v1 ) / ( x2-x1 )



    def update_time( self, time_abs ):
        if  self._seq_type == seq_location:
            if self._time_type == seq_time_abs:
                self._update_time_location_abs( time_abs )
        elif self._seq_type == seq_look_pos:
            pass


    def update_timedelta( self, time_delta ):
        pass


    def update_frame( self, framenr ):
        if  self._seq_type == seq_location:
            if self._time_type == seq_time_frame:
                self._update_time_location_frame( framenr )


    def _update_time_location_abs( self, time_abs ):
        print( time_abs )


    def _update_time_location_frame( self, framenr ):
        print( framenr )
        if self._current is None:
            # looking for a start point
            i = 0
            while ( i < len( self._data) ):
                if self._data[i][0] >= framenr:
                    break
                i += 1

            self._current = i

        if ( framenr > self._data[self._current][0] ):
            # test if next step is reached
            if ( self._current + 1 ) != len( self._data ):
                if ( framenr >= self._data[self._current+1][0] ):
                    self._current += 1


        if ( ( framenr <= self._data[self._current][0] ) ) or (( self._current + 1 ) == len( self._data ) ):
            # use this value
            self._camera.set_location( self._data[self._current][1]  )
        else:
            print( 'interpolate' )
            self._camera.set_location( self._interpolate_vector( framenr,
                                                                  self._data[self._current][0],
                                                                  self._data[self._current+1][0],
                                                                  self._data[self._current][1],
                                                                  self._data[self._current+1][1] ) )
