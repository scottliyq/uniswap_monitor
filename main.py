"""
token bean
"""
import json
from enum import Enum

import web3
from eth_abi import encode
from web3 import Web3, HTTPProvider
POOL_INIT_CODE_HASH: str = '0xe34f199b19b2b4f47f68442619d555527d244f78a3297ea89325f843f87b8b54'
FACTORY_ADDRESS = '0x1F98431c8aD98523631AE4a59f267346ea31F984'.lower()
ADDRESS_ZERO: str = '0x0000000000000000000000000000000000000000'
RPC_URL = 'https://opt-mainnet.g.alchemy.com/v2/nCQbm_KIbQkMvNGUP6lNYuuOvMCjv_3X'


class Token:
    _decimal: int = 18
    _address: str
    _symbol: str

    def __init__(self, address: str, decimal: int = 18, symbol: str = None):
        self._decimal = decimal
        self._address = address
        self._symbol = symbol

    @property
    def decimal(self):
        return self._decimal

    @property
    def address(self):
        return self._address

    @property
    def symbol(self):
        return self._symbol


# 手续费枚举
class FeeAmount(Enum):
    LOWEST = 100
    LOW = 500
    MEDIUM = 3000
    HIGH = 10000


# 暂使用 get_pool_address 去链上查询 bug
def compute_uniswap_v3_pool_address(token0: Token, token1: Token, fee: FeeAmount,
                                    factory_address: str = FACTORY_ADDRESS):
    # if factory_address is None:
    #     factory_address = FACTORY_ADDRESS
    abi_encoded_1 = encode(['address', 'address', 'uint24'], [token0.address, token1.address, fee.value])
    salt = Web3.solidity_keccak(['bytes'], ['0x' + abi_encoded_1.hex()])
    # abi_encoded_2 = Web3.solidity_keccak(['address', 'bytes32'], (factory_address, salt))
    # res_pair = Web3.keccak(['bytes', 'bytes'], ['0xff' + abi_encoded_2.hex(), POOL_INIT_CODE_HASH])[12:]
    # return salt
    return web3.utils.address.get_create2_address(factory_address, salt, POOL_INIT_CODE_HASH)


def get_pool_address(token0: Token, token1: Token, fee: FeeAmount):
    web3_provider = Web3(HTTPProvider(RPC_URL))
    f = open('facory.abi.json')
    factory_json = json.load(f)
    factory_contract = web3_provider.eth.contract(address=Web3.toChecksumAddress(FACTORY_ADDRESS), abi=factory_json)
    return factory_contract.functions.getPool(Web3.toChecksumAddress(token0.address.lower()), Web3.toChecksumAddress(token1.address.lower()), fee.value).call()

def get_pool_slot0(pool_address:str):
    web3_provider = Web3(HTTPProvider(RPC_URL))
    f = open('pool.abi.json')
    pool_address_json = json.load(f)
    pool_contract = web3_provider.eth.contract(address=Web3.toChecksumAddress(pool_address.lower()), abi=pool_address_json)
    slot0 = pool_contract.functions.slot0().call();
    return slot0
# token address排序
def sorts_token_address_before(token0_address: str, token1_address: str):
    return (token0_address, token1_address) if int(token0_address, 16) < int(token1_address,
                                                                             16) else (token1_address, token0_address)


if __name__ == '__main__':
    (token0_address, token1_address) = sorts_token_address_before('0xc84da6c8ec7a57cd10b939e79eaf9d2d17834e04',
                                                                  '0x9d34f1d15c22e4c0924804e2a38cbe93dfb84bc2');
    token0 = Token(token0_address)
    token1 = Token(token1_address)
    pool_address = get_pool_address(token0, token1, FeeAmount.MEDIUM)
    slot0 = get_pool_slot0(pool_address)
    sqrtPriceX96 = slot0[0]
    price = sqrtPriceX96 ** 2 / 2 ** 192;
    print(price)


