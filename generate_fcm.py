# Author: Sebastiano Barezzi <barezzisebastiano@gmail.com>
# Modifier: Envoy-Z-Lab <envoyzlab@gmail.com>
# Version: 2.0

from re import search
from typing import Dict
import sys


class Version:
    def __init__(self, version: str):
        self.major, self.minor = version.split(".")
        self.major = int(self.major)
        self.minor = int(self.minor)

    def merge_version(self, other):
        if other.minor > self.minor:
            self.minor = other.minor

    def format(self) -> str:
        version_str = '    <version>'
        if self.minor > 0:
            version_str += f"{self.major}.0-{self.minor}"
        else:
            version_str += f"{self.major}.0"
        version_str += '</version>\n'
        return version_str

    def __str__(self):
        return f"{self.major}.{self.minor}"


class Interface:
    def __init__(self, name: str, instance: str):
        self.name = name
        self.instances = [instance]

    def merge_interface(self, other):
        for instance in other.instances:
            if instance not in self.instances:
                self.instances.append(instance)

    def format(self) -> str:
        result = '    <interface>\n'
        result += f'        <name>{self.name}</name>\n'
        for instance in sorted(self.instances):
            result += f'        <instance>{instance}</instance>\n'
        result += '    </interface>\n'
        return result


class Entry:
    def __init__(self, fqname: str):
        self.type = "HIDL" if "@" in fqname else "AIDL"

        if self.type == "HIDL":
            self.name, version_str = fqname.split("::")[0].split("@")
            interface_part = fqname.split("::")[1]
            interface_name, instance = interface_part.split("/", 1)
            version = Version(version_str)
            self.versions: Dict[int, Version] = {version.major: version}
        else:
            self.name, iface_str = fqname.rsplit(".", 1)
            interface_name, instance = iface_str.split("/", 1)
            self.versions = {}

        interface = Interface(interface_name, instance)
        self.interfaces: Dict[str, Interface] = {interface.name: interface}

    def merge_entry(self, other):
        if self.name != other.name or self.type != other.type:
            raise AssertionError("Mismatched entry during merge.")

        for major, version in other.versions.items():
            if major in self.versions:
                self.versions[major].merge_version(version)
            else:
                self.versions[major] = version

        for name, interface in other.interfaces.items():
            if name in self.interfaces:
                self.interfaces[name].merge_interface(interface)
            else:
                self.interfaces[name] = interface

    def format(self) -> str:
        result = f'<hal format="{self.type.lower()}" optional="true">\n'
        result += f'    <name>{self.name}</name>\n'
        for version in sorted(self.versions.values(), key=lambda v: v.major):
            result += version.format()
        for interface in sorted(self.interfaces.values(), key=lambda i: i.name):
            result += interface.format()
        result += '</hal>\n'
        return result


def main():
    input_file = "fqnames.txt"
    entries: Dict[str, Entry] = {}

    with open(input_file, "r") as f:
        for line in f:
            fqname = line.strip()
            if not fqname or fqname.startswith("#"):
                continue

            match = search(r" @\d+$", fqname)
            if match:
                fqname = fqname.removesuffix(match.group(0))

            entry = Entry(fqname)
            key = f"{entry.type}:{entry.name}"

            if key in entries:
                entries[key].merge_entry(entry)
            else:
                entries[key] = entry

    output = '<?xml version="1.0" encoding="utf-8"?>\n'
    output += '<compatibility-matrix version="2.0" type="framework">\n'
    for entry in sorted(entries.values(), key=lambda e: e.name):
        output += entry.format()
    output += '</compatibility-matrix>\n'

    print(output)


if __name__ == "__main__":
    main()
