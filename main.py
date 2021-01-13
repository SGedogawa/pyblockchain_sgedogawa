from mylib import wallet

if __name__ == '__main__':
    # my_blockchain_address = 'my_blockchain_address'
    # block_chain = blockchain.BlockChain(my_blockchain_address)
    # block_chain.add_transaction('A', 'B', 5.0)
    # block_chain.mining()
    #
    # utils.pprint(block_chain.chain)

    wallet_M = wallet.Wallet()
    wallet_A = wallet.Wallet()
    wallet_B = wallet.Wallet()

    t = wallet.Transaction(
        wallet_A.private_key, wallet_A.public_key, wallet_B.blockchain_address, 'B', 1.0
    )

    print(t.generate_signature())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
