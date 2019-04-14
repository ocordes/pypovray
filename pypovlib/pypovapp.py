"""

pypovlib/pypovapp.py

written by: Oliver Cordes 2019-04-14
changed by: Oliver Cordes 2019-04-14

"""


from pypovlib.pypovobjects import PovFile, print_statistics
from pypovlib.pypovrayqueue import RQPovFile


PovApp_Unknown   = 0
PovApp_Image     = 1
PovApp_Animation = 2



class PovApp(object):
    def __init__(self, **kwargs):

        self._type       = PovApp_Unknown
        self._filename   = None
        self._has_rq     = False
        self._rq_config  = None

        self._build_list = []

        # handle all arguments
        for key, value in kwargs.items():
            if key == 'app_type':
                self._type = value
            elif key == 'filename':
                self._filename = value
            elif key == 'rq_config':
                self._rq_config = value
                self._has_rq = True
            elif key == 'has_rq':
                self._has_rq = value


        if self._type == PovApp_Image:
            if self._has_rq:
                self._povfile = RQPovFile(filename=self._filename,
                                            config=self._rq_config)
            else:
                self._povfile = PovFile(filename=self._filename)


        else:
            self._povdile = None
            print('This type is not supported yet: type=%i' % self._type)



    def build(self, **kwargs):
        for creator in self._build_list:
            creator()

        if self._povfile is not None:
            self._povfile.do_statistics()
        print_statistics()



    def run(self, **kwargs):
        if self._povfile is not None:
            self._povfile.write_povfile()



    # decorator handling tool
    def creator(self, f):
        self._build_list.append(f)
        return f


    # some wrapper functions
    def set_prefix_file(self, filename):
        if self._povfile is not None:
            self._povfile.set_prefix_file(filename)


    def set_camera(self, camera):
        if self._povfile is not None:
            self._povfile.set_camera(camera)


    def add(self, povobjects):
        if self._povfile is not None:
            self._povfile.add(povobjects)
