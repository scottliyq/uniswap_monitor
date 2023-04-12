"""
token bean
"""
import json
from enum import Enum

import requests
import os
import time
from dotenv import load_dotenv
import web3
from eth_abi import encode
from web3 import Web3, HTTPProvider
from apscheduler.schedulers.background import BackgroundScheduler

import logging 
from logging import handlers

logger = logging.getLogger()
logger.setLevel(logging.INFO) 
logFile = './monitor.log'

# logging.basicConfig(level=logging.INFO, filename=logFile,
# 	format='[%(asctime)s %(levelname)-8s] %(message)s',
# 	datefmt='%Y-%m-%d %H:%M:%S',
# 	)

# 创建一个FileHandler,并将日志写入指定的日志文件中
fileHandler = logging.FileHandler(logFile, mode='a')
fileHandler.setLevel(logging.INFO) 
 
 # 或者创建一个StreamHandler,将日志输出到控制台
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.INFO)

# 定义Handler的日志输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler.setFormatter(formatter)
 
# 定义日志滚动条件，这里按日期-天保留日志
timedRotatingFileHandler = handlers.TimedRotatingFileHandler(filename=logFile, when='D')
timedRotatingFileHandler.setLevel(logging.INFO)
timedRotatingFileHandler.setFormatter(formatter)

# 添加Handler
# logger.addHandler(fileHandler)
logger.addHandler(streamHandler)
logger.addHandler(timedRotatingFileHandler)

def Log(*params):

    logging.info(params)

POOL_INIT_CODE_HASH: str = '0xe34f199b19b2b4f47f68442619d555527d244f78a3297ea89325f843f87b8b54'
FACTORY_ADDRESS = '0x1F98431c8aD98523631AE4a59f267346ea31F984'.lower()
#pancakev3
FACTORY_ADDRESS = '0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865'.lower()
ADDRESS_ZERO: str = '0x0000000000000000000000000000000000000000'
# RPC_URL = 'https://opt-mainnet.g.alchemy.com/v2/nCQbm_KIbQkMvNGUP6lNYuuOvMCjv_3X'
RPC_URL = 'https://koge-rpc-bsc.48.club'

BSC_USDC = '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d'
BSC_BUSD  = '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56'
BSC_USDT  = '0x55d398326f99059fF775485246999027B3197955'

BSC_PAIRS = [
    {
        "pair_name" : "usdc/busd",
        "token0": BSC_USDC,
        "token1": BSC_BUSD,
    },
    {
        "pair_name" : "usdt/busd",
        "token0": BSC_USDT,
        "token1": BSC_BUSD,
    },
    {
        "pair_name" : "usdt/usdc",
        "token0": BSC_USDT,
        "token1": BSC_USDC,
    }
]

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
    # todo bsc
    f = open('bsc.pool.abi.json')
    pool_address_json = json.load(f)
    pool_contract = web3_provider.eth.contract(address=Web3.toChecksumAddress(pool_address.lower()), abi=pool_address_json)
    slot0 = pool_contract.functions.slot0().call();
    return slot0
# token address排序
def sorts_token_address_before(token0_address: str, token1_address: str):
    return (token0_address, token1_address) if int(token0_address, 16) < int(token1_address,
                                                                             16) else (token1_address, token0_address)
def send_notice(event_name, data):

    load_dotenv()

    ifttt_webhook_key = os.getenv('IFTTT_KEY')

    ifttt_event_name = 'lp_price_alert'



    headers = {
        'Content-Type': "application/json",
        'User-Agent': "PostmanRuntime/7.15.0",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "a9477d0f-08ee-4960-b6f8-9fd85dc0d5cc,d376ec80-54e1-450a-8215-952ea91b01dd",
        'Host': "maker.ifttt.com",
        'accept-encoding': "gzip, deflate",
        'content-length': "63",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }
    # 将JSON数据转换为字符串
    payload = json.dumps(data)
    url = f"https://maker.ifttt.com/trigger/{ifttt_event_name}/json/with/key/{ifttt_webhook_key}"

    # 发送POST请求到IFTTT Webhook接口
    # response = requests.post(f'https://maker.ifttt.com/trigger/{ifttt_event_name}/json/with/key/{ifttt_webhook_key}', data=payload)
    requests.request("POST", url, data=payload.encode('utf-8'), headers=headers)

def process():
    paydata = []
    for pair in BSC_PAIRS:
        token0 = Token(pair['token0'])
        token1 = Token(pair['token1'])
        pool_address = get_pool_address(token0, token1, FeeAmount.LOWEST)
        slot0 = get_pool_slot0(pool_address)
        sqrtPriceX96 = slot0[0]
        price = round(sqrtPriceX96 ** 2 / 2 ** 192,5)
        # 构造JSON数据
        data = {'protocol': 'pancake', 'pair': pair['pair_name'], 'price': price}
        paydata.append(data)
    
    send_notice('lp_price_alert', paydata)
if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(process, 'interval', minutes=20)
    scheduler.start()
    Log('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()

    # (token0_address, token1_address) = sorts_token_address_before(BSC_USDC,
    #                                                               BSC_BUSD)
    # token0 = Token(token0_address)
    # token1 = Token(token1_address)
    # pool_address = get_pool_address(token0, token1, FeeAmount.LOWEST)
    # print(pool_address)
    # slot0 = get_pool_slot0(pool_address)
    # sqrtPriceX96 = slot0[0]
    # price = sqrtPriceX96 ** 2 / 2 ** 192
    # print(price)
    # # 构造JSON数据
    # data = {'protocol':'pancake','pair': 'busd/usdc', 'price': price}
    # send_notice('lp_price_alert', data)

