#
# pypovlib/pypovblob.py
#
# written by: Oliver Cordes 2019-08-03
# changed by: Oliver Cordes 2019-08-03
#
#

from pypovlib import *              # thought this should be enough
from pypovlib.pypovanimation import *
from pypovlib.pypovweather import *
from pypovlib.pypovobjects import *
from pypovlib.pypovtextures import *
from pypovlib.pypovlights import *
from pypovlib.pypovtools import *
from pypovlib.pypovcamera import *



class PovBlob(PovCSGObjectList):
    _name = 'Blob'
    def __init__(self, threshold=1., comment=None):
        PovCSGObjectList.__init__(self, comment=comment)
        self._threshold = threshold

    def _verify_object(self, val):
        if PovCSGObjectList._verify_object(self, val):
            if hasattr(val, '_blob'):
                return val._blob
        print('_verify_object:' +
              ' A none blob object should be added. Object will be ignored!')
        return False

    def write_pov( self, ffile, indent = 0 ):
        if len(  self._items ) == 0:
            print('Blob structure needs at least one item to proceed!')
            #raise TypeError('Union structure needs at least one item to proceed
            self._write_indent(ffile, '//empty blob', indent)
            return
        PovCSGObjectList.write_pov(self, ffile, indent=indent)
        self._write_indent(ffile, 'blob{\n', indent)

        self._write_indent(ffile, 'threshold %f' % self._threshold,
            indent=indent+1)

        self._write_items(ffile, indent+1)
        self._write_attributes(ffile, indent+1 )
        self._write_indent(ffile, '}\n', indent )


    def do_statistics(self):
        PovBaseList.do_statistics(self)
        self.add_stat_count('Blob')


class PovBlobSphere(PovCSGSphere):
    _blob = True
    _name = 'BlobSphere'
    def __init__(self, xyz, radius, strength=1., comment=None ):
        PovCSGSphere.__init__(self, xyz, radius, comment=comment)
        self._strength = strength


    def write_pov(self, ffile, indent = 0):
        PovCSGObject.write_pov(self, ffile, indent=indent)
        self._write_indent(ffile, 'sphere{\n', indent)
        self._write_indent(ffile,
                           '%s, %f, %f\n' % (self._xyz,
                                             self._radius,
                                             self._strength), indent+1)
        self._write_attributes(ffile, indent+1)
        self._write_indent(ffile, '}\n', indent)
