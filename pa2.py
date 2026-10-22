#Khoa Nguyen ID: 041238009
import sys
import json
import xml.etree.ElementTree as ET
import yaml

class Device:
  """Class containing information about a device"""
  def __init__(self, id, role, os, owner, interfaces):
    """Constructor for the Device class"""
    self.id = id
    self.role = role
    self.os = os
    self.owner = owner
    self.interfaces = interfaces
  
  def has_owner(self):
    """Check if the device has an owner"""
    if self.owner is None:
      return False
    owner = self.owner.strip()
    if owner == "":
      return False
    return True

  def down_count(self):
    """Count how many interfaces are down"""
    counter = 0
    for d in self.interfaces:
      if d == "down":
        counter += 1
    return counter
  
class InputFileError(Exception):
  """Custom exception for input file error"""

def parse(path):
  """Read and load the xml file, then parse the data into a list of Device objects, return the number of skipped devices and the site name"""
  try:
    parsed = ET.parse(path)
  except FileNotFoundError:
    raise InputFileError(f"{path} File not found")
  except ET.ParseError:
    raise InputFileError(f"{path} File is not a valid XML file")
  parsed_root = parsed.getroot()
  site = parsed_root.get("site")
  devices = []
  skipped_devices = 0
  for d in parsed_root.findall("device"):
    if d.get("id") is None:
      skipped_devices += 1
      continue
    id = d.get("id")
    role = d.get("role")
    os = d.get("os")
    owner = d.find("owner")
    if owner is not None:
      owner = owner.text
    interfaces = []
    for i in d.findall("interface"):
      interfaces.append(i.get("status"))
    devices.append(Device(id, role, os, owner, interfaces))
  return devices, skipped_devices, site

