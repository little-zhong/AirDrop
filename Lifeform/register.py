import httpx
import asyncio

from web3 import Web3
from loguru import logger
from eth_account.messages import encode_defunct

w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org"))
logger.add("log/file_{time:YYYY-MM-DD}.log",
           format="[{time:%H:%M:%S.%f!UTC}] {level} {message}", enqueue=True)


def get_signature(mesg, privatekey):
    message = encode_defunct(text=mesg)
    signatures = w3.eth.account.sign_message(message, privatekey)
    signatures_sign = w3.toHex(signatures.signature)
    return signatures_sign


async def login_wallet(client, account):
    url = 'https://superbrain-api.lifeform.cc/superbrain/api/v1/wallet_login'
    json_data = {
        "address": account[0],
        "chain_id": 56,
        "sign": get_signature(f'address={account[0]},chain_id=56', account[1])
    }
    response = await client.post(url, json=json_data)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}")
    response_json = response.json()
    return response_json['data']['header'], response_json['data']['salt']


async def get_token_id(client, account):
    url = f'https://api-v2.lifeform.cc/api/v1/nft/nfts_online_paged?page=0&size=200&address={account[0]}&chain_id=56&contract=0x6f282fc910CD6eCdCcC9E0f06e6EA3e5602A24d5'
    response = await client.get(url)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}")
    response_json = response.json()
    if len(response_json['data']['items']) > 0:
        return response_json['data']['items'][0]['token_id']
    raise Exception("Error: Token ID not found")


async def registerSign(client, account):
    url = 'https://pandora.lifeform.cc/lifeform_bsc_prod/api/answer/registerSign'
    json_data = {
        "registerType": 2,
        "tokenId": await get_token_id(client, account),
        "activityId": 12,
        "address": account[0],
    }
    response = await client.post(url, json=json_data)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}")
    response_json = response.json()
    return response_json['result']['condition']['signCode'], response_json['result']['condition']['wlSignature'], response_json['result']['dataSignature']['signature'], response_json['result']['condition']['tokenId']


def setApprovalForAll(account):
    payale = {
        'from': account[0],
        'to': '0x6f282fc910CD6eCdCcC9E0f06e6EA3e5602A24d5',
        'data': '0xa22cb46500000000000000000000000009bb16c94a3ba650b7b825bff641626bbe179e6d0000000000000000000000000000000000000000000000000000000000000001',
        'gas': 50000,
        'gasPrice': w3.eth.gasPrice,
        'nonce': w3.eth.getTransactionCount(account[0], 'pending'),
        'chainId': 56
    }
    signed_txn = w3.eth.account.sign_transaction(payale, account[1])
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if tx_receipt.status == 0:
        raise Exception("Error: setApprovalForAll")
    return tx_receipt.transactionHash.hex()


def register(account, sign_info):
    tokenHash = bytes(sign_info[3], 'UTF-8').hex()
    payale = {
        'from': account[0],
        'to': '0x09Bb16C94a3bA650B7B825BFf641626BBE179E6D',
        'data': f'0xdf09dbea0000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000001e00000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000{tokenHash}{sign_info[0][2:]}00000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000041{sign_info[1][2:]}000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000041{sign_info[2][2:]}000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
        'gas': 200000,
        'gasPrice': w3.eth.gasPrice,
        'nonce': w3.eth.getTransactionCount(account[0], 'pending'),
        'chainId': 56
    }
    signed_txn = w3.eth.account.sign_transaction(payale, account[1])
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if tx_receipt.status == 0:
        raise Exception("Error: register")
    return tx_receipt.transactionHash.hex()


async def worker(account, num):
    async with num:
        account = account.split("----")
        try:
            async with httpx.AsyncClient() as client:
                login_info = await login_wallet(client, account)
                client.headers.update({'Authorization': login_info[0]})
                sign_info = await registerSign(client, account)
                setApprovalForAll(account)
                register_hash = register(account, sign_info)
                logger.info('ACCOUNT: %s, REGISTER_HASH: %s',
                            account[0], register_hash)
        except Exception as e:
            logger.error('ACCOUNT: %s, ERROR: %s', account[0], e.args)
        finally:
            await asyncio.sleep(1)


async def main():
    tasks = []
    num = asyncio.Semaphore(5)
    for account in ACCOUNT_LIST:
        tasks.append(asyncio.create_task(worker(account, num)))
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    '''
    ADDRESS1----PRIVATE_KEY1
    ADDRESS2----PRIVATE_KEY2
    '''
    ACCOUNT_LIST = open("account.txt", "r").read().splitlines()
    asyncio.run(main())
