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

def parse_xml(path):
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

def parse_policy(path):
  """Read and load the yaml file, similar to parse_xml"""
  try:
    with open(path, encoding= "utf-8") as f:
      policy = yaml.safe_load(f)
  except FileNotFoundError:
    raise InputFileError(f"{path} File not found")
  except yaml.YAMLError:
    raise InputFileError(f"{path} File is not a valid YAML file")
  if policy is None:
    policy = {}
  if isinstance(policy, dict) is False:
    raise InputFileError(f"{path} Policy is not a dict")
  return policy

def str_to_num(os_str):
  """Convert os string to number for comparison"""
  num = os_str.split(".")
  int_num = []
  for d in num:
    int_num.append(int(d))
  return int_num

def os_comp(dev_ver, pol_ver):
  """Compare the os version"""
  os1 = str_to_num(dev_ver)
  os2 = str_to_num(pol_ver)
  while len(os1) < len(os2):
    os1.append(0)
  while len(os2) < len(os1):
    os2.append(0)
  if os1 < os2:
    return True

def policy_check(device, policy):
  """Compare the device to the policy"""
  violations = []
  if "min_os" in policy:
    if device.role not in policy["min_os"]:
      violations.append({"device": device.id, "type": "unknown_role", "role": device.role})
    if device.role in policy["min_os"]:
      os = os_comp(device.os, policy["min_os"][device.role])
      if os is True:
        violations.append({"device": device.id, "type": "os_outdated", "found": device.os, "required": policy["min_os"][device.role]})
  if device.has_owner() is False and policy.get("require_owner"):
    violations.append({"device": device.id, "type": "missing_owner"})
  if "max_down_interfaces" in policy:
    if device.down_count() > policy.get("max_down_interfaces"):
      violations.append({"device": device.id, "type": "too_many_down", "down": device.down_count()})
  return violations

#Functions used for making and writing the audit------------------------------------------------------------------------------------
def role_count(devices):
  """Count how many devices are in each role"""
  role_counter = {}
  for d in devices:
    if d.role in role_counter:
      role_counter[d.role] += 1
    else:
      role_counter[d.role] = 1
  return role_counter

def interface_count(devices):
  """Count the status of interfaces"""
  interface_counter = {"up": 0, "down": 0, "other": 0}
  for d in devices:
    for i in d.interfaces:
      if i == "up":
        interface_counter["up"] += 1
      elif i == "down":
        interface_counter["down"] += 1
      else:
        interface_counter["other"] += 1
  return interface_counter

def make_audit(site, devices, skipped, policy):
  """Build the audit"""
  roles = role_count(devices)
  interface_status = interface_count(devices)
  violations = []
  compliant = []
  for d in devices:
    check = policy_check(d, policy)
    if len(check) == 0:
      compliant.append(d.id)
    else:
      violations.extend(check)

  compliant = sorted(compliant)
  audit = {"site": site, "total_devices": len(devices), "skipped_devices": skipped, "roles": roles, "interfaces": interface_status, "violations": violations, "compliant": compliant}
  return audit

def write_audit(audit):
  """Write the audit"""
  with open("audit.json", "w", encoding= "utf-8") as f:
    json.dump(audit, f, indent=2)
#-----------------------------------------------------------------------------------------------------------------------------
