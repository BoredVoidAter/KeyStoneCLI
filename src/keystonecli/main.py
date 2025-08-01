import os
import json
from cryptography.fernet import Fernet

class KeyStoneCLI:
    def __init__(self, vault_path="~/.keystone_vault.json"):
        self.vault_path = os.path.expanduser(vault_path)
        self.key = None
        self.vault = {}

    def _load_key(self):
        key_path = self.vault_path.replace(".json", ".key")
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(key_path, "wb") as f:
                f.write(self.key)

    def _load_vault(self):
        if os.path.exists(self.vault_path):
            with open(self.vault_path, "r") as f:
                self.vault = json.load(f)

    def _save_vault(self):
        with open(self.vault_path, "w") as f:
            json.dump(self.vault, f, indent=4)

    def initialize_vault(self, master_password):
        self._load_key()
        # For simplicity, master_password is not directly used for encryption key derivation here.
        # In a real application, a KDF like PBKDF2 would be used to derive the key from the password.
        print("Vault initialized. Remember your master password!")
        self._save_vault()

    def store_credentials(self, name, value):
        if not self.key:
            print("Vault not initialized. Please initialize it first.")
            return

        f = Fernet(self.key)
        encrypted_value = f.encrypt(value.encode()).decode()
        self.vault[name] = encrypted_value
        self._save_vault()
        print(f"Credential '{name}' stored securely.")

    def retrieve_credentials(self, name):
        if not self.key:
            print("Vault not initialized. Please initialize it first.")
            return
        if name not in self.vault:
            print(f"Credential '{name}' not found.")
            return

        f = Fernet(self.key)
        encrypted_value = self.vault[name].encode()
        decrypted_value = f.decrypt(encrypted_value).decode()
        return decrypted_value

    def list_secrets(self):
        if not self.key:
            print("Vault not initialized. Please initialize it first.")
            return
        if not self.vault:
            print("No secrets stored in the vault.")
            return

        print("Stored secrets:")
        for name in self.vault.keys():
            print(f"- {name}")

if __name__ == "__main__":
    cli = KeyStoneCLI()
    # Example Usage (for demonstration purposes)
    # In a real CLI, these would be command-line arguments
    cli.initialize_vault("my_master_password")
    cli.store_credentials("my_api_key", "sk_live_xxxxxxxxxxxx")
    print(f"Retrieved API Key: {cli.retrieve_credentials('my_api_key')}")
    cli.list_secrets()
