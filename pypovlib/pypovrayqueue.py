"""

pypovlib/pypovrayqueue.py

written by: Oliver Cordes 2019-03-04
changed by: Oliver Cordes 2019-04-21

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
        logfile = pre + '.log'

        data = { 'scene': filename,
                 'width': self._width,
                 'height': self._height,
                 'outfile': outname,
                 'logfile': logfile }

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


    def _create_images_from_filenames(self, filenames):
        images = []
        missed = 0
        # compile all data and create a rq image
        for filename in filenames:
            print('Submitting %s ...' % filename)
            image = self._create_image(filename)
            if image is not None:
                images.append(image)
            else:
                missed += 1
                if missed == 3:
                    print('Too many errors, submitting aborted!')
                    return None

        if len(images) == 0:
            return None

        return images


    def _download_file(self, fileid, directory='.'):
        if fileid != -1:
            dbfile = File.get_db_by_id(self._session, fileid)
            md5sum = dbfile.md5sum

            status, filename = File.get_by_id(self._session, fileid,
                                            directory, md5sum=md5sum)
            print('Downloaded \'%s\'' % filename )


    def _download_files(self, list_of_images, nr_images, directory='.', verbose=False):
        new_list = []
        im_queued    = 0
        im_rendering = 0
        im_inlist    = 0
        for image in list_of_images:
            image.update(self._session)
            #if verbose:
            #    print('Image status: %s' % image.status())
            if image.status() == 'Finished':
                if hasattr(image, 'render_image_id'):
                    self._download_file(image.render_image_id, directory=directory)
                if hasattr(image, 'log_file_id'):
                    self._download_file(image.log_file_id, directory=directory)
                print('error code of rendering process: %i' % image.error_code)
            else:
                new_list.append(image)
                if image.status() == 'Queued':
                    im_queued += 1
                if image.status() == 'Rendering':
                    im_rendering += 1
                im_inlist += 1

        if verbose:
            print('Queued    : %5i' % im_queued)
            print('Rendering : %5i' % im_rendering)
            print('Finished  : %5i' % (nr_images - im_inlist))

        return new_list


    """
    _wait_download_files

    takes a python list of images and waits until all images are processed!
    Images which are finished will be downloaded as soon as possible

    :param list_of_images : python-list of submitted images
    :param directory      : directory for the results
    """
    def _wait_download_files(self, list_of_images, directory='.'):
        running_time = 0
        is_running = True
        nr_images = len(list_of_images)
        while is_running:
            # update project data
            self._rq_project.update(self._session)
            list_of_images = self._download_files(list_of_images, nr_images, directory=directory, verbose=True)
            is_running = self._rq_project.status() != 'Finished'

            if is_running != False:
                if len(list_of_images) == 0:
                    # all images downloaded?
                    print('Images all downloaded but project is still not finished!')

                else:
                    if running_time >= self._timeout:
                        print('Running into timeout!')
                        return False
                    else:
                        print('Waiting ... %i/%i' % (running_time, self._timeout))
                        time.sleep(self._sleep)
                        running_time += self._sleep
        return True


    """
    _prepare_submit

    does the preperations, login, project selection, project clearing

    :param project_type : image or animation
    """
    def _prepare_submit(self, project_type):
        # now connects to the RQ service
        if not self._rq_login():
            return False

        self._rq_project = self._select_rq_project(project_type)

        if self._rq_project is None:
            print('User abort!')
            return False

        # clear old files...
        ret = self._rq_project.clear_images(self._session)
        if ret:
            print('All old files cleared!')
        else:
            print('Something went wrong while clearing old files!')
            return False

        return True


    """
    _render_download

    takes a python list of submitted images, starts the queuing and waits
    until all images are processed and download the files

    :param images   : python-list of submitted images
    :param diretory : directory for all results
    """
    def _render_download(self, images, directory='.'):
        # switch the project into rendering mode
        started = self._rq_project.start_rendering(self._session)

        if started:
            print('Project switched to rendering mode, waiting for worker ...')

            if self._wait_download_files(images, directory=directory):
                print('Rendering was successful!')
                return True
            else:
                print('File is not rendered within the time frame of %i seconds' %self._timeout)
                return False
        else:
            print('Project cannot be switched to rendering mode!')

        return False


    """
    rq_execute

    the summary which is necessary to render a single image or an
    image set for an animation. Flexible and easy

    :param project_type: type of project necessary, image or animation
    :param filenames   : python-list of filenames to render
    :param directory   : optional the directory to store the results
    """
    def rq_execute(self, project_type, filenames, directory='.'):

        print('Submitting image(s) to RQ for rendering ...')

        if self._prepare_submit(project_type) == False:
            return False

        images = self._create_images_from_filenames(filenames)

        if images is not None:
            return self._render_download(images, directory=directory)

        return False



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


    def write_povfile(self, filename=None, submit=True):
        # first save the standard file
        PovFile.write_povfile(self, filename=filename)

        if submit:
            self.rq_execute(PROJECT_TYPE_IMAGE, [self._filename], directory='.')

        return



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


    def animate(self, frames = None, duration = None, fps = None, submit=True):
        PovAnimation.animate(self, frames=frames, duration=duration, fps=fps)

        if submit:
            self.rq_execute(PROJECT_TYPE_ANIMATION, self._animation_files, directory=self._directory)

        return
