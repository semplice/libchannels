# -*- coding: utf-8 -*-
#
# libchannels - update channels management library
# Copyright (C) 2015 Eugenio "g7" Paolantonio
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

class Relation:
	
	"""
	A Relation() is the base relation object.
	You should use one of the relations subclassing this class (e.g. Dependency)
	"""
	
	def __init__(self, target):
		"""
		Initializes the relation.
		"""
		
		self.target = target


	def __eq__(self, other):
		"""
		Returns True if the dependencies are equal, False if not.
		"""
		
		if type(other) == bool:
			# Bool comparison, just test for the __bool__ condition
			return other == self.__bool__()
		else:
			# Assume this is another relation
			return self.target == other.target
	
class Dependency(Relation):
	
	"""
	The Dependency() relation handles a dependency between two channels.
	"""
	
	def __init__(self, target):
		"""
		Initializes the relation.
		"""
		
		super().__init__(target)
	
	def __bool__(self):
		"""
		Returns True if the dependency is statisfied, False if not.
		"""
		
		return self.target.enabled

