"""

pypovlib/pypovrayqueue.py

written by: Oliver Cordes 2019-03-04
changed by: Oliver Cordes 2019-03-04

"""

import sys,os

try:
    from client.api import Session
    from client.projects import Project
except:
    print('rayqueue client modules not found!')
    os.exit(-1)


from pypovlib.pypovobjects import *



class RQPovFile(PovFile):
    def __init__(self, filename=None,
                        verbose=False,
                        camera_optimize=False,
                        config=None):
        PovFile.__init__(self,filename=filename,
                            verbose=verbose,
                            camera_optimize=camera_optimize)

        self._session = Session(config=config)



    def write_povfile(self, filename=None):
        # first save the standard file
        PovFile.write_povfile(self, filename=filename)

        # now connects to the RQ service

        if self._session.login():
            print('Successfully logged in to the RQ service!')
        else:
            print('Cannot login into the RQ service!')
