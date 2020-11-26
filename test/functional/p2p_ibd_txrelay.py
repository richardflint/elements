#!/usr/bin/env python3
# Copyright (c) 2020 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test fee filters during and after IBD."""

from decimal import Decimal

from test_framework.messages import COIN
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal

# ELEMENTS: this number is implied by DEFAULT_MIN_RELAY_TX_FEE in src/net_processing.cpp
#  which is different in Elements/Bitcoin and cannot be changed by command-line args
MAX_FEE_FILTER = Decimal(9936506) / COIN
NORMAL_FEE_FILTER = Decimal(100) / COIN


class P2PIBDTxRelayTest(BitcoinTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 2
        self.extra_args = [
            ["-minrelaytxfee={}".format(NORMAL_FEE_FILTER)],
            ["-minrelaytxfee={}".format(NORMAL_FEE_FILTER)],
        ]
    def run_test(self):
        self.log.info("Check that nodes set minfilter to MAX_MONEY while still in IBD")
        for node in self.nodes:
            assert node.getblockchaininfo()['initialblockdownload']
            for conn_info in node.getpeerinfo():
                assert_equal(conn_info['minfeefilter'], MAX_FEE_FILTER)

        # Come out of IBD by generating a block
        self.nodes[0].generate(1)
        self.sync_all()

        self.log.info("Check that nodes reset minfilter after coming out of IBD")
        for node in self.nodes:
            assert not node.getblockchaininfo()['initialblockdownload']
            for conn_info in node.getpeerinfo():
                assert_equal(conn_info['minfeefilter'], NORMAL_FEE_FILTER)


if __name__ == '__main__':
    P2PIBDTxRelayTest().main()