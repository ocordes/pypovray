"""

pypovlib/pypovrayqueue.py

written by: Oliver Cordes 2019-03-04
changed by: Oliver Cordes 2019-04-09

"""

import sys, os

import configparser
import tarfile
import uuid
import time

try:
    from rq_client.api import Session
    from rq_client.projects import Project
    from rq_client.images import Image
    from rq_client.files import File
except:
    print('rayqueue client modules not found!')
    sys.exit(-1)


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
                        rq_project_name=None,
                        width=640,
                        height=480,
                        timeout=3600,
                        sleep=5):
        PovFile.__init__(self,filename=filename,
                            verbose=verbose,
                            camera_optimize=camera_optimize)

        self._session = Session(config=config, verbose=True)


        self._rq_project_name = rq_project_name
        self._rq_projects = None
        self._rq_project  = None

        self._width = width
        self._height = height

        self._timeout = timeout
        self._sleep = sleep


    def _load_projects(self):
        self._rq_projects = Project.queryall(self._session)


    def _select_rq_project(self):
        if self._rq_project_name is None:
            print('All projects:')
            for p in self._rq_projects:
                print('<%4i> %s' % (p.id, p.name))

            print('-'*80)
            user_input = input('Enter the project id:')
            print()
            try:
                id = int(user_input)-1   # count from zero!
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


    def _create_master_ini(self):

        pre, ext = os.path.splitext(self._filename)
        outname = pre + '.png'

        data = { 'scene': self._filename,
                 'width': self._width,
                 'height': self._height,
                 'outfile': outname }

        config = configparser.ConfigParser()
        config['DEFAULT'] = data
        filename = 'scene.ini'
        with open(filename, 'w') as configfile:
            config.write(configfile)

        return filename

    def _wait_until_ready(self):
        running_time = 0
        while running_time <= self._timeout:
            self._rq_project.update(self._session)
            if self._rq_project.status() == 'Finished':
                return True

            print('Waiting ... %i/%i' % (running_time, self._timeout))
            time.sleep(self._sleep)
            running_time += self._sleep

        print('Running into timeout!')


    def _download_file(self, fileid, directory='.'):
        if fileid != -1:
            dbfile = File.get_db_by_id(self._session, fileid)
            md5sum = dbfile.md5sum

            status, filename = File.get_by_id(self._session, fileid,
                                            directory, md5sum=md5sum)
            print('Downloaded \'%s\'' % filename )



    def _download_files(self, image, directory='.'):
        # update all informations ;-)
        image.update(self._session)

        if hasattr(image, 'render_image_id'):
            self._download_file(image.render_image_id)
        if hasattr(image, 'log_file_id'):
            self._download_file(image.log_file_id)

        print('error code of rendering process: %i' % image.error_code)



    def write_povfile(self, filename=None):
        # first save the standard file
        PovFile.write_povfile(self, filename=filename)


        # generates a temptile name

        #tempfile = os.path.join('/tmp','image_%s.tar.gz' %(str(uuid.uuid4())))
        tempfile = os.path.join('/tmp','image_%s.tar.gz' %('simple'))

        listoffiles = []
        listoffiles.append(self._filename)
        listoffiles.append(self._create_master_ini())

        self._create_rq_image_file(tempfile, listoffiles)

        # now connects to the RQ service

        if not self._session.login():
            print('Cannot login into the RQ service!')
            return

        print('Successfully logged in to the RQ service!')
        self._load_projects()
        self._rq_project = self._select_rq_project()


        # clear old files...
        ret = self._rq_project.clear_images(self._session)
        if ret:
            print('All old files cleared!')
        else:
            print('Something went wrong while clearing old files!')

        # upload the image description

        do_trying = True
        while do_trying:
            image_id = Image.create(self._session, self._rq_project.id, tempfile)

            if image_id != -1:
                do_trying = False
            else:
                print('Image creation failed! Possible solutions:')
                print('------------------------------------------')
                print(' <1> Reset project')
                user_input = int(input('Your choice: '))

                if user_input != 1:
                    do_trying = False
                else:
                    self._rq_project.reset(self._session)

        # end while


        # remove temporary file
        os.remove(tempfile)

        if image_id != -1:
            print('New image with id=%i created' % image_id)

            # this is the code for testing the loop
            # waiting for the image to be ready!
            image = Image.query(self._session, image_id)

            started = self._rq_project.start_rendering(self._session)

            if started:
                print('Project switched to rendering mode, waiting for worker ...')


                if self._wait_until_ready():
                    # Download files
                    self._download_files(image)
                else:
                    print('File is not rendered within the time frame of %i seconds' %self._timeout)

            else:
                print('Project cannot be switched to rendering mode!')
        else:
            print('Image couldn\'t be created!')
