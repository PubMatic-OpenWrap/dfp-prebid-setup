#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dfp.client import get_client

def get_dfp_network():
    dfp_client = get_client()
    network_service = dfp_client.GetService('NetworkService', version='v202402')
    current_network = network_service.getCurrentNetwork()
    return current_network

def main():
  network = get_dfp_network()
  print(network)

if __name__ == '__main__':
  main()
