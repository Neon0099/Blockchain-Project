import hashlib
import json
from time import time
from uuid import uuid4


class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: The proof given by the Proof of Work algorithm (nonce)
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,  # This is the nonce
            'previous_hash': previous_hash or self.hash(self.chain[-1]),  # Hash of the previous block
            'current_hash': None  # Placeholder for the current hash
        }

        # Calculate and store the current block's hash
        block['current_hash'] = self.hash(block)

        # Reset the current list of transactions
        self.current_transactions = []

        # Add the new block to the chain
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        """
        Returns the last block in the chain
        """
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        :return: <str> Hash of the block
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:
        - Find a number p' such that hash(pp') contains leading 2 zeroes
        - Where p is the previous proof, and p' is the new proof
        :param last_block: <dict> last Block
        :return: <int> Proof (nonce)
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while not self.valid_proof(last_proof, proof, last_hash):
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof: Does hash(last_proof, proof, last_hash) contain 2 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:2] == "00"  # Check if it starts with two zeroes

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            # Check that the previous hash is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block['current_hash']):
                return False

            last_block = block
            current_index += 1

        return True


# User Interaction Section

def print_menu():
    print("\nBlockchain Menu:")
    print("1. Mine a new block")
    print("2. Add a new transaction")
    print("3. Display the blockchain")
    print("4. Exit")


def mine_block(blockchain):
    """
    Function to mine a new block
    """
    if not blockchain.current_transactions:
        print("No transactions to mine.")
        return

    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # Miner receives a reward for finding the proof
    blockchain.new_transaction(
        sender="0",  # Reward for mining
        recipient=str(uuid4()).replace('-', ''),
        amount=1,
    )

    # Forge the new block
    block = blockchain.new_block(proof)
    print(f"New block mined! Block index: {block['index']}")


def add_transaction(blockchain):
    """
    Function to add a new transaction
    """
    sender = input("Enter the sender: ")
    recipient = input("Enter the recipient: ")
    amount = input("Enter the amount: ")

    index = blockchain.new_transaction(sender, recipient, float(amount))
    print(f"Transaction will be added to block {index}")


def display_chain(blockchain):
    """
    Function to display the entire blockchain
    """
    for block in blockchain.chain:
        print(json.dumps(block, indent=4))


if __name__ == "__main__":
    # Instantiate the Blockchain
    blockchain = Blockchain()

    while True:
        print_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            mine_block(blockchain)
        elif choice == '2':
            add_transaction(blockchain)
        elif choice == '3':
            display_chain(blockchain)
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please choose a valid option.")
