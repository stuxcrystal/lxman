import click
from lxman.registry import Lxss, Distribution


class Setting(object):

    def __init__(self, name, internal_name, type):
        self.name = name
        self.internal_name = internal_name
        self.type = type

    def get(self, dist):
        return getattr(dist, self.internal_name)

    def _parse_value(self, value):
        if self.type is bool:
            return value.lower() in ["1", "yes", "true", "on"]
        else:
            try:
                return self.type(value)
            except ValueError:
                return False

    def set(self, dist, value):
        if self.type is None:
            return False

        var = self._parse_value(value)

        setattr(dist, self.internal_name, var)
        return True


class DefaultDistributionSetting(Setting):

    def __init__(self, name):
        super(DefaultDistributionSetting, self).__init__(name, None, bool)

    def get(self, dist):
        return Lxss.default.guid == dist.guid

    def set(self, dist, value):
        var = self._parse_value(value)
        if not var:
            return False
        Lxss.default = dist
        return True

class EnvironmentVariableSetting(Setting):

    def __init__(self, name):
        super(EnvironmentVariableSetting, self).__init__(name, 'environment', None)

    def get(self, dist):
        return [f"{k}={v}" for k, v in dist.environment.items()]


SETTINGS = [
    Setting("name",                'name',                str),
    Setting("guid",                'guid',                None),
    Setting("default-uid",         'default_user',        int),
    Setting("command-line",        'cmdline',             str),
    Setting("state",               "state",               int),
    Setting("base-path",           "base_path",           str),
    Setting("package-family-name", "package_family_name", str),
    EnvironmentVariableSetting('environment'),
    DefaultDistributionSetting('default')
]


class _Dist(click.ParamType):
    name = "distribution"

    def convert(self, value, param, ctx):
        if isinstance(value, Distribution):
            return value

        try:
            return Lxss[value]
        except KeyError:
            self.fail("Unknown distribution: %s" % value)

Dist = _Dist()
