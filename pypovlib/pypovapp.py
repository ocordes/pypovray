"""

pypovlib/pypovapp.py

written by: Oliver Cordes 2019-04-14
changed by: Oliver Cordes 2020-04-04

"""


from pypovlib.pypovobjects import PovFile, print_statistics
from pypovlib.pypovrayqueue import RQPovFile, RQPovAnimation


PovApp_Unknown   = 0
PovApp_Image     = 1
PovApp_Animation = 2



class PovApp(object):
    def __init__(self, **kwargs):

        self._type            = PovApp_Unknown
        self._filename        = None
        self._directory       = None
        self._has_rq          = False
        self._rq_config       = None
        self._rq_project_name = None

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
            elif key == 'directory':
                self._directory = value
            elif key == 'rq_project_name':
                self._rq_project_name = value


        if self._type == PovApp_Image:
            if self._has_rq:
                self._povfile = RQPovFile(filename=self._filename,
                                            config=self._rq_config,
                                            rq_project_name=self._rq_project_name)
            else:
                self._povfile = PovFile(filename=self._filename)
        elif self._type == PovApp_Animation:
            if self._has_rq:
                self._povfile = RQPovAnimation(directory=self._directory,
                                                config=self._rq_config,
                                                rq_project_name=self._rq_project_name)
            else:
                self._povfile = PovAnimation(directory=self._directory)


        else:
            self._povdile = None
            print('This type is not supported yet: type=%i' % self._type)



    def build(self, **kwargs):
        for creator in self._build_list:
            creator()

        if self._povfile is not None:
            self._povfile.do_statistics()
        print_statistics()


    def create(self, **kwars):
        if self._povfile is not None:
            if self._type == PovApp_Image:
                self._povfile.write_povfile(submit=False)
            elif self._type == PovApp_Animation:
                self._povfile.animate(submit=False)


    def run(self, **kwargs):
        if self._povfile is not None:
            if self._type == PovApp_Image:
                self._povfile.write_povfile()
            elif self._type == PovApp_Animation:
                self._povfile.animate()



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


    def add_include(self, incfile):
        if self._povfile is not None:
            self._povfile.add_include(incfile)


    def add_declare(self, key, value):
        if self._povfile is not None:
            self._povfile.add_declare(key, value)


    def add_extra_file(self, files):
        if self._povfile is not None:
            self._povfile.add_extra_file(files)


    def set_lights(self, lights):
        if self._povfile is not None:
            self._povfile.set_lights(lights)


    def set_geometry(self, width, height):
        if self._type == PovApp_Image:
            if self._has_rq:
                self._povfile.set_geometry(width, height)


    def set_fps(self, fps):
        if self._type == PovApp_Animation:
            self._povfile.set_fps(fps)


    def set_frames(self, frames):
        if self._type == PovApp_Animation:
            self._povfile.set_frames(frames)


    def set_duration(self, duration):
        if self._type == PovApp_Animation:
            self._povfile.set_duration(duration)


    def set_project(self, project):
        if self._povfile is not None:
            if self._has_rq:
                self._povfile.set_project(project)


    def set_add_args(self, args):
        if self._povfile is not None:
            if self._has_rq:
                self._povfile.set_add_args(args)
