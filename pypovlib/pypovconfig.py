# pypovconfig.py
#
# written by: Oliver Cordes 2020-04-18
# changed by: Oliver Cordes 2020-04-18



class Settings(object):
    def isfloat(self, v, vmin=None, vmax=None):
        if not isinstance(v, (float,int)):
            return -1
        if vmin is not None:
            if v < vmin:
                return -2
        if vmax is not None:
            if v > vmax:
                return -3
        return 0

    def isint(self, v, vmin=None, vmax=None):
        if not isinstance(v, int):
            return -1
        if vmin is not None:
            if v < vmin:
                return -2
        if vmax is not None:
            if v > vmax:
                return -3
        return 0

    def getvalues(self):
        # select all class attributes which are not callable and
        # don't start with a _ which indicates an internal variable
        vars = [attr for attr in dir(self) if (not attr.startswith('_')) and (not callable(getattr(self, attr)))]
        # copy all values from the vars list into a dictonary
        return  {attr:getattr(self,attr) for attr in vars}


global_settings_pre  = 0
global_settings_post = 1
global_settings_mid  = 2

defined_keys = [
                 'assumed_gamma',
                 'ambient_light'
               ]

class GlobalSettings(Settings):
    def __init__(self):
        self._settings = global_settings_pre


    def verify_key(self, key, value):
        if key in defined_keys:
            return True
        else:
            print('WARNING: GlobalSettings: \'{}\' not defined. Ignored!'.format(key))
            return False


    def write_pov(self, f):
        d = self.getvalues()

        if len(d.keys()) > 0:
            f.write('global_settings {\n')
            for k in d.keys():
                if self.verify_key(k, d[k]):
                    f.write('    {} {}\n'.format(k, d[k]))
            f.write('}\n\n')


    def write_pov_pre(self, f):
        if self._settings == global_settings_pre:
            self.write_pov(f)

    def write_pov_mid(self, f):
        if self._settings == global_settings_mid:
            self.write_pov(f)

    def write_pov_post(self, f):
        if self._settings == global_settings_post:
            self.write_pov(f)
