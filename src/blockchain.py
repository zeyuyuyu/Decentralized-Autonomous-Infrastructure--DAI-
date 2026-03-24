"""Core blockchain synchronization and validation module"""

import hashlib
import json
import time
from typing import List, Dict, Optional

class Block:
    def __init__(self, index: int, transactions: List[Dict], timestamp: float,
                 previous_hash: str, nonce: int = 0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions: List[Dict] = []
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=time.time(),
            previous_hash='0'
        )
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, block: Block) -> bool:
        if self.is_valid_block(block, self.get_latest_block()):
            self.chain.append(block)
            return True
        return False

    def is_valid_block(self, block: Block, previous_block: Block) -> bool:
        if previous_block.index + 1 != block.index:
            return False

        if previous_block.hash != block.previous_hash:
            return False

        if block.calculate_hash() != block.hash:
            return False

        if not self.is_valid_proof(block.hash):
            return False

        return True

    def is_valid_proof(self, block_hash: str) -> bool:
        return block_hash.startswith('0' * self.difficulty)

    def proof_of_work(self, block: Block) -> int:
        block.nonce = 0
        computed_hash = block.calculate_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.calculate_hash()
        return block.nonce

    def add_transaction(self, sender: str, recipient: str, amount: float) -> None:
        self.pending_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

    def mine_pending_transactions(self, miner_address: str) -> Optional[Block]:
        if not self.pending_transactions:
            return None

        block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            timestamp=time.time(),
            previous_hash=self.get_latest_block().hash
        )

        self.proof_of_work(block)
        self.add_block(block)
        self.pending_transactions = [
            {'sender': 'network', 'recipient': miner_address, 'amount': 10.0}
        ]
        return block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if not self.is_valid_block(current_block, previous_block):
                return False

        return True

    def replace_chain(self, new_chain: List[Block]) -> bool:
        if len(new_chain) <= len(self.chain):
            return False

        if not self.is_chain_valid():
            return False

        self.chain = new_chain
        return True
