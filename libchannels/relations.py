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
	
	def get_name(self):
		"""
		Returns the name of the target channel.
		"""
		
		return self.target.channel_name
		
	def __bool__(self):
		"""
		Returns True if the dependency is statisfied, False if not.
		"""
		
		return self.target.enabled

class Conflict(Relation):
	
	"""
	The Conflict() relation handles a conflict between two channels.
	"""
	
	def get_name(self):
		"""
		Returns the name of the target channel.
		"""
		
		return self.target.channel_name
	
	def __bool__(self):
		"""
		Returns True if the conflict is clear, False if not.
		"""
		
		return (not self.target.enabled)

class ProviderRelation(Relation):
	
	"""
	The ProviderRelation() relation handles a relation between a channel and
	a provider.
	"""
	
	def __init__(self, requirer, target, channels):
		"""
		Initializes the relation.
		"""
		
		self.requirer = requirer
		self.target = target
		self.channels = channels

	def get_name(self):
		"""
		Returns the name of the target channel.
		"""
		
		return self.target.provider_name
	
	def is_provider_enabled(self, channel):
		"""
		Returns True if the given channel provides the provider and is
		enabled, False if not.
		"""
		
		if (
			not channel.endswith(".provider") and # Check on channels
			not self.requirer.channel_name == channel and # Ensure we aren't checking ourselves
			self.target.provider_name in self.channels[channel].get_providers() and # Actual provider check 
			self.channels[channel].enabled # If the channel is not enabled, don't worry
		):
			return True
		else:
			return False
		
	def get_current_provider_channel(self):
		"""
		Returns the channel that currently provides the provider.
		"""
		
		for channel in self.channels:
			if self.is_provider_enabled(channel):
				return channel
		
		return None

	def __bool__(self):
		"""
		Returns True if the provider is not statisfied, False if it is.
		"""
		
		return (not (True in [True for x in self.channels if self.is_provider_enabled(x)]))
