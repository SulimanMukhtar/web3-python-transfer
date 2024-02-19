from eth_account import Account
from web3 import Web3

# this code will loop through your x accounts diverted from the mnemonic_phrase and transfer all balance to one account
mnemonic_phrase = ""
target_wallet = ""
num_accounts = 50
# Connect to BSC mainnet
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))


def generate_private_keys(mnemonic, accounts_num):
    private_keys = []
    Account.enable_unaudited_hdwallet_features()
    for i in range(accounts_num):
        account_ob = Account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{i}")
        private_keys.append(account_ob.key.hex())
    return private_keys


wallet_keys = generate_private_keys(mnemonic_phrase, num_accounts)


def transfer_bnb(account_ob, receiver_address, balance):
    gas_price = w3.to_wei('3', 'gwei')  # Gas price in Wei (3 Gwei)
    gas_limit = 21000
    fee = gas_price * gas_limit
    value = balance - fee
    total_value = value + fee

    if balance < total_value:
        raise ValueError("Insufficient balance to cover transaction value and gas fee.")

    nonce = w3.eth.get_transaction_count(account_ob.address)
    tx = {
        'nonce': nonce,
        'to': receiver_address,
        'value': value,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'chainId': 56,  # BSC mainnet chain ID
    }
    signed_tx = account_ob.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)


def get_account_from_private_key(key):
    return w3.eth.account.from_key(key)


def get_balance(address):
    return w3.eth.get_balance(address)


for private_key in wallet_keys:
    account = get_account_from_private_key(private_key)
    if account.address == target_wallet:
        pass
    else:
        balance = get_balance(account.address)
        balance_in_BNB = w3.from_wei(balance, 'ether')
        print(f"Address: {account.address}, Balance: {balance_in_BNB} BNB")
        if balance > 0:
            tx_receipt = transfer_bnb(account, target_wallet, balance)
            print(f"Transferred {balance_in_BNB} BNB from {account.address} to {target_wallet}. Transaction hash: {tx_receipt.transactionHash.hex()}")

target_wallet_balance = w3.from_wei(get_balance(target_wallet), 'ether')
print(f"Transfer Completed with final balance of {target_wallet_balance} for {target_wallet}")
