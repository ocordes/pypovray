# pypovobjects.py
#
# written by: Oliver Cordes 2013-12-30
# changed by: Oliver Cordes 2014-01-02


import os


class PovObject( object ):
    def __init__( self ):
        self.position      = [ 0.0, 0.0, 0.0 ]
        self.scale         = [ 1.0, 1.0, 1.0 ]
        self.object_cmd    = None
        self.texture_cmd   = None

    def set_object_cmd( self, new_object_cmd ):
        if isinstance( new_object_cmd, str ):
            self.object_cmd = new_object_cmd
        else:
            raise TypeError( 'object_cmd must be a string' )

    def set_texture_cmd( self, new_texture_cmd ):
        if isinstance( new_texture_cmd, str ):
            self.texture_cmd = new_texture_cmd
        else:
            raise TypeEroor( 'texture_cmd must be a string' )

        
    def set_position( self, new_pos ):
        ok = False
        if isinstance( new_pos, list ):
            if ( len( new_pos ) == 3 ):
                self.position = new_pos
                ok = True
        elif isinstance( new_pos, tuple ):
            if ( len( new_pos ) == 3 ):
                self.position = list( new_pos )
                ok = True
        if ok == False:
            raise TypeError( 'position is not list or tuple with 3 elements' )


    def set_scale( self, new_scale ):
        ok = False
        if isinstance( new_scale, int ):
             self.scale = [ float( new_scale ), float( new_scale ), float( new_scale ) ]
             ok = True
        if isinstance( new_scale, float ):
             self.scale = [ new_scale, new_scale, new_scale ]
             ok = True
        elif isinstance( new_scale, list ):
            if ( len( new_scale ) == 3 ):
                self.scale = new_scale
                ok = True
        elif isinstance( new_scale, tuple ):
            if ( len( new_scale ) == 3 ):
                self.scale = list( new_scale )
                ok = True
        if ok == False:
            raise TypeError( 'scale is not float, integer, list or tuple with 3 elements' )
    

    def writepov( self, ffile ):
        if ( self.object_cmd != None ):
            ffile.write( 'object{\n' )
            ffile.write( ' %s\n' % self.object_cmd )
            if ( self.texture_cmd != None ):
                ffile.write( ' %s\n' % self.texture_cmd )
            ffile.write( ' scale <%f,%f,%f>\n' % ( self.scale[0], self.scale[1], self.scale[2] ) )
            ffile.write( ' translate <%f,%f,%f>\n' % ( self.position[0], self.position[1], self.position[2] ) )
            ffile.write( '}\n' )
        else:
            print( 'Object is undefined! Skip this object!' )


    def update_time( self, time_abs ):
        pass

    def update_timedelta( self, time_delta ):
        pass




class PovObjects( list ):
    def update_time( self, time_abs ):
        for i in iter( self ):
            i.update_time( time_abs )


    def update_timedelta( self, time_delta ):
        for i in iter( self ):
            i.update_timedelta( time_delta )

            
    def writepov( self, ffile ):
        for i in iter( self ):
            i.writepov( ffile )



class PovrayFile( object ):
    options = {
        'prefix_filename'  : None,
        'postfix_filename' :  None,
        'output_dir'       : None 
        }

    objects_list = []
    
    def __init__( self, **kwargs ):
        self.options.update( kwargs )


    def set_prefix_file( self, prefix_filename ):
        self.options['prefix_filename'] = prefix_filename

    def set_postfix_file( self, postfix_filename ):
        self.options['postfix_filename'] = postfix_filename

    def append_objects( self, objects ):
        self.objects_list.append( objects )


    def update_time( self, time_abs ):
        for i in self.objects_list:
            i.update_time( time_abs )


    def update_timedelta( self, time_delta ):
        for i in self.objects_list:
            i.update_timedelta( time_delta )
            
        
    def write( self, filename ):
        if ( self.options['output_dir'] != None ):
            fname = os.path.join( self.options['output_dir'], filename )
        else:
            fname = filename
            
        f = open( fname, 'w' )

        if ( self.options['prefix_filename'] != None ):
            f.write( '/* append prefix file \'%s\' */\n' % self.options['prefix_filename'] )
            try:
                fi = open( self.options['prefix_filename'] )
                for i in fi:
                    f.write( i )
                fi.close()
            except:
                print( 'Can\' read prefix file! File skipped!' )
            f.write( '/* end append prefix file \'%s\' */\n' % self.options['prefix_filename'] )

        # add objects
        for i in self.objects_list:
            i.writepov( f )
            
        if ( self.options['postfix_filename'] != None ):
            f.write( '/* append postfix file \'%s\' */\n' % self.options['postfix_filename'] )
            try:
                fi = open( self.options['postfix_filename'] )
                for i in fi:
                    f.write( i )
                fi.close()
            except:
                print( 'Can\' read postfix file! File skipped!' )
            f.write( '/* end append postfix file \'%s\' */\n' % self.options['postfix_filename'] )
            
        f.close()


    def animate( self, **kwargs ):
        animation_opts = { 'prefix' : 'animation',
                           'frames' : None,
                           'duration' : None,
                           'time_delta' : None 
                           }

        animation_opts.update( kwargs )
        

        # do the real animation stuff

        frames     = animation_opts['frames']        
        if ( animation_opts['duration'] != None ):
            time_delta = float( animation_opts['duration'] ) / frames
        else:
            time_delta = animation_opts['time_delta']

        time_abs = 0.0


        for fnr in xrange( frames ):
            fname = '%s%05i.pov' % ( animation_opts['prefix'], fnr )

            self.write( fname )

            self.update_time( time_abs)
            self.update_timedelta( time_delta )
            
            # prepare the next step
            time_abs += time_delta
