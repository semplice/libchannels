#!/usr/bin/python3
# -*- coding: utf-8 -*-

import libchannels.discovery

discovery = libchannels.discovery.ChannelDiscovery()

discovery.discover()


print(discovery.channels)
