# pypovtextures.py
#
#
# written by: Oliver Cordes 2015-04-10
# changed by: Oliver Cordes 2016-12-16

# povray syntax for finish
#ambient COLOR | diffuse Amount | brilliance Amount |
#    phong Amount | phong_size Amount | specular Amount |
#    roughness Amount | metallic [Amount] | reflection COLOR |
#    crand Amount | conserve_energy BOOL_ON_OF |
#    reflection { Color_Reflecting_Min [REFLECTION_ITEMS...] }|
#    irid {

from  pypovlib.pypovbase import PovBasicObject, convert2vector, convertarray2vector


_fmt_key_float = '{:s} {:6f}\n'
_fmt_key_int   = '{:s} {:d}\n'

normal_type_none   = 0
normal_type_bumps  = 1


class PovFinish( PovBasicObject ):
    def __init__( self, comment=None, name=None ):
        PovBasicObject.__init__( self, comment=comment )
        self.name = name

        self.ambient         = None
        self.diffuse         = None
        self.brilliance      = None
        self.phong           = None
        self.phong_size      = None
        self.specular        = None
        self.roughness       = None
        self.is_metallic     = False
        self.metallic        = None
        self.reflection      = None
        self.crand           = None
        self.conserve_energy = None
        self.irid            = None

    def verify( self ):
        self._is_number( self.ambient )
        self._is_number( self.diffuse )
        self._is_number( self.brilliance )
        self._is_number( self.phong )
        self._is_number( self.phong_size )
        self._is_number( self.specular )
        self._is_number( self.roughness )
        self._is_bool( self.is_metallic )
        self._is_number( self.metallic )
        self._is_number_string( self.reflection )
        self._is_number( self.crand )
        self._is_bool( self.conserve_energy )
        self._is_string( self.irid )
        return True

    def write_pov( self, ffile, indent=0 ):
        if ( self.verify() == True ):
            self._write_indent( ffile, 'finish{\n', indent )
            if self.ambient is not None:
                s = _fmt_key_float.format( 'ambient', self.ambient )
                self._write_indent( ffile, '%s' % s, indent+1 )
            if self.diffuse is not None:
                self._write_indent( ffile, _fmt_key_float.format( 'diffuse', self.diffuse ), indent+1 )
            if self.brilliance is not None:
                s = _fmt_key_float.format( 'brilliance', self.brilliance )
                self._write_indent( ffile, '%s' % s, indent+1 )
            if self.phong is not None:
                s = _fmt_key_float.format( 'phong', self.phong )
                self._write_indent( ffile, '%s' % s, indent+1 )
            if self.phong_size is not None:
                s = _fmt_key_float.format( 'phong_size', self.phong_size )
                self._write_indent( ffile, '%s' % s, indent+1 )
            if self.specular is not None:
                s = _fmt_key_float.format( 'specular', self.specular )
                self._write_indent( ffile, '%s' % s, indent+1 )
            if self.roughness is not None:
                s = _fmt_key_float.format( 'roughness', self.roughness )
                self._write_indent( ffile, '%s' % s, indent+1 )
            if self.is_metallic:
                if self.metallic is None:
                    self._write_indent( ffile, 'metallic\n' )
                else:
                    s = _fmt_key_float.format( 'metallic', self.metallic )
                    self._write_indent( ffile, '%s' % s, indent+1 )
            if self.reflection is not None:
                if ( isinstance( self.reflection, str) ):
                    s = 'reflection { %s }' % self.reflection
                else:
                    s = _fmt_key_float.format( 'reflection', self.reflection )
                self._write_indent( ffile, '%s' % s, indent+1 )
            if self.crand is not None:
                pass
            if self.conserve_energy is not None:
                pass
            if self.irid is not None:
                pass
            self._write_indent( ffile, '}\n', indent )


class PovImageMap( PovBasicObject ):
    def __init__( self, image, map_type, once, comment=None ):
        PovBasicObject.__init__( self, comment=comment )

        self._image                   = image
        self._map_type                = map_type
        self._once                    = once

        self._translate               = None
        self._rotate                  = None
        self._scale                   = None
        self._rotate_before_translate = True

    def set_rotate( self, new_rotate ):
        self._rotate = convertarray2vector( new_rotate )

    def set_translate( self, new_translate ):
        self._translate = convertarray2vector( new_translate )

    def set_rotate_before_translate( self, val ):
        self._rotate_before_translate = val

    def set_scale( self, new_scale ):
        self._scale = convert2vector( new_scale )
        #print self._scale

    def _write_scale( self, ffile, indent=0 ):
        if self._scale is None: return
        self._write_indent( ffile, 'scale <%f,%f,%f>\n' % ( self._scale[0],
                                                     self._scale[1],
                                                     self._scale[2] ),
                                                     indent )

    def _write_translate( self, ffile, indent=0 ):
        if self._translate is None: return
        self._write_indent( ffile, 'translate <%f,%f,%f>\n' % ( self._translate[0],
                                                                self._translate[1],
                                                                self._translate[2] ),
                                                                indent )

    def _write_rotate( self, ffile, indent=0 ):
        if self._rotate is None: return
        self._write_indent( ffile, 'rotate <%f,%f,%f>\n' % ( self._rotate[0],
                                                             self._rotate[1],
                                                             self._rotate[2] ),
                                                             indent )

    def _write_geometrics( self, ffile, indent=0 ):
        self._write_scale( ffile, indent=indent )
        if self._rotate_before_translate:
            self._write_rotate( ffile, indent=indent )
            self._write_translate( ffile, indent=indent )
        else:
            self._write_translate( ffile, indent=indent )
            self._write_rotate( ffile, indent=indent )

    def write_pov( self, ffile, indent = 0 ):
        PovBasicObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'image_map{\n', indent=indent )
        self._write_indent( ffile, '"%s"\n' % self._image, indent=indent+1 )
        self._write_indent( ffile, 'map_type %i\n' % self._map_type,  indent=indent+1 )
        if ( self._once ):
            self._write_indent( ffile, 'once\n',  indent=indent+1 )
        self._write_geometrics( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent=indent )


class PovColorMap( PovBasicObject ):
    def __init__( self, cmap, comment=None ):
        PovBasicObject.__init__( self, comment=comment )

        self._cmap = cmap

    def write_pov( self, ffile, indent = 0 ):
        PovBasicObject.write_pov( self, ffile, indent=indent )
        self._write_indent( ffile, 'color_map{\n', indent=indent )
        for i in self._cmap:
            self._write_indent( ffile, '[ %f, color %s ]\n' % ( i[0], i[1] ) , indent=indent)
        self._write_indent( ffile, '}\n', indent=indent )


class PovNormal( PovBasicObject ):
    def __init__( self, comment=None, name=None, cmd=None ):
        PovBasicObject.__init__( self, comment=comment )

        self._cmd = cmd
        self.normap_type = normal_type_none

        self.bumps_size = None
        self.bumps_scale = None


    def write_pov( self, ffile, indent=0 ):
        self._write_indent( ffile, 'normal{\n', indent=indent )
        if self._cmd is not None:
            self._write_indent( ffile, cmd+'\n',  indent=indent+1 )
        else:
            if ( self.normal_type == normal_type_bumps ):
                if ( self.bumps_size is None ):
                    raise ValueError( 'bumps_size must be defined!' )
                s = _fmt_key_float.format( 'bumps', self.bumps_size )
                self._write_indent( ffile, '%s' % s, indent+1 )
                if ( self.bumps_scale is not None ):
                    s = _fmt_key_float.format( 'scale', self.bumps_scale )
                    self._write_indent( ffile, '%s' % s, indent+1 )
            else:
                pass
        self._write_indent( ffile, '}\n', indent=indent )


class PovPigment( PovBasicObject ):
    def __init__( self,
                  comment   = None,
                  name      = None,
                  color     = None,
                  rgb       = None,
                  image_map = None,
                  color_map = None,
                  gradient  = None ):
        PovBasicObject.__init__( self, comment )

        self._color     = color
        self._rgb       = rgb
        self._image_map = image_map
        self._color_map = color_map
        self._gradient  = gradient

        self._translate               = None
        self._rotate                  = None
        self._scale                   = None
        self._rotate_before_translate = True


    def set_rotate( self, new_rotate ):
        self._rotate = convertarray2vector( new_rotate )

    def set_translate( self, new_translate ):
        self._translate = convertarray2vector( new_translate )

    def set_rotate_before_translate( self, val ):
        self._rotate_before_translate = val

    def set_scale( self, new_scale ):
        self._scale = convert2vector( new_scale )
        #print self._scale

    def _write_scale( self, ffile, indent=0 ):
        if self._scale is None: return
        self._write_indent( ffile, 'scale <%f,%f,%f>\n' % ( self._scale[0],
                                                     self._scale[1],
                                                     self._scale[2] ),
                                                     indent )

    def _write_translate( self, ffile, indent=0 ):
        if self._translate is None: return
        self._write_indent( ffile, 'translate <%f,%f,%f>\n' % ( self._translate[0],
                                                                self._translate[1],
                                                                self._translate[2] ),
                                                                indent )

    def _write_rotate( self, ffile, indent=0 ):
        if self._rotate is None: return
        self._write_indent( ffile, 'rotate <%f,%f,%f>\n' % ( self._rotate[0],
                                                             self._rotate[1],
                                                             self._rotate[2] ),
                                                             indent )

    def _write_geometrics( self, ffile, indent=0 ):
        self._write_scale( ffile, indent=indent )
        if self._rotate_before_translate:
            self._write_rotate( ffile, indent=indent )
            self._write_translate( ffile, indent=indent )
        else:
            self._write_translate( ffile, indent=indent )
            self._write_rotate( ffile, indent=indent )


    def write_pov( self, ffile, indent ):
        self._write_indent( ffile, 'pigment{\n', indent=indent )
        if ( self._color is not None ):
            self._write_indent( ffile, 'color %s\n' % self._color , indent+1 )
        elif ( self._rgb is not None ):
            self._write_indent( ffile, 'color rgb %s\n' % self._rgb , indent+1 )
        elif ( self._image_map is not None ):
            self._image_map.write_pov( ffile, indent=indent+1 )
            self._write_geometrics( ffile, indent=indent+1 )
        elif ( self._color_map is not None ) and ( self._gradient is not None ):
            self._write_indent( ffile, 'gradient <%f,%f,%f>\n' % ( self._gradient[0],
                                                                  self._gradient[1],
                                                                  self._gradient[2] ), indent+1 )
            self._color_map.write_pov( ffile, indent=indent+1 )
            self._write_geometrics( ffile, indent=indent+1 )

        self._write_indent( ffile, '}\n', indent=indent )


class PovTexture( PovBasicObject ):
    def __init__( self, comment=None, name=None, finish=None, normal=None, pigment=None ):
        PovBasicObject.__init__( self, comment=comment )

        self._finish  = finish
        self._normal  = normal
        self._pigment = pigment


    def set_finish( self, new_finish ):
        self._finish = new_finish


    def set_normal( self, new_normal ):
        self._normal = new_normal


    def set_pigment( self,  pigment ):
        self._pigment = pigment


    def write_pov( self, ffile, indent=0 ):
        PovBasicObject.write_pov( self, ffile, indent )
        self._write_indent( ffile, 'texture{\n', indent )
        self.write_texture( ffile, indent+1 )
        if self._pigment is not None:
            self._pigment.write_pov( ffile, indent=indent+1 )
        if self._normal is not None:
            self._normal.write_pov( ffile, indent=indent+1 )
        if self._finish is not None:
            self._finish.write_pov( ffile, indent=indent+1 )
        self._write_indent( ffile, '}\n', indent )


    def write_texture( self, ffile, indent ):
        pass


class PovTextureRaw( PovBasicObject ):
    def __init__( self, comment=None, text=None ):
        PovBasicObject.__init__( self, comment=comment )
        self._text = text

    def write_pov( self, ffile, indent=0 ):
        if self._text is not None:
            PovBasicObject.write_pov( self, ffile, indent )
            self._write_indent( ffile, 'texture{\n', indent )
            self._write_indent( ffile, self._text, indent+1 )
            self._write_indent( ffile, '}\n', indent )
