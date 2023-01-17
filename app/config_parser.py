"""define ConfigParser object to read app configuration arguments"""
from configparser import ConfigParser

configuration = ConfigParser()
configuration.read("settings.ini")
