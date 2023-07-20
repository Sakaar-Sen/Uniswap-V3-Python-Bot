from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware
import ccxt
import time
import abiList
import math


private_key = ""
account_address = Account.from_key(private_key).address


localProvider = "http://localhost:8545"
ankr = "https://rpc.ankr.com/arbitrum" 

web3 = Web3(Web3.HTTPProvider(ankr))  
web3.middleware_onion.inject(geth_poa_middleware, layer=0)


uniswap_router_address = '0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45'
weth_address = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'  
usdc_address = '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8'  
arb_address = '0x912CE59144191C1204E64559FE8253a0e49E6548'

print("Account address:", account_address)


uniswap_router = web3.eth.contract(address=uniswap_router_address, abi=abiList.uniswapabi_v3)
weth_contract = web3.eth.contract(address=weth_address, abi=abiList.arb_wethabi)
usdc_contract =  web3.eth.contract(address=usdc_address, abi=abiList.usdcabi)
arb_contract = web3.eth.contract(address=arb_address, abi=abiList.arb_arbabi)

gas_price = web3.to_wei(1, 'gwei') 
gas_limit = 250000 

exchange = ccxt.binance()

def getOffchainPrice(asset):
    if asset.lower() == 'weth':
        asset = 'eth'
    return exchange.fetch_ticker(f'{asset.upper()}/USDT')['last']

def send_transaction(txn):
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return tx_hash

def approveAsset(asset, amountInEther):
    if asset.lower() == 'weth' or asset.lower() == 'arb':
        if asset.lower() == 'weth':
            token_contract = weth_contract
        if asset.lower() == 'arb':
            token_contract = arb_contract
    
        approve_txn = token_contract.functions.approve(uniswap_router_address, web3.to_wei(amountInEther, 'ether')).build_transaction({
            'from': account_address,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': web3.eth.get_transaction_count(account_address),
            'value': 0
        })
        
    elif asset.lower() == 'usdc':
        amountInEther = math.floor(amountInEther)
        approve_txn = usdc_contract.functions.approve(uniswap_router_address, amountInEther * 10 ** 6).build_transaction({
        'from': account_address,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': web3.eth.get_transaction_count(account_address),
        'value': 0
    })

    else:
        print("Invalid asset")
        return

    approve_tx_hash = send_transaction(approve_txn)
    print(f"Approving {amountInEther} {asset.upper()}, hash: ", approve_tx_hash.hex())
   
def assetToUsdc(asset, amountInEther):
        asset = asset.lower()
        if getBalance('eth') < 0.01:
                print("Not enough ETH to pay for gas")
                
                return
        
        if asset.lower()=='weth':
            if (getBalance('weth') < amountInEther):
                WrapEth(amountInEther - getBalance('weth'))      
            
            tokenIn = weth_address 
            fee = 500
            slippage = 0.99
        
        if asset.lower() == 'arb':
            amountInEther = int(amountInEther)
            tokenIn = arb_address
            slippage = 0.99
            fee = 3000
   
        if asset.lower() != 'arb' and asset.lower() != 'weth':
            print("Invalid asset in assetToUsdc")
            return
       
             
        AssetPrice = getOffchainPrice(asset)
        amt_min = int(AssetPrice * float(amountInEther) * slippage)
       
        if(getAllowance(asset) < amountInEther):
            approveAsset(asset, web3.from_wei(2**256-1, 'ether'))


        print(f"Price of {asset.upper()}:", AssetPrice)
        print("Min amount of USDC:", amt_min)



        swap_txn = uniswap_router.functions.exactInputSingle({
            'tokenIn': tokenIn,
            'tokenOut': usdc_address,
            'fee': fee,
            'recipient': account_address,
            'deadline': web3.eth.get_block('latest')['timestamp'] + 60 * 10,
            'amountIn': web3.to_wei(amountInEther, 'ether'),
            'amountOutMinimum': amt_min * 10 ** 6,
            'sqrtPriceLimitX96': 0
        }).build_transaction({
            'from': account_address,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': web3.eth.get_transaction_count(account_address),
            'value': 0
        })

        swap_tx_hash = send_transaction(swap_txn)
        print(f"Swapping {amountInEther} {asset.upper()} for USDC, hash: ", swap_tx_hash.hex())
       
def usdcToAsset(asset, amountInEther):
    asset = asset.lower()

    if asset.lower()=='weth':
        tokenOut = weth_address
        fee = 500
    
    if asset.lower() == 'arb':
        tokenOut = arb_address
        fee = 3000

    if asset.lower() != 'arb' and asset.lower() != 'weth':
        print("Invalid asset in usdcToAsset")
       
        return

    amountInEther = int(amountInEther)

    if(getAllowance('usdc') < amountInEther):
        approveAsset('usdc', web3.from_wei(2**256-1, 'ether'))

    AssetPrice = getOffchainPrice(asset)
    amt_min = round(float(amountInEther/AssetPrice * 0.99),2)

    print(f"Price of {asset.upper()}:", AssetPrice)
    print("Min amount of Asset:", amt_min)

  
    swap_txn = uniswap_router.functions.exactInputSingle({
        'tokenIn': usdc_address,
        'tokenOut': tokenOut,
        'fee': fee,
        'recipient': account_address,
        'deadline': web3.eth.get_block('latest')['timestamp'] + 60 * 10,
        'amountIn': amountInEther * 10 ** 6,
        'amountOutMinimum': web3.to_wei(amt_min, 'ether'),
        'sqrtPriceLimitX96': 0
    }).build_transaction({
        'from': account_address,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': web3.eth.get_transaction_count(account_address),
        'value': 0
    })

    swap_tx_hash = send_transaction(swap_txn)
    print(f"Swapping {amountInEther} USDC for {asset.upper()}, hash: ", swap_tx_hash.hex())
  
def getBalance(asset):
    if asset.lower() == "eth":
        return web3.from_wei(web3.eth.get_balance(account_address), 'ether')
    
    elif asset.lower() == "weth":
        x =  weth_contract.functions.balanceOf(account_address).call()
        return web3.from_wei(x, 'ether')
    
    elif asset.lower() == "usdc":
        x= usdc_contract.functions.balanceOf(account_address).call()
        x = web3.to_wei(x, 'szabo')
        return web3.from_wei(x, 'ether')
    
    elif asset.lower() == "arb":
        x= arb_contract.functions.balanceOf(account_address).call()
        return web3.from_wei(x, 'ether')

    else:
        print("Invalid asset in getBalance")
        return

def getAllowance(asset):
    if asset.lower() == "weth":
        x= weth_contract.functions.allowance(account_address, uniswap_router_address).call()
        return web3.from_wei(x, 'ether')
    
    elif asset.lower() == "usdc":
        x= usdc_contract.functions.allowance(account_address, uniswap_router_address).call()
        return web3.from_wei(web3.to_wei(x, 'szabo'), 'ether')
    
    elif asset.lower() == "arb":
        x= arb_contract.functions.allowance(account_address, uniswap_router_address).call()
        return web3.from_wei(x, 'ether')
    
    else:
        print("Invalid asset")
        return

def getAllBalances():
    print("Eth Balance:", getBalance('eth'))
    print("Weth Balance:", getBalance('weth'))
    print("Usdc Balance:", getBalance('usdc'))
    print("Arb Balance:", getBalance('arb'))

def getAllAllowances():
    print("Weth Allowance:", getAllowance('weth'))
    print("Usdc Allowance:", getAllowance('usdc'))
    print("Arb Allowance:", getAllowance('arb'))

def WrapEth(amountInEther):
    wrap_txn = weth_contract.functions.deposit().build_transaction({
        'from': account_address,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': web3.eth.get_transaction_count(account_address),
        'value': web3.to_wei(amountInEther, 'ether')
    })

    wrap_tx_hash = send_transaction(wrap_txn)
    print("Wrapping {0} ETH. Hash: {1}".format(amountInEther, wrap_tx_hash.hex()))

def unwrapWeth(amountInEther=getBalance('weth')):
    unwrap_txn = weth_contract.functions.withdraw(web3.to_wei(amountInEther, 'ether')).build_transaction({
        'from': account_address,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': web3.eth.get_transaction_count(account_address),
        'value': 0
    })

    unwrap_tx_hash = send_transaction(unwrap_txn)
    print("Unwrapping {0} WETH. Hash: {1}".format(amountInEther, unwrap_tx_hash.hex()))

def infiniteApproveAll():
    approveAsset('weth', web3.from_wei(2**256-1, 'ether'))
    approveAsset('usdc', web3.from_wei(2**256-1, 'ether'))
    approveAsset('arb', web3.from_wei(2**256-1, 'ether'))

def revokeApproveAll():
    approveAsset('weth', 0)
    approveAsset('usdc', 0)
    approveAsset('arb', 0)

def buyEth():
    usdcToAsset('eth', getBalance('usdc'))

def sellEth():
    assetToUsdc('eth', getBalance('weth'))

def main():
    #sample use: 
    infiniteApproveAll()
    assetToUsdc('weth', 0.1)
    usdcToAsset('arb', getBalance('usdc'))
    getAllBalances()
    
