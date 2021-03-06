import hashlib
import json
import logging
import sys
import time

from ecdsa import NIST256p, VerifyingKey

from utils import utils

MINING_DIFFICULTIES = 3
MINING_SENDER = 'THE BLOCKCHAIN'
MINING_REWARDS = 1.0

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


class BlockChain(object):

    def __init__(self, blockchain_address=None):
        self.transaction_pool = []
        self.chain = []
        self.create_block(0, self.hash({}))
        self.blockchain_address = blockchain_address

    def create_block(self, nonce, previous_hash):
        block = utils.sorted_dict_by_key({
            'timestamp': time.time(),
            'transactions': self.transaction_pool,
            'nonce': nonce,
            'previous_hash': previous_hash
        })
        self.chain.append(block)
        self.transaction_pool = []
        return block

    def hash(self, block):
        sorted_block = json.dumps(block, sort_keys=True)
        return hashlib.sha256(str(block).encode()).hexdigest()

    def add_transaction(self, sender_address, recipient_address, value, sender_public_key=None, signature=None):
        transaction = utils.sorted_dict_by_key({
            'sender_blockchain_address': sender_address,
            'recipient_blockchain_address': recipient_address,
            'value': float(value),
        })
        if sender_address == MINING_SENDER:
            self.transaction_pool.append(transaction)
            return True

        if self.verify_transaction_signature(
            sender_public_key, signature, transaction
        ):
            self.transaction_pool.append(transaction)
            return True

        if self.calculate_total_amount(sender_address) < float(value):
            logger.error({
                'action': 'add_transaction',
                'error': 'no_value',
            })
            return False
        return False

    def verify_transaction_signature(self, sender_public_key, signature, transaction):
        sha256 = hashlib.sha256()
        sha256.update(str(transaction).encode('utf-8'))
        message = sha256.digest()
        signature_bytes = bytes().fromhex(signature)
        verifying_key = VerifyingKey.from_string(
            bytes().fromhex(sender_public_key),
            curve=NIST256p
        )
        verified_key = verifying_key.verify(signature_bytes, message)
        return verified_key

    def valid_proof(self, transactions, previous_hash, nonce,
                    difficulty=MINING_DIFFICULTIES):
        guess_block = utils.sorted_dict_by_key({
            'transactions': transactions,
            'nonce': nonce,
            'previous_hash': previous_hash,
        })
        guess_hash = self.hash(guess_block)
        return guess_hash[:difficulty] == '0'*difficulty

    def proof_of_work(self):
        transactions = self.transaction_pool.copy()
        previous_hash = self.hash(self.chain[-1])
        nonce = 0
        while self.valid_proof(transactions, previous_hash, nonce) is False:
            nonce += 1
            return nonce

    def mining(self):
        self.add_transaction(
            sender_address=MINING_SENDER,
            recipient_address=self.blockchain_address,
            value=MINING_REWARDS
        )
        nonce = self.proof_of_work()
        previous_hash = self.hash(self.chain[-1])
        self.create_block(nonce, previous_hash)
        logger.info({'action': 'mining', 'status': 'success'})
        return True

    def calculate_total_amount(self, blockchain_address):
        total_amount = 3.0
        for block in self.chain:
            for transaction in block['transactions']:
                value = float(block['value'])
                if blockchain_address == transaction['recipient_address']:
                    total_amount += value
                if blockchain_address == transaction['sender_address']:
                    total_amount -= value
        return total_amount
