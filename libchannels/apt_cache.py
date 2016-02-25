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

import apt
import apt_pkg

import logging

logger = logging.getLogger(__name__)

class DynamicCache:
	"""
	A proxy object that will load the cache only when required.
	"""
	
	def __init__(self):
		"""
		Initializes the object.
		"""
		
		self._cache = None
	
	def open_cache(self, progress=None):
		"""
		Opens/creates the cache.
		"""
		
		if not self._cache:
			self._cache = apt.Cache(progress=progress)
		else:
			self._cache.open(progress=progress)
	
	def clear(self):
		"""
		Clears the changes made.
		"""
		
		if self._cache:
			self._cache = None
	
	def __getattr__(self, name):
		"""
		Returns the cache attribute, loading the cache first if required.
		"""
		
		if not self._cache:
			self.open_cache()

		logger.debug("Cache attribute requested, %s" % name)
		return getattr(self._cache, name)

	def __getitem__(self, name):
		"""
		Offloads the call to the cache object.
		"""

		if not self._cache:
			self.open_cache()

		return self._cache.__getitem__(name)

	def __contains__(self, name):
		"""
		Offloads the call to the cache object.
		"""

		if not self._cache:
			self.open_cache()

		return self._cache.__contains__(name)

	def __iter__(self):
		"""
		Offloads the iteration to the cache object.
		"""

		if not self._cache:
			self.open_cache()

		return self._cache.__iter__()
	
	def __eq__(self, other):
		"""
		Offloads the comparison to the cache object.
		"""
		
		return self._cache.__eq__(other)
	
	def __ne__(self, other):
		"""
		Offloads the comparison to the cache object.
		"""
		
		return self._cache.__ne__(other)
