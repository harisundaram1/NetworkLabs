from pyorient.types import OrientRecord
from topgenerator.connect_db import *
import abc

class NetworkLabObject(OrientRecord):

	@classmethod
	def __init__(cls):
		cls.__connect_to_db__()
	
	@classmethod
	def __connect_to_db__(cls):
		cls.db = connect()
		print 'db connected'
		return cls.db

	def __init__(self):
		self.db = self.__connect_to_db__()

	def save_vertex():
		return self.db.command('Create vertex '+self.__class__.__name__+' set '+obj_key_values())

	def obj_key_values():
		return key_value_string(self.__dict__)

	@classmethod
	def key_value_string(cls,params={},seperator=','):
		keys = params.keys()
		filtered_keys = []
		for k in keys:
			if ~(k.startswith('_') or k == 'in' or k == 'out'):
				filtered_keys.append(k)
		query_string = ''
		for key in filtered_keys:
			query_string += k+'='+params[k]
			if key != filtered_keys[-1]:
				query_string+=seperator
		print query_string
		return query_string
	
	@classmethod
	def find(cls,self,params={}):
		cls.__connect_to_db__()
		cls.db.command('Select from '+self.__class__.__name__+' where '+cls.key_value_string(params,' and '))

# class User(NetworkLabObject):
# 	def __init__(self):
# 		super(self)
# 		print "User is created"

# 	def save():
# 		print "User saved"

# 	def create():
# 		print "User created"

class Action(NetworkLabObject):
	def __init__(self):
		super(Action,self).__init__()
		print "Action is created"

	def find(self,params={}):
		return super(Action,self).find(self,params)

	def save():
		self.db.command('Create')

# class BaseEntity(NetworkLabObject):
# 	__metaclass__  = abc.ABCMeta

# 	@abc.abstractmethod
# 	def __init__(self):
		# print "Base Entity is created"