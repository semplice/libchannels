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

from apt_pkg import size_to_str

logger = logging.getLogger(__name__)

# APT Configuration

# FIXME: should make this interactive
apt_pkg.config.set("DPkg::Options::", "--force-confdef")
apt_pkg.config.set("DPkg::Options::", "--force-confold")

class APT:
	
	"""
	Same-release distribution updates management.
	"""
	
	MAX_TRIES = 5
	
	def __init__(self, cache):
		"""
		Initializes the class.
		"""
		
		# Used to determine if mark_for_upgrade has been executed
		self.changed = False
		
		# True if the last call on mark_for_upgrade was in dist-upgrade mode.
		# This is used by restore_working_state()
		self.last_is_dist_upgrade = False
		
		self.lock = apt_pkg.SystemLock()
		self.lock_failure_callback = None
		
		self.generic_failure_callback = None

		self.cache = cache
		
		self.cache_progress = None
		self.cache_acquire_progress = None
		self.packages_acquire_progress = None
		self.packages_install_progress = None
		self.packages_install_failure_callback = None
		
		self.id_with_packages = {}
		
		self.now_kept = []
	
	def notify_error(self, error, description="", callback=None):
		"""
		Notifies an error, by logging it and firing a specified callback.
		
		If callback is None, it will assume self.generic_failure_callback.
		"""
		
		logger.error(error)
		if description:
			logger.error("Description was: %s" % description)
		
		if callback or self.generic_failure_callback:
			(callback if callback else self.generic_failure_callback)(error, str(description))
	
	def open_cache(self, progress=None):
		"""
		Opens/Creates the cache.
		"""
		
		return self.cache.open_cache(progress if progress else self.cache_progress)
	
	def clear(self):
		"""
		Clears the changes made.
		"""
		
		if self.cache:
			self.cache.clear()
		
		self.changed = False
		
		self.id_with_packages = {}
		self.now_kept = []
	
	def get_update_infos(self):
		"""
		Returns useful info (required_download, required_space).
		"""
		
		if not self.cache:
			return 0, 0
		
		try:
			return self.cache.required_download, self.cache.required_space
		except SystemError as err:
			self.notify_error("An error occurred", err)
			return 0, 0

	def check_relationship(self, relationship):
		"""
		Checks a single relationship.

		Returns True if it does, False if not.

		`relationship` is a single relationship.
		"""

		for package_name, relationship_version, operator in relationship:
			if package_name in self.cache:
				package = self.cache[package_name]
				if package.is_installed:
					version = package.installed
				elif package.marked_install or package.marked_upgrade or package.marked_downgrade:
					# FIXME: this assumption may not be always correct
					version = package.candidate

				if apt_pkg.check_dep(version.version, operator, relationship_version):
					return True

		return False

	def check_relationships(self, relationships):
		"""
		Checks if the current APT state satisfies the given relationships.

		Returns True if it does, False if not.

		`relationships` is a relationship list as returned by `apt_pkg.parse_src_depends()`.
		"""

		# Example relationship list:
		# [[('abiword', '5.0', '>='), ('meh', '', '')], [('gnumeric', '', ''), ('lol', '', '')]]
		# which roughly translates to:
		# abiword (>= 5.0) | meh, gnumeric | lol

		for group in relationships:
			if not self.check_relationship(group):
				return False

		return True

	def update(self):
		"""
		Updates the package cache.
		"""
		
		if not self.cache:
			self.open_cache()
		
		self.cache.update(fetch_progress=self.cache_acquire_progress)
		self.open_cache()
	
	def mark_for_upgrade(self, dist_upgrade=False):
		"""
		Marks the package for upgrade/dist-upgrade.
		
		Returns True if everything went correctly, False if not (dependency problems).
		"""
		
		if not self.cache:
			self.open_cache()
		
		try:
			self.cache._depcache.upgrade(dist_upgrade)
			
			self.changed = True
			self.last_is_dist_upgrade = dist_upgrade
		except Exception as err:
			self.clear()
			self.notify_error("Unable to mark the packages for dist-upgrade", err)
			return False
		
		return True
	
	def fetch(self, package_manager=None):
		"""
		Fetches the updates.
		"""
		
		if not self.cache:
			return False
		
		logger.info("Beginning fetch")
		acquire_object = apt_pkg.Acquire(progress=self.packages_acquire_progress)
		
		try:
			if not package_manager:
				self.cache.fetch_archives(fetcher=acquire_object)
			else:
				# Handle internally
				self.cache._fetch_archives(acquire_object, package_manager)
			acquire_object.shutdown()
		except apt.cache.FetchCancelledException:
			# Cancelled
			logger.info("Fetch cancelled")
			return False
		except Exception as err:
			self.notify_error("Unable to fetch the packages", err)
			return False
		
		return True
	
	def install(self):
		"""
		Installs the updates.
		"""
		
		if not self.cache:
			return False
		
		package_manager = apt_pkg.PackageManager(self.cache._depcache)
		
		# Once the installation has been completed, there are three
		# possible actions to do:
		#   - If the status is pm.RESULT_COMPLETED, the installation
		#     was successful and we can go home
		#   - If the status is pm.RESULT_INCOMPLETE or pm.RESULT_FAILED,
		#     we try again, fixing the possible broken packages.
		#     libchannels will re-try the operation for maximum 5 tries.
		#   - If the status is unknown, listeners are notified and
		#     everything ends here.

		# Notify progress listeners that the installation is starting
		self.packages_install_progress.start_update()

		tries = 0
		while tries < self.MAX_TRIES:
			# Run the fetch operation again, just to be sure
			if not self.fetch(package_manager):
				return
			
			logger.debug("Starting the update run")
			
			# Then run the actual installation process
			res = self.packages_install_progress.run(package_manager)
			#res = package_manager.do_install()
						
			if res in (package_manager.RESULT_INCOMPLETE, package_manager.RESULT_FAILED):
				logger.warning("System update %s, trying again (%s/%s)" %
					(
						"incomplete"
						if res == package_manager.RESULT_INCOMPLETE
						else "failed",
						
						tries+1,
						
						self.MAX_TRIES
					)
				)
				# Dpkg journal dirty?
				if self.cache.dpkg_journal_dirty:
					logger.debug("Dirty journal, fixing...")
					subprocess.call(["dpkg", "configure", "--all"])
				
				# FIXME: add check for core packages
				
				# Broken packages?
				#if self.cache._depcache.broken_count > 0:
				if True:
					logger.debug("Broken packages, fixing...")
					self.cache.clear()
					self.open_cache()
					fixer = apt_pkg.ProblemResolver(self.cache._depcache)
					fixer.resolve(True)
					
					# FIXME: should notify this?
					self.fetch(package_manager)
					self.packages_install_progress.run(package_manager)
					
					# Restore working state for the next upgrade run
					self.restore_working_state()
			elif res == package_manager.RESULT_COMPLETED:
				# Everything completed successfully
				logger.info("Clearing cache")
				self.clear()
				
				logger.info("System update completed")
				self.packages_install_progress.finish_update()
				return
			else:
				# Unknown error.
				logger.error("Unknown error: %s" % res)
				self.packages_install_failure_callback("Unknown error: %s" % res)
				return
				
			tries += 1
		
		# If we are here, the installation process failed and we were
		# unable to continue.
		logger.error("System upgrade failed: MAX_TRIES reached")
		self.packages_install_failure_callback("System upgrade failed: MAX_TRIES reached")
	
	def get_reason(self, pkg):
		"""
		Returns the change reason of the given package.
		"""
		
		if pkg.marked_delete:
			# Remove
			reason = "remove"
		elif pkg.marked_downgrade:
			# Downgrade
			reason = "downgrade"
		elif pkg.marked_install:
			# Install
			reason = "install"
		elif pkg.marked_upgrade:
			# Upgrade
			reason = "upgrade"
		else:
			return None
		
		return reason
	
	def get_changes(self, callback, finish_callback=None):
		"""
		Returns the changes one-by-one by firing the callback.
		"""
		
		for pkg in self.cache:
			reason = self.get_reason(pkg)
			
			if reason == None and not pkg.id in self.now_kept:
				continue
			
			if pkg.candidate == None:
				# What?!
				continue
			
			# Save the id, may be used later
			if not pkg.id in self.id_with_packages:
				self.id_with_packages[pkg.id] = (pkg, reason)
			
						
			callback(
				pkg.id, # id
				pkg.name, # name
				pkg.candidate.version, # version
				reason if reason else self.id_with_packages[pkg.id][1], # reason
				not pkg.id in self.now_kept, # status
				size_to_str(pkg.candidate.size) + "B" # size (FIXME: should use size_to_str outside)
			)
		
		if finish_callback:
			finish_callback()
	
	def restore_working_state(self, package=None, reason=None):
		"""
		Tries to restore a working state.
		"""
		
		if package:
			print("Restoring working state (%s)" % package.name)
		
		# Clear cache
		self.cache.clear()
		
		# Mark again upgradeable packages
		self.mark_for_upgrade(dist_upgrade=self.last_is_dist_upgrade)
		
		# Restore now_kept
		for id in self.now_kept:
			self.cache._depcache.mark_keep(self.id_with_packages[id][0]._pkg)
	
	def change_status(self, id, reason):
		"""
		Keeps a package, and tries to fix eventual problems.
		"""
		
		with self.cache.actiongroup():
			
			self.cache.cache_pre_change()
			
			package = self.id_with_packages[id][0]
			
			# Change status
			if reason == "keep":
				self.cache._depcache.mark_keep(package._pkg)
			elif reason == "remove":
				self.cache._depcache.mark_delete(package._pkg)
			elif reason in ("install", "downgrade", "upgrade"):
				auto = package.is_auto_installed
				self.cache._depcache.mark_install(
					package._pkg,
					True,
					True,
				)
				package.mark_auto(auto)
				
			
			# Fix eventual problems
			if self.cache._depcache.broken_count > 0:
				fixer = apt_pkg.ProblemResolver(self.cache._depcache)
				fixer.clear(package._pkg)
				fixer.protect(package._pkg)
				
				try:
					if reason == "keep":
						fixer.resolve_by_keep()
					else:
						# FIXME: What if a new package is marked?
						self.cache._depcache.fix_broken()
						fixer.resolve(True)
				except SystemError:
					# Unable to resolve.
					# This sucks, but we have nothing to do except reloading
					# the previous state.
					self.restore_working_state(package, reason)
				finally:
					# Clear state again
					fixer.clear(package._pkg)
			
			self.cache.cache_post_change()
	
	def get_user_changes(self, callback):
		"""
		Returns the user changes (done by keep_package).
		"""
		
		# Firstly handle previously kept packages that may now have
		# been restored to their original action
		for id in self.now_kept[:]:
			if not self.id_with_packages[id][0].marked_keep:
				# Reason changed back, should notify
				reason = self.get_reason(self.id_with_packages[id][0])
				if reason:
					callback(
						id,
						reason
					)
				
				# Remove from now_kept
				self.now_kept.remove(id)
			
		
		# Now handle every other package that may have now been kept
		for id, val in self.id_with_packages.items():
						
			if val[0].marked_keep and not id in self.now_kept:
				# Newly kept, should notify
				callback(
					id,
					"keep"
				)
				
				# Add to now_kept
				self.now_kept.append(id)
			
			
