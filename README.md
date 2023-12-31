# Uniswap-V3-Python-Bot

## Description
This Python Bot interacts with the Arbitrum blockchain to perform various operations on Uniswap V3 using the Web3 library. It allows for token swaps, token approvals, checking balances, and wrapping/unwrapping ETH as WETH.

# Key Features
- Connectivity: The app connects to the Arbitrum network using the Web3 library and can be configured to connect to a local node or a remote node via Ankr.

- Token Swaps: The app allows users to swap ERC-20 tokens like WETH (Wrapped Ethereum) and USDC (USD Coin) for other ERC-20 tokens (the code currently only contains ARB,USDC,WETH but can be configured to swap to more tokens) using Uniswap V3's exact input single method.

- Token Approvals: The app facilitates token approvals for Uniswap V3 trading. Users can approve an infinite or custom amount as well as revoke approvals.

- Token Balances: Users can check their account balances on the connected Arbitrum network.

- Token Allowances: The app allows users to check the allowances granted to Uniswap V3 for spending their tokens.

# Possible Use Cases
- Command-Line Interface (CLI): Users can create a custom CLI using the bot's functions for faster execution, avoiding the need to wait for a UI/UX interface to load and having to manually sign and approve transactions. The CLI allows for efficient and quick interaction with the Uniswap V3 platform.
- Integration with Custom Strategies: Users can seamlessly integrate the bot with their custom trading strategies. By automating the execution of trades and approvals, users can focus more on refining their strategies rather than dealing with manual transaction management.


# Setup

### Prerequisites
1. Python 3.x installed (https://www.python.org/downloads/).
2. A private key for the Ethereum account that will be used to perform transactions.
3. An active Ethereum node connection. You can use either a local node (Tested on Ganache) or connect to a remote node via Ankr.


### Installation
1. Clone this repository to your local machine:
   ```
   git clone https://github.com/Sakaar-Sen/Uniswap-V3-Python-Bot.git
   cd Uniswap-V3-Python-Bot
2. Install required Python packages using pip
   ``` 
   pip install web3
   pip install eth_account  
   pip install ccxt
3. Configure the Private Key:
Replace the empty private_key variable in the main.py file with your Ethereum account's private key or use an ENV file (recommended).

4. Set Gas Price and Gas Limit (Optional):
If required, adjust the gas_price and gas_limit variables in the main.py file according to your needs.

### Example 
The main function demonstrates a sample use case, where it approves all tokens for an infinite amount, swaps 0.1 WETH for USDC, converts USDC to Arb, and finally displays all account balances.

# Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.




