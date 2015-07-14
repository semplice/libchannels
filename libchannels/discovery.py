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

import os

import libchannels.channel
import libchannels.provider
import libchannels.common
import libchannels.config

class ChannelDiscovery:
	
	"""
	The ChannelDiscovery() class permits to discover every enabled channel
	and is used to get a precise status of a given channel.
	"""
	
	cache = {}
	channels = {}
	
	def __init__(self):
		"""
		Initializes the class.
		"""
		
		pass
	
	def discover(self):
		"""
		Discovers the currently enabled channels.
		"""
				
		# Pre-load channels
		for channel in os.listdir(libchannels.config.CHANNEL_SEARCH_PATH):
			
			if not channel.endswith(".channel") and not channel.endswith(".provider"):
				continue
			
			# Obtain name
			channel = channel.replace(".channel","")
			
			if channel.endswith(".provider"):
				self.cache[channel] = libchannels.provider.Provider(channel)
			else:
				self.cache[channel] = libchannels.channel.Channel(channel)
				
		# Loop through enabled repositories to get a list of enabled channels
		for repository in libchannels.common.sourceslist:
			if repository.uri == "" or repository.type == "deb-src":
				continue
			
			# Generate InRelease filename from repository URI
			release_base = repository.uri.replace("/","_").split("_")
			# Remove empty (former) trailslashes
			while release_base.count("") > 0:
				release_base.remove("")
			# Add other informations
			release_base += ["dists", repository.dist.replace("/","_")]
			# Remove protocol
			release_base.pop(0)
			
			# InRelease
			InRelease = os.path.join("/var/lib/apt/lists", "_".join(release_base + ["InRelease"]))
			# Release (fallback)
			Release = os.path.join("/var/lib/apt/lists", "_".join(release_base[1:] + ["Release"]))
			
			# Check existence
			if os.path.exists(InRelease):
				# InRelease found
				release_file = open(InRelease)
			elif os.path.exists(Release):
				# Release found
				release_file = open(Release)
			else:
				# Nothing found, we should try our luck with the default mirror
				release_file = None
						
			# Obtain informations
			origin = label = codename = None
			if release_file:
				for line in release_file:
					line = line.strip().split(" ")
					if line[0] == "Origin:":
						origin = " ".join(line[1:])
					elif line[0] == "Label:":
						label = " ".join(line[1:])
					elif line[0] == "Codename:":
						codename = " ".join(line[1:])
			
			# Search for the right channel
			for channel, obj in self.cache.items():
				
				if channel.endswith(".provider"):
					# Providers do not need checking
					continue
				
				obj.check(
					repository.uri + "/" if not repository.uri.endswith("/") else repository.uri,
					origin,
					label,
					[repository.dist, codename],
					repository
				)
			
			# Close
			if release_file: release_file.close()
		
		for channel, obj in self.cache.items():
			if not channel.endswith(".provider") and obj.enabled:
				self.channels[channel] = obj

