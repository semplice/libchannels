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

import configparser

import libchannels.common

from aptsources.sourceslist import SourceEntry

class Channel(configparser.ConfigParser):
	
	"""
	A Channel is, basically, a set of Debian repositories with Dependency
	and "Provider" support.
	
	A channel should have the ".channel" extension and it should look like this:
	
		[channel]
		name = Channel name
		description = Channel description
		depends = eventual-dependencies
		provides = eventual-provider
		
		[repo1]
		default_mirror = http://path/to/mirror
		origin = Repository origin, as given in the Release file
		codename = distribution codename
		components = repository components

		[repo2]
		default_mirror = http://path/to/mirror
		origin = Repository origin, as given in the Release file
		codename = distribution codename
		components = repository components
		
		[repo3]
		...
	
	Enabling a channel will enable every repository in the set.
	"""
		
	def __init__(self, channel_name):
		"""
		Initializes the class.
		"""
		
		super().__init__()
		
		self.repositories = {}
		
		self.channel_name = channel_name
		
		self.read("./%s.channel" % channel_name) # FIXME: Should properly retrieve the path!
		
		# Build repository dictionary
		for repository in self.sections():
			if repository == "channel":
				continue
			
			self.repositories[repository] = None # check() will eventually change that to the appropriate SourceEntry
	
	def disable(self):
		"""
		Disables enitrely the channel.
		"""
		
		print("Disabling %s channel..." % self.channel_name)
		
		for repository, source_entry in self.repositories.items():
			if source_entry: source_entry.set_enabled(False)
		
		libchannels.common.sourceslist.save()
	
	def enable(self):
		"""
		Enables the channel.
		"""
		
		print("Enabling %s channel..." % self.channel_name)
		
		for repository, source_entry in self.repositories.items():
			if self.is_proposed(repository):
				# Proposed components should be enabled manually
				continue
			
			if type(source_entry) == SourceEntry:
				source_entry.set_enabled(True)
			else:
				# Manually add the entry
				self.repositories[repository] = libchannels.common.sourceslist.add(
					"deb",
					self[repository]["default_mirror"],
					self[repository]["codename"],
					self[repository]["components"].split(" "), # FIXME
					comment=repository,
					file="/etc/apt/sources.list.d/%s.list" % self.channel_name
				)
		
		libchannels.common.sourceslist.save()
	
	def get_dependencies(self):
		"""
		Returns a list of the channel's dependencies.
		"""
		
		return self["channel"]["depends"].split(" ") if "depends" in self["channel"] else []
	
	def get_conflicts(self):
		"""
		Returns a list of the channel's conflicts.
		"""
		
		return self["channel"]["conflicts"].split(" ") if "conflicts" in self["channel"] else []
	
	def get_providers(self):
		"""
		Returns a list of the channel's provides.
		"""
		
		return self["channel"]["provides"].split(" ") if "provides" in self["channel"] else []
	
	def __str__(self):
		"""
		Returns a stringified version of the object.
		"""
		
		return self["channel"]["name"]
	
	def check(self, uri, origin, label, codename, source_entry):
		"""
		Sets the given SourceEntry into self.repositories if it matches
		the other information given.
		"""
				
		for repository in self.repositories:
			
			#print(self["channel"]["name"], origin, codename, source_entry)
			
			if ((origin and origin != self[repository]["origin"]) or
				(not origin and not (
					self[repository]["default_mirror"] + "/"
					if not self[repository]["default_mirror"].endswith("/")
					else self[repository]["default_mirror"]
				) == uri)
			):
				continue
				
			if codename != self[repository]["codename"]:
				continue
			
			#if label != self[repository]["label"]:
			#	continue
			
			# Good!
			self.repositories[repository] = source_entry
	
	def is_proposed(self, name):
		"""
		Returns True if the repository name is proposed, False if not.
		"""
		
		return (
			"proposed" in self[name] and
			self[name].getboolean("proposed")
		)
	
	def is_sourceentry_enabled(self, name, repository, skip_proposed=False):
		"""
		Returns True if the sourceentry is enabled, False if not.
		"""
				
		return (
			(
				type(repository) == SourceEntry and
				not repository.disabled
			) or
			(
				skip_proposed and
				self.is_proposed(name)
			)
		)
	
	@property
	def enabled(self):
		"""
		Returns True if the channel is enabled, False if not.
		"""
		
		#return (not (None in self.repositories.values()))
		return (not (False in [self.is_sourceentry_enabled(x, y, skip_proposed=True) for x, y in self.repositories.items()]))
