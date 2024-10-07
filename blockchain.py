import hashlib
import json
from time import time
from uuid import uuid4


class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []

        # Create the genesis block with dynamic proof-of-work
        self.new_block(proof=self.proof_of_work({'index': 0, 'previous_hash': '1'}), previous_hash='1')

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
            'previous_hash': previous_hash or self.hash(self.chain[-1]),  # Hash of the previous block
            'current_hash': None,  # Placeholder for the current hash
            'proof': proof  # This is the nonce
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

        print(f"Transaction added: {sender} -> {recipient} : {amount}")
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
        Proof of Work Algorithm:
        - Find a number p' (nonce) such that hash(last_block + p') contains leading 2 zeros
        - p is the previous proof, and p' is the new proof
        """
        last_hash = self.hash(last_block)
        proof = 0

        while not self.valid_proof(last_hash, proof):
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_hash, proof):
        """
        Validates the Proof by checking if hash(last_hash + proof) starts with '00'.
        :param last_hash: <str> The hash of the last block
        :param proof: <int> The current proof
        :return: <bool> True if correct, False if not.
        """
        guess = f'{last_hash}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:2] == "00"

    def valid_chain(self):
        """
        Determine if the current blockchain is valid by checking:
        1. The previous_hash of each block matches the hash of the previous block.
        2. The proof of work for each block is valid.
        :return: True if the chain is valid, False otherwise
        """
        last_block = self.chain[0]  # Genesis block
        current_index = 1

        while current_index < len(self.chain):
            block = self.chain[current_index]

            # Check if the 'previous_hash' matches the hash of the last block
            if block['previous_hash'] != self.hash(last_block):
                print(f"Invalid block at index {current_index}: Previous hash does not match.")
                return False

            # Check if the proof of work is valid for this block
            if not self.valid_proof(self.hash(last_block), block['proof']):
                print(f"Invalid proof of work at block {current_index}.")
                return False

            # Move to the next block
            last_block = block
            current_index += 1

        return True


# User Interaction Section

def print_menu():
    print("\nBlockchain Menu:")
    print("1. Mine a new block")
    print("2. Add a new transaction")
    print("3. Display the blockchain")
    print("4. Validate the blockchain")
    print("5. Exit")


def mine_block(blockchain):
    """
    Function to mine a new block
    """
    if not blockchain.current_transactions:
        print("No transactions to mine. Block won't be mined.")
        return

    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # Miner receives a reward for mining
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


def validate_blockchain(blockchain):
    """
    Function to validate the blockchain
    """
    is_valid = blockchain.valid_chain()
    if is_valid:
        print("Blockchain is valid.")
    else:
        print("Blockchain is invalid!")


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
            validate_blockchain(blockchain)
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please choose a valid option.")
