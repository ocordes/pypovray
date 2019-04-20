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
    from rq_client.projects import Project, PROJECT_TYPE_IMAGE, PROJECT_TYPE_ANIMATION
    from rq_client.images import Image
    from rq_client.files import File
except:
    print('rayqueue client modules not found!')
    sys.exit(-1)


from pypovlib.pypovobjects import *
from pypovlib.pypovanimation import *


# helper functions
"""

"""
def tarinfo_reset(tarinfo):
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = 'root'
    return tarinfo



class RQPovObj(object):
    def __init__(self, config=None,
                       rq_project_name=None,
                       timeout=3600,
                       sleep=5,
                       width=640,
                       height=480):

        # RQ specific information
        self._session = Session(config=config, verbose=True)

        self._rq_project_name = rq_project_name
        self._rq_projects = None
        self._rq_project  = None

        self._timeout = timeout
        self._sleep = sleep

        self._width = width
        self._height = height


    def set_geometry(self, width, height):
        if width is not None:
            self._width = width
        if height is not None:
            self._height = height


    def _rq_login(self):
        if not self._session.login():
            print('Cannot login into the RQ service!')
            return False

        print('Successfully logged in to the RQ service!')

        return True


    def _select_rq_project(self, project_type):
        self._rq_projects = Project.queryall(self._session)
        if self._rq_project_name is not None:
            for p in self._rq_projects:
                if p.name ==  self._rq_projectname:
                    return p

        # ask for selecting a project
        retry = True
        while retry:
            print('All projects:')
            for p in self._rq_projects:
                print('<%4i> %s' % (p.id, p.name))

            print('-'*80)
            user_input = input('Enter the project id: ')
            print()

            user_input = int(user_input)

            # check for user abort
            if user_input == 0:
                return None

            id = user_input-1   # count from zero!

            #checks
            if id >= len(self._rq_projects):
                print('Index outside of list. Please retry!')
            else:
                p = self._rq_projects[id]
                if p.project_type != project_type:
                    print('Wrong project type! Select a new one!')
                else:
                    return self._rq_projects[id]

            print()



    def _create_image_archive(self, filename, listoffiles):
        with tarfile.open(filename, 'w:gz') as tar:
            for f in listoffiles:
                tar.add(f, filter=tarinfo_reset)


    def _create_master_ini(self, filename):

        pre, ext = os.path.splitext(filename)
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


    def _create_image(self, filename):
        # generates a tempfile name

        tempfile = os.path.join('/tmp','image_%s.tar.gz' %('simple'))

        listoffiles = []
        listoffiles.append(filename)
        listoffiles.append(self._create_master_ini(filename))

        self._create_image_archive(tempfile, listoffiles)

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


        if image_id == -1:
            print('Image couldn\'t be created!')
            image = None
        else:
            print('New image with id=%i created' % image_id)

            # this is the code for testing the loop
            # waiting for the image to be ready!
            image = Image.query(self._session, image_id)
        return image


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


    def _wait_download_files(self, list_of_images, directory='.'):
        new_list = []
        for image in list_of_images:
            image.update(self._session)
            print(image.status())
            if image.status() == 'Finished':
                if hasattr(image, 'render_image_id'):
                    self._download_file(image.render_image_id, directory=directory)
                if hasattr(image, 'log_file_id'):
                    self._download_file(image.log_file_id, directory=directory)
                print('error code of rendering process: %i' % image.error_code)
            else:
                new_list.append(image)



class RQPovFile(PovFile, RQPovObj):
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

        RQPovObj.__init__(self, config=config,
                               rq_project_name=rq_project_name,
                               timeout=timeout,
                               sleep=sleep,
                               width=width,
                               height=height)


    def write_povfile(self, filename=None):
        # first save the standard file
        PovFile.write_povfile(self, filename=filename)


        print('Submitting image to RQ for rendering ...')

        # now connects to the RQ service
        if not self._rq_login():
            return

        self._rq_project = self._select_rq_project(PROJECT_TYPE_IMAGE)

        if self._rq_project is None:
            print('User abort!')
            return

        # clear old files...
        ret = self._rq_project.clear_images(self._session)
        if ret:
            print('All old files cleared!')
        else:
            print('Something went wrong while clearing old files!')


        # compile all data and create a rq image
        image = self._create_image(self._filename)

        if image is None:
            return

        # switch the project into rendering mode
        started = self._rq_project.start_rendering(self._session)

        if started:
            print('Project switched to rendering mode, waiting for worker ...')


            if self._wait_until_ready():
                # Download files
                #self._download_files(image)
                self._wait_download_files([image])
            else:
                print('File is not rendered within the time frame of %i seconds' %self._timeout)

        else:
            print('Project cannot be switched to rendering mode!')




class RQPovAnimation(PovAnimation, RQPovObj):
    def __init__(self, directory=None,
                        verbose=False,
                        camera_optimize=False,
                        config=None,
                        rq_project_name=None,
                        width=640,
                        height=480,
                        timeout=3600,
                        sleep=5):
        PovAnimation.__init__(self, directory=directory,
                                verbose=verbose,
                                camera_optimize=camera_optimize)

        RQPovObj.__init__(self, config=config,
                               rq_project_name=rq_project_name,
                               timeout=timeout,
                               sleep=sleep,
                               width=width,
                               height=height)

        self._animation_files = []


    def write_povfile(self, filename=None):
        # first save the standard file
        PovFile.write_povfile(self, filename=filename)

        self._animation_files.append(self._filename)


    def animate( self, frames = None, duration = None, fps = None ):
        PovAnimation.animate(self, frames=frames, duration=duration, fps=fps)

        print('Submitting image to RQ for rendering ...')


        print(self._animation_files)
