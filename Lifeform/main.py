import json
import hmac
import time
import base64
import hashlib
import urllib3
import requests

from web3 import Web3
from loguru import logger
from hashlib import sha256
from eth_account.messages import encode_defunct
from requests_toolbelt import MultipartEncoder
from pyuseragents import random as random_useragent

urllib3.disable_warnings()
# ChainId: 56 (BSC)
w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org"))
# lifeform_contract_address = "0x37ac6a9b55DCEc42145a2147c2fccCB4c737c7E4"
# lifeform_contract_abi = json.load(open("Cartoon.json"))
# lifefrom_contract = w3.eth.contract(address=lifeform_contract_address, abi=lifeform_contract_abi)
apikey = "xct7PWyzBVCqRhHWPRTDEU"
apisecret = "4DkJhvGcyuyaNEHkZ4JZza"
'''
function call_FridaActivity3() {
    Java.perform(function () {
        // var FridaActivity3 = Java.use("com.faceunity.app_ptag.entity.SaveAvatarParam");
        Java.choose("com.faceunity.app_ptag.entity.SaveAvatarParam", {
            onMatch: function (instance) {
                console.log(instance.getApiKey());
                console.log(instance.getApiSecret());
            },
            onComplete: function () {
            }
        });
    })
}
frida -U -l fr.js -f com.houlangtech.lifeform
'''


def get_signature(mesg, privatekey):
    message = encode_defunct(text=mesg)
    signatures = w3.eth.account.sign_message(message, privatekey)
    signatures_sign = w3.toHex(signatures.signature)
    return signatures_sign


def wallet_login(client, address, signature):
    url = 'https://api-v2.lifeform.cc/api/v1/wallet_login'
    json_data = {
        "address": address,
        "chain_id": 56,
        "sign": signature
    }
    response = client.post(url, json=json_data).json()
    if response['code'] != 0:
        raise Exception(json.dumps(response))
    return response['data']['access_token'], response['data']['salt']


def get_token(client):
    time_ = int(time.time() * 1000)
    data = f"{apikey}{time_}{apisecret}".encode('utf-8')  # 加密数据fr
    signature = hmac.new(apisecret.encode('utf-8'), data,
                         digestmod=sha256).hexdigest()
    url = f'https://pandora.lifeform.cc/web_avatar/api/token/info?timestamp={int(time.time() * 1000)}&signature={signature}&apikey={apikey}'
    response = client.get(url).json()
    if response['code'] != 0:
        raise Exception(json.dumps(response))
    return response['data']['value']


def create_avatar_id(client, token):
    url = f'https://pandora.lifeform.cc/web_avatar/api/items/avatar/create?token={token}'
    files = {
        'data': json.dumps({"name": "", "style": "default", "gender": "male", "bundle_list": ["GAssets/AsiaMale/head/BaseModelAmale_head.bundle", "GAssets/AsiaMale/body/BaseModelAmale_body.bundle", "GAssets/AsiaMale/brow/brow000.bundle", "GAssets/AsiaMale/hair/hair001.bundle", "GAssets/AsiaMale/cloth/lower_inner/shorts/shorts001.bundle", "GAssets/AsiaMale/cloth/upper_inner/shirt/shirt003.bundle", "GAssets/AsiaMale/face_components/eye/eye201a.bundle", "GAssets/AsiaMale/face_components/face/face201b.bundle", "GAssets/AsiaMale/face_components/mouth/mouth201a.bundle", "GAssets/AsiaMale/face_components/nose/nose201b.bundle"], "facepup_config": {"bone_controllers": [], "bones": [], "blendshapes": []}, "texture_list": [], "color_list": [{"name": "hair_color", "color": [115, 70, 53, 255]}, {"name": "makeup_lip_color", "color": [219, 149, 135, 255]}, {"name": "eyebrow_color", "color": [35, 30, 32, 255]}, {"name": "beard_color", "color": [118, 62, 38, 255]}, {"name": "skin_color", "color": [240, 185, 147, 255]}, {"name": "iris_color", "color": [121, 47, 16, 255]}]}),
        'icon': ('avatar.png', open('avatar.png', 'rb'), 'image/png'),
    }
    client.headers.update(
        {"content-type": "multipart/form-data; boundary=boundaryInInFUPTAIniOS"})
    files = MultipartEncoder(fields=files, boundary='boundaryInInFUPTAIniOS')
    response = client.post(url, data=files).json()
    if response['code'] != 0:
        raise Exception(json.dumps(response))
    return response['data']['avatar_id']


def create_avatar(client, token, salt):
    url = 'https://api-v2.lifeform.cc/api/v1/avatar_v2'
    main_str = r'{"misc":{"avatarJsonContent":"{\"name\":\"raven\",\"style\":\"default\",\"gender\":\"female\",\"bundle_list\":[\"GAssets\/AsiaFemale\/head\/basemodelafemale_head.bundle\",\"GAssets\/AsiaFemale\/body\/basemodelafemale_body.bundle\",\"GAssets\/AsiaFemale\/brow\/brow000.bundle\",\"GAssets\/AsiaFemale\/face_components\/face\/face201b.bundle\",\"GAssets\/AsiaFemale\/face_components\/nose\/nose201b.bundle\",\"GAssets\/AsiaFemale\/cloth\/suit\/suit061.bundle\",\"GAssets\/AsiaFemale\/cloth\/shoes\/shoes015.bundle\",\"GAssets\/AsiaFemale\/face_beauty\/blush\/blush_none.bundle\",\"GAssets\/AsiaFemale\/face_beauty\/eyeshadow\/eyeshadow_none.bundle\",\"GAssets\/AsiaFemale\/face_beauty\/eyelash\/eyelash005.bundle\",\"GAssets\/AsiaFemale\/hair\/hair015.bundle\",\"GAssets\/AsiaFemale\/face_beauty\/lip\/lip_none.bundle\",\"GAssets\/AsiaFemale\/face_beauty\/pupil\/pupil004.bundle\",\"GAssets\/AsiaFemale\/face_components\/eye\/eye203c.bundle\",\"GAssets\/AsiaFemale\/face_components\/mouth\/mouth201c.bundle\"],\"facepup_config\":{\"bone_controllers\":[{\"name\":\"L_innBrow_jnt_syNeg\",\"value\":0.6233521103858948},{\"name\":\"mouth_root_jnt_tyNeg\",\"value\":0.10734468698501587},{\"name\":\"L_brow_jnt_syNeg\",\"value\":0.29566851258277893},{\"name\":\"R_innBrow_jnt_txPos\",\"value\":0.05461393669247627},{\"name\":\"mouth_root_jnt_szNeg\",\"value\":1.0},{\"name\":\"mouth_root_jnt_syPos\",\"value\":0.5518888453338623},{\"name\":\"R_brow_jnt_syNeg\",\"value\":0.29566851258277893},{\"name\":\"waist_length_long\",\"value\":0.4000000059604645},{\"name\":\"waist_thickness_thick\",\"value\":0.4000000059604645},{\"name\":\"R_innBrow_jnt_tyNeg\",\"value\":0.24293792247772217},{\"name\":\"forehead_jnt_tzNeg\",\"value\":0.6610169410705566},{\"name\":\"forehead_jnt_sxPos\",\"value\":0.22033892571926117},{\"name\":\"L_cheek_jnt_tyPos\",\"value\":1.0},{\"name\":\"L_cheek_jnt_txNeg\",\"value\":0.5518888453338623},{\"name\":\"legs_thickness_thick\",\"value\":0.20000000298023224},{\"name\":\"L_brow_jnt_tyNeg\",\"value\":0.08851224184036255},{\"name\":\"arms_thickness_thick\",\"value\":0.20000000298023224},{\"name\":\"L_innBrow_jnt_txNeg\",\"value\":0.05461393669247627},{\"name\":\"R_innBrow_jnt_syNeg\",\"value\":0.6233521103858948},{\"name\":\"mouth_jnt_syPos\",\"value\":0.25423723459243774},{\"name\":\"R_cheek_jnt_tyPos\",\"value\":1.0},{\"name\":\"arms_length_long\",\"value\":0.699999988079071},{\"name\":\"R_brow_jnt_tyNeg\",\"value\":0.08851224184036255},{\"name\":\"L_innBrow_jnt_tyNeg\",\"value\":0.24293792247772217},{\"name\":\"R_brow_jnt_txNeg\",\"value\":0.028248703107237816},{\"name\":\"R_cheek_jnt_txPos\",\"value\":0.5518888453338623},{\"name\":\"R_cheek_jnt_tzNeg\",\"value\":0.06591348350048065},{\"name\":\"L_brow_jnt_txPos\",\"value\":0.028248703107237816},{\"name\":\"mouth_root_jnt_sxNeg\",\"value\":0.06967979669570923},{\"name\":\"head_size_small\",\"value\":0.4000000059604645},{\"name\":\"L_cheek_jnt_tzNeg\",\"value\":0.06591348350048065},{\"name\":\"forehead_jnt_tyPos\",\"value\":0.03954802080988884},{\"name\":\"legs_length_long\",\"value\":1.0}],\"bones\":[],\"blendshapes\":[]},\"texture_list\":[],\"color_list\":[{\"name\":\"iris_color\",\"color\":[82,62,44,255]},{\"name\":\"makeup_lip_color\",\"color\":[218,90,85,255]},{\"name\":\"eyebrow_color\",\"color\":[192,165,135,255]},{\"name\":\"skin_color\",\"color\":[245,202,168,255]},{\"name\":\"hair_color\",\"color\":[192,165,135,255]}]}","avatarId":"raven","ip":"cartoon","avatarJsonPath":"\/var\/mobile\/Containers\/Data\/Application\/7A686DD2-0C7D-4436-A0BE-19F24B0CB8A9\/Documents\/avatarsData\/raven\/avatar.json","platform":"ios"}}'.replace(
        'raven', token)
    main_str = base64.b64encode(main_str.encode('utf-8'))
    md5_str = main_str + salt.encode('utf-8')
    mainHash = hashlib.md5(md5_str).hexdigest()
    file_ = open('4789691621222800897.png', 'rb').read() + salt.encode('utf-8')
    files = {
        'main': main_str,
        'ip': 'cartoon',
        'imageHash': hashlib.md5(file_).hexdigest(),
        'gender': 'male',
        'mainHash': mainHash,
        'ext': 'MQ==',
        'image': ('4789691621222800897.png', open('4789691621222800897.png', 'rb'), 'image/png'),
    }
    files = MultipartEncoder(
        fields=files, boundary='alamofire.boundary.0f158e0f74a32ec2')
    client.headers.update(
        {"content-type": "multipart/form-data; boundary=alamofire.boundary.0f158e0f74a32ec2"})
    response = client.post(url, data=files).json()
    print(response)
    if response['code'] != 0:
        raise Exception(json.dumps(response))
    return True


def get_mintAvatar(send, address):
    # url = 'https://pandora.lifeform.cc/lifeform_bsc_prod/api/avatarCartoon/mintAvatar'
    url = 'https://pandora.lifeform.cc/lifeform_bsc_prod/api/avatarCartoon/easyMintAvatar'
    data = {
        "gender": "female",
        "address": address,
        "affAddress": affAddress
    }
    response = send.post(url, json=data).json()
    # print(response)
    if response['status'] != 10000:
        raise Exception(json.dumps(response))
    return response['result']


def mintAvatar721(address, privatekey, code_raw):
    mintRule = code_raw['condition']['mintRule'][2:]
    udIndex = hex(code_raw['condition']['udIndex'])[2:]
    stakeErc20 = code_raw['condition']['stakeErc20'][2:]
    costErc20 = code_raw['condition']['costErc20'][2:]
    signCode = code_raw['condition']['signCode'][2:]
    wlSignature = code_raw['condition']['wlSignature'][2:]
    dataSignature = code_raw['dataSignature']['signature'][2:]

    data_bytes = {
        "from": address,
        "to": "0x37ac6a9b55DCEc42145a2147c2fccCB4c737c7E4",
        "data": f'0x5e194c3700000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000200000000000000000000000000{mintRule}00000000000000000000000000000000000000000000000000000000000{udIndex}000000000000000000000000{stakeErc20}0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000{costErc20}000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001{signCode}00000000000000000000000000000000000000000000000000000000000001400000000000000000000000000000000000000000000000000000000000000041{wlSignature}000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000041{dataSignature}00000000000000000000000000000000000000000000000000000000000000',
        "gas": 300000,
        "gasPrice": w3.toWei('5', 'gwei'),
        "nonce": w3.eth.getTransactionCount(address, "pending"),
        "chainId": 56,
    }
    signed_txn = w3.eth.account.sign_transaction(data_bytes, privatekey)
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return w3.toHex(tx_hash)


def main(account):
    send = requests.session()
    send.headers.update(
        {
            # 'authority': 'pandora.lifeform.cc',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,es;q=0.5',
            'content-type': 'application/json',
            # 'origin': 'https://cartoon.lifeform.cc',
            # 'referer': 'https://cartoon.lifeform.cc/',
            # 'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
            # 'sec-ch-ua-mobile': '?0',
            # 'sec-ch-ua-platform': '"macOS"',
            # 'sec-fetch-dest': 'empty',
            # 'sec-fetch-mode': 'cors',
            # 'sec-fetch-site': 'same-site',
            'user-agent': random_useragent()
        }
    )
    signature_msg = f'address={account[0]},chain_id=56'
    signature = get_signature(signature_msg, account[1])
    access_token = wallet_login(send, account[0], signature)
    send.headers.update({"authorization": f"Bearer {access_token[0]}"})

    mint_code = get_mintAvatar(send, account[0])
    mint_hash = mintAvatar721(account[0], account[1], mint_code)
    print(f'{account[0]}----{mint_hash}')


if __name__ == '__main__':
    affAddress = '0x0000'
    account_list = open("account.txt", "r").read().splitlines()
    for account in account_list:
        main(account.split('----'))
