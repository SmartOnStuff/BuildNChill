import asyncio
from os import getenv

import rsa
import hashlib
from eth_account.messages import encode_defunct

from alith.data import encrypt
from alith.data.storage import (
    GetShareLinkOptions,
    PinataIPFS,
    StorageError,
    UploadOptions,
)
from alith.lazai import Client

privacy_data = """\
LazaiTrader
AI-Powered Decentralized Trading Assistant on Hyperion Testnet

LazaiTrader is an intelligent trading assistant that combines AI-powered automation with community-driven strategy optimization. Built on the Hyperion testnet, it offers a complete trading experience through Telegram with advanced features like the Strategy Vault, real-time analytics, and AI-driven support.

Key Features
Intelligent Trading
Automated Martingale Strategy: Dynamic buy-low, sell-high with consecutive trade multipliers
Multi-Pair Support: Trade tgMetis-USDC, tgETH-USDC, and more
Real-Time Execution: Blockchain-integrated smart contract trading
Risk Management: Configurable trade percentages, triggers, and safety limits
AI-Powered Support
Alith Support Agent: LangChain-powered customer support with document intelligence
Strategy Vault: Secure, privacy-preserving community strategy sharing
Personalized Suggestions: AI recommendations based on collective performance data
Vector-Based Knowledge: GitHub documentation integration with semantic search
Advanced Analytics
Real-Time Charts: Multi-pair trading visualization with PnL tracking
Trade History: Comprehensive logging with USD value tracking
Performance Metrics: Detailed balance and trade value analysis
Export Capabilities: Data contribution to decentralized analytics
Security and Privacy
TEE Integration: Trusted Execution Environment for secure data processing
Wallet-Signed Encryption: User-controlled data privacy
Testnet Safety: Risk-free testing environment
Decentralized Storage: IPFS-based data distribution
Quick Start
1. Join the Ecosystem
Main Trading Bot: https://t.me/LazaiTrader_bot
AI Support Agent: https://t.me/LazaiTrader_alithbot
Community Group: https://t.me/LazaiTrader
2. Get Your Funded Wallet
Send /start to the bot
Receive automatically funded testnet wallet:
100 tgUSDC
10,000,000 tgMetis
0.1 testgETH
3. Configure Your Strategy
/config → Select Pair → Choose Risk Level → Fine-tune Parameters → Start Trading!
4. Monitor and Optimize
/chart        View your trading performance
/contribute   Add data to Strategy Vault
/suggestion   Get AI recommendations
/balance      Check wallet balances
System Architecture
LazaiTrader employs a sophisticated multi-component architecture designed for scalability, security, and intelligence.

(Diagram and Mermaid code removed for brevity, let me know if you'd like it cleaned too.)

Core Components
Main Trading Bot
User Management
Configuration System
Trading Execution
Analytics
Strategy Vault
Alith Support Agent
Document Intelligence
Vector Storage
AI Conversation
Memory Management
Trading Engine
Price Monitoring
Trade Execution
Risk Management
Oracle Updates
Installation and Setup (For Developers Only)
Prerequisites
Python >= 3.8
Node.js >= 16
Git
Environment Setup
Clone Repository
Install Dependencies
Configure .env file
Add Configuration Files
Wallet Setup
Running the System
python plugins/alith_bot.py
python plugins/main_bot.py
python main.py
User Guide
Getting Started
/start          Register and get funded wallet
/wallet         View your wallet address
/balance        Check token balances
Strategy Configuration
/config         Interactive strategy setup
/myconfig       View active configurations
/deleteconfig   Remove configurations
Analytics and Optimization
/chart          View trading charts and PnL
/contribute     Add data to Strategy Vault
/suggestion     Get AI strategy recommendations
Community Support
Use @LazaiTrader_alithbot for:

Strategy advice
Technical questions
Command help
Troubleshooting
Trading Strategy Explained
Martingale Strategy with Multipliers

Price drops 5% → Buy $10 worth of tgMetis
Price drops 5% again → Buy $15 worth
Price drops 5% again → Buy $22.50 worth
Price recovers 5% → Sell $22.50 worth
Price recovers 5% → Sell $15 worth
Configuration Files
config/tokens.json and config/config.json
(JSON content preserved and cleaned — let me know if you want it formatted separately.)

AI Support Agent
Features:

Document Intelligence
Vector Search
Contextual Memory
Support-Focused Personality
Strategy Vault
Key Features:

TEE Security
Wallet-Signed Encryption
Anonymous Analytics
AI Recommendations
Security and Privacy
Multi-Layer Protection:

Testnet Safety
Data Encryption
TEE Integration
Access Controls
API Reference
Main Bot Commands:

/start, /wallet, /balance
/config, /myconfig, /deleteconfig
/chart, /contribute, /suggestion
/withdraw, /cancel
Alith Agent Integration:

Direct Chat: https://t.me/LazaiTrader_alithbot
Group Support: Mention in @LazaiTrader group
Performance and Monitoring
Chart Features:

Multi-Pair Visualization
PnL Calculation
Trade Markers
Balance Tracking
Roadmap
Phases:

Enhanced Security
Advanced Trading
Community Features
Enterprise Expansion
Contributing
Development Setup:

Fork, clone, create feature branch
Install dev dependencies
Run tests
Submit pull request
Contribution Areas:

Strategy Development
AI Enhancement
Security Audits
Documentation
Testing
External Resources
Hyperion Testnet: https://hyperion.metis.io
Metis Docs: https://docs.metis.io
LazAI Network: https://lazai.network
LangChain: https://langchain.com
Web3.py: https://web3py.readthedocs.io
FAQ
No real money involved during testing
Strategy Vault uses encrypted, anonymous data
Choose trading pairs based on volatility preference
Bot trades only on configured price movements
Strategies can be changed anytime
Support
Alith AI Agent: https://t.me/LazaiTrader_alithbot
Community Group: https://t.me/LazaiTrader
Documentation and GitHub Issues
License
MIT License

Acknowledgments
Thanks to gMetis, Metis Andromeda, Lazai Network, DeepSeek AI, LangChain, and Telegram.
"""


async def main():
    client = Client()
    ipfs = PinataIPFS()
    try:
        # 1. Prepare your privacy data and encrypt it
        data_file_name = "your_encrypted_dat2.txt"
        privacy_data_sha256 = hashlib.sha256(privacy_data.encode()).hexdigest()
        encryption_seed = "Sign to retrieve your encryption key"
        message = encode_defunct(text=encryption_seed)
        password = client.wallet.sign_message(message).signature.hex()
        encrypted_data = encrypt(privacy_data.encode(), password)
        # 2. Upload the privacy data to IPFS and get the shared url
        token = getenv("IPFS_JWT", "")
        file_meta = await ipfs.upload(
            UploadOptions(name=data_file_name, data=encrypted_data, token=token)
        )
        url = await ipfs.get_share_link(
            GetShareLinkOptions(token=token, id=file_meta.id)
        )
        # 3. Upload the privacy url to LazAI
        file_id = client.get_file_id_by_url(url)
        if file_id == 0:
            file_id = client.add_file_with_hash(url, privacy_data_sha256)
        print("File ID:", file_id)
        pub_key = client.get_public_key()
        encryption_key = rsa.encrypt(
            password.encode(),
            rsa.PublicKey.load_pkcs1(pub_key.strip().encode(), format="PEM"),
        ).hex()
        client.add_permission_for_file(
            file_id, client.contract_config.data_registry_address, encryption_key
        )
    except StorageError as e:
        print(f"Error: {e}")
    except Exception as e:
        raise e
    finally:
        await ipfs.close()


if __name__ == "__main__":
    asyncio.run(main())