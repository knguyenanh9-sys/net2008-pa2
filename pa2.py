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
