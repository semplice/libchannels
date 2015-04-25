#!/usr/bin/python3
# -*- coding: utf-8 -*-

import libchannels.discovery
import libchannels.resolver
import libchannels.actions

import sys

if len(sys.argv) < 3:
	print("You should specify the action and the channel to execute the action on!")
	sys.exit(1)

action = libchannels.actions.ActionType.DISABLE if sys.argv[1] == "disable" else libchannels.actions.ActionType.ENABLE
channel = sys.argv[2]

# Discovery
discovery = libchannels.discovery.ChannelDiscovery()
discovery.discover()

# Resolver
resolver = libchannels.resolver.DependencyResolver(discovery.cache)

# Actions
actions = libchannels.actions.Actions(discovery, resolver)

#print(action)
if action == libchannels.actions.ActionType.DISABLE:
	actions.disable_channel(channel)
else:
	actions.enable_channel(channel)
