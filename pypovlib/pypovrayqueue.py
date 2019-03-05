"""

pypovlib/pypovrayqueue.py

written by: Oliver Cordes 2019-03-04
changed by: Oliver Cordes 2019-03-05

"""

import sys,os

import tarfile
import uuid

try:
    from client.api import Session
    from client.projects import Project
except:
    print('rayqueue client modules not found!')
    os.exit(-1)


from pypovlib.pypovobjects import *


# helper functions
"""

"""
def tarinfo_reset(tarinfo):
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = 'root'
    return tarinfo



class RQPovFile(PovFile):
    def __init__(self, filename=None,
                        verbose=False,
                        camera_optimize=False,
                        config=None,
                        rq_project_name=None):
        PovFile.__init__(self,filename=filename,
                            verbose=verbose,
                            camera_optimize=camera_optimize)

        self._session = Session(config=config)


        self._rq_project_name = rq_project_name
        self._rq_projects = None
        self._rq_project  = None


    def _load_projects(self):
        self._rq_projects = Project.query(self._session)


    def _select_rq_project(self):
        if self._rq_project_name is None:
            print('All projects:')
            for p in self._rq_projects:
                print('<%4i> %s' % (p.id, p.name))

            print('-'*80)
            user_input = input('Enter the project id:')
            print()
            try:
                id = int(user_input)
                return self._rq_projects[id]
            except:
                pass
            return None
        else:
            for p in self._rq_projects:
                if p.name ==  self._rq_projectname:
                    return p
            return None


    def _create_rq_image_file(self, filename, listoffiles):
        with tarfile.open(filename, 'w:gz') as tar:
            for f in listoffiles:
                tar.add(f, filter=tarinfo_reset)


    def write_povfile(self, filename=None):
        # first save the standard file
        PovFile.write_povfile(self, filename=filename)


        # generates a temptile name

        tempfile = os.path.join('/tmp','image_%s.tar.gz' %(str(uuid.uuid4())))

        listoffiles = []
        listoffiles.append(self._filename)
        self._create_rq_image_file(tempfile, listoffiles)

        # now connects to the RQ service

        if not self._session.login():
            print('Cannot login into the RQ service!')
            return

        print('Successfully logged in to the RQ service!')
        self._load_projects()
        self._rq_project_id = self._select_rq_project()
