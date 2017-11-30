# -*- encoding: utf-8 -*-

from collections import UserDict
from itertools import count
import shutil
import winreg
import uuid

PATH = "Software\\Microsoft\\Windows\\CurrentVersion\\Lxss"
KEY = winreg.HKEY_CURRENT_USER


class RegistryDescriptor(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, clazz):
        key = instance._key()
        if key is not None:
            return self._get_value_by_registry(key)
        return self._get_value_by_vartable(instance, key)

    def __set__(self, instance, value):
        key = instance._key("", winreg.KEY_WRITE)
        if key is not None:
            return self._set_value_by_registry(key, value)

    def _get_value_by_registry(self, key):
        with key as k:
            try:
                value, _ = winreg.QueryValueEx(k, self.name)
            except FileNotFoundError:
                return None
            return value

    def _set_value_by_registry(self, key, value):
        if isinstance(value, int):
            type = winreg.REG_DWORD
        elif isinstance(value, (list, tuple)):
            type = winreg.REG_MULTI_SZ
        else:
            type = winreg.REG_SZ

        with key as k:
            winreg.SetValueEx(k, self.name, 0, type, value)

    def _get_value_by_vartable(self, instance, key):
        return vars(instance)[key]


class EnvironmentVariables(UserDict):

    def __init__(self, distribution):
        super(EnvironmentVariables, self).__init__()
        self.distribution = distribution
        self.reload()

    def _save_values(self):
        return (f"{v[0]}={v[1]}" for v in self.data.items())

    def save(self):
        self.distribution.default_environment = list(self._save_values())

    def reload(self):
        self.clear()
        self.update(dict(
            v.split("=", 1) for v in self.distribution.default_environment
        ))


class Distribution(object):

    @classmethod
    def create(cls, name, source_path):
        guid = "{%s}"%uuid.uuid4()
        with winreg.CreateKey(KEY, f"{PATH}\\{guid}") as k:
            winreg.SetValueEx(k, 'State', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(k, 'DistributionName', 0, winreg.REG_SZ, name)
            winreg.SetValueEx(k, 'BasePath', 0, winreg.REG_SZ, source_path)
            winreg.SetValueEx(k, 'DefaultUid', 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(k, 'Version', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(k, 'KernelCommandLine', 0, winreg.REG_SZ, 'BOOT_IMAGE=/kernel init=/init ro')
            winreg.SetValueEx(k, 'DefaultEnvironment', 0, winreg.REG_MULTI_SZ, [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            ])
        return cls(guid)

    def __init__(self, guid=""):
        self.guid = guid

    def _key(self, sub="", privileges=winreg.KEY_READ):
        if not self.guid:
            return None

        if sub:
            sub = "\\" + sub
        return winreg.OpenKey(KEY, PATH+f"\\{self.guid}"+sub, 0, privileges)

    name                = RegistryDescriptor("DistributionName")
    base_path           = RegistryDescriptor("BasePath")
    default_user        = RegistryDescriptor("DefaultUid")
    default_environment = RegistryDescriptor("DefaultEnvironment")
    cmdline             = RegistryDescriptor("KernelCommandLine")
    flags               = RegistryDescriptor("Flags")
    package_family_name = RegistryDescriptor("PackageFamilyName")
    _state              = RegistryDescriptor("State")
    version             = RegistryDescriptor("Version")

    @property
    def environment(self):
        return EnvironmentVariables(self)

    def launch_params(self, params=("/bin/bash",)):
        return [shutil.which("wsl.exe"), f"{self.guid}"] + list(params)

    def __repr__(self):
        return f"<Distribution '{self.name}' guid:{self.guid}>"

    def delete(self):
        with Lxss._key('', winreg.KEY_WRITE) as k:
            winreg.DeleteKey(k, self.guid)

    @property
    def state(self):
        st = self._state
        if st == 1:
            return "Ready"
        elif st == 3:
            return "Installing"
        return "Unknown:" + str(st)

    @state.setter
    def state(self, value):
        if isinstance(value, int):
            self._state = value
            return

        value = value.lower()
        if value == "ready":
            self._state = 1
        elif value == "installing":
            self._state = 3
        else:
            self._state = value

    def __enter__(self):
        self._state = 3
        return self

    def __exit__(self, *exc):
        self._state = 1
        return False


class _Lxss(object):
    def _key(self, sub="", privileges=winreg.KEY_READ):
        if sub:
            sub = "\\" + sub
        return winreg.OpenKey(KEY, PATH+sub, 0, privileges)

    default_distribution = RegistryDescriptor("DefaultDistribution")

    @property
    def default(self):
        return Distribution(self.default_distribution)

    @default.setter
    def default(self, value):
        self.default_distribution = value.guid

    def __iter__(self):
        for i in count():
            with self._key() as k:
                try:
                    name = winreg.EnumKey(k, i)
                except OSError as e:
                    if e.winerror != 259:
                        raise
                    break
            yield Distribution(name)

    def get(self, value, default=None):
        for distribution in self:
            if value.startswith("{") and value.endswith("}"):
                if distribution.guid.lower() == value.lower():
                    return distribution
            else:
                if distribution.name == value:
                    return distribution
        return default

    def __getitem__(self, value):
        value = self.get(value, None)
        if value is None:
            raise KeyError("Unknown distribution")
        return value


Lxss = _Lxss()
