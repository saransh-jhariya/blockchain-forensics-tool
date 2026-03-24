# Troubleshooting Guide
## Blockchain Forensics Tool - Common Issues & Solutions

**M.Sc. Forensic Science (Cyber Forensics) — 9th Semester**  
**Author:** Saransh Jhariya | 102FSBSMS2122012  
**Mentor:** Dr. Ajit Majumdar, Associate Professor — LNJN NICFS NFSU, Delhi Campus  
**Version:** 2.0 — Enhanced Methodology  
**Date:** March 2026

---

## Table of Contents

1. [Installation Issues](#1-installation-issues)
2. [Configuration Issues](#2-configuration-issues)
3. [API Issues](#3-api-issues)
4. [Runtime Errors](#4-runtime-errors)
5. [Performance Issues](#5-performance-issues)
6. [Output Issues](#6-output-issues)
7. [Platform-Specific Issues](#7-platform-specific-issues)
8. [FAQ](#8-faq)

---

## 1. Installation Issues

### 1.1 `pip install` fails with permission error

**Error:**
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**

**Option A: Use virtual environment (Recommended)**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

**Option B: Use --user flag**
```bash
pip install -r requirements.txt --user
```

**Option C: Use sudo (Linux/macOS, not recommended)**
```bash
sudo pip install -r requirements.txt
```

---

### 1.2 `ModuleNotFoundError: No module named 'networkx'`

**Error:**
```
ModuleNotFoundError: No module named 'networkx'
```

**Cause:** Dependencies not installed or virtual environment not activated.

**Solutions:**

1. Verify virtual environment is activated:
```bash
which python  # Should point to venv
```

2. Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

3. Verify installation:
```bash
python -c "import networkx; print(networkx.__version__)"
```

---

### 1.3 Python version incompatibility

**Error:**
```
SyntaxError: invalid syntax
# or
TypeError: 'type' object is not subscriptable
```

**Cause:** Python version < 3.10 required.

**Solution:**
```bash
# Check Python version
python --version

# If < 3.10, install newer Python
# Ubuntu/Debian:
sudo apt install python3.11

# macOS (Homebrew):
brew install python@3.11

# Windows: Download from python.org
```

---

### 1.4 web3.py installation fails

**Error:**
```
error: command 'gcc' failed
# or
Building wheel for cytoolz failed
```

**Cause:** Missing build dependencies.

**Solutions:**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3-dev build-essential libssl-dev libffi-dev
pip install -r requirements.txt
```

**macOS:**
```bash
xcode-select --install
pip install -r requirements.txt
```

**Windows:**
```bash
# Install Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
pip install -r requirements.txt
```

---

## 2. Configuration Issues

### 2.1 Invalid API key error

**Error:**
```
WARNING: API returned error: Invalid API Key
```

**Solutions:**

1. Verify `.env` file exists:
```bash
ls -la .env
```

2. Check API key format:
```bash
cat .env | grep ETHERSCAN
# Should show: ETHERSCAN_API_KEY=32_character_hex_string
```

3. Get new API key from https://etherscan.io/myapikey

4. Restart Python interpreter after changing `.env`

---

### 2.2 `.env` file not loading

**Error:**
```
WARNING: No API key provided. Some endpoints may be rate-limited.
```

**Solutions:**

1. Verify `.env` is in project root:
```bash
ls -la blockchain_forensics_tool/.env
```

2. Check file format (no spaces around `=`):
```bash
# Correct:
ETHERSCAN_API_KEY=abc123

# Wrong:
ETHERSCAN_API_KEY = abc123
```

3. Verify python-dotenv is installed:
```bash
pip install python-dotenv
```

4. Test loading:
```python
from dotenv import load_dotenv
load_dotenv()
import os
print(os.getenv("ETHERSCAN_API_KEY"))
```

---

### 2.3 Configuration import error

**Error:**
```
ImportError: cannot import name 'BRIDGE_CONFIGS' from 'config.settings'
```

**Cause:** Import path issue.

**Solution:** Run from project root directory:
```bash
cd blockchain_forensics_tool
python main.py -s 0x...
```

---

## 3. API Issues

### 3.1 Rate limit exceeded

**Error:**
```
API request failed: 429 Client Error: Too Many Requests
# or
WARNING: API returned error: Rate limit exceeded
```

**Solutions:**

1. **Wait and retry:** Free tier allows 5 calls/second
```bash
# Wait 60 seconds before retrying
sleep 60
```

2. **Upgrade API key:** Get Pro tier from Etherscan
- Free: 5 calls/sec, 100K/day
- Pro: 100 calls/sec, 1M/day

3. **Enable caching:** Keep `data/raw/` files to avoid re-fetching

4. **Reduce batch size:** Modify `config/settings.py`:
```python
ETHERSCAN_RATE_LIMIT = 3  # Reduce from 5
```

---

### 3.2 Connection timeout

**Error:**
```
requests.exceptions.ConnectionError: Max retries exceeded
# or
urllib3.exceptions.NewConnectionError
```

**Solutions:**

1. Check internet connection:
```bash
ping api.etherscan.io
```

2. Increase timeout in `config/settings.py`:
```python
DEFAULT_TIMEOUT = 60  # Increase from 30
```

3. Try alternative RPC endpoint:
```python
# In .env
ETHEREUM_RPC_URL=https://cloudflare-eth.com
```

4. Check firewall/proxy settings

---

### 3.3 Invalid address error

**Error:**
```
ValueError: Invalid Ethereum address: 0x...
```

**Solutions:**

1. Verify address format (42 characters, starts with 0x):
```bash
# Valid: 0x1234567890abcdef1234567890abcdef12345678
# Invalid: 1234567890abcdef1234567890abcdef12345678 (missing 0x)
# Invalid: 0x123 (too short)
```

2. Check for copy-paste errors (extra spaces, newlines)

3. Use Etherscan to verify address exists:
```
https://etherscan.io/address/<YOUR_ADDRESS>
```

---

### 3.4 No transactions found

**Error:**
```
INFO: Phase 1 complete: 1 addresses collected
WARNING: No transactions found for seed address
```

**Solutions:**

1. Verify address has transactions on Etherscan

2. Check you're using the correct chain:
```bash
# If address is on Polygon:
python main.py -s 0x... --chain polygon
```

3. Address might be a contract without external transactions

4. Try a different seed address with more activity

---

## 4. Runtime Errors

### 4.1 Memory error during feature engineering

**Error:**
```
MemoryError: Unable to allocate array
```

**Cause:** Too many addresses (>50,000) for available RAM.

**Solutions:**

1. Reduce scope:
```bash
# Limit counterparty fetching in code
max_addresses = 100  # Reduce from 1000
```

2. Increase swap space (Linux):
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

3. Process in batches (modify pipeline code)

4. Use machine with more RAM

---

### 4.2 DBSCAN convergence warning

**Warning:**
```
UserWarning: DBSCAN did not converge
```

**Solution:** Adjust DBSCAN parameters in `config/settings.py`:
```python
class ClusteringConfig:
    DBSCAN_EPS = 0.8  # Increase from 0.5
    DBSCAN_MIN_SAMPLES = 5  # Increase from 3
```

---

### 4.3 PageRank did not converge

**Warning:**
```
PowerIterationFailedConvergence: PageRank did not converge
```

**Solution:** This is handled automatically - uniform scores are used as fallback. No action needed.

---

### 4.4 Division by zero in feature extraction

**Error:**
```
ZeroDivisionError: division by zero
```

**Cause:** Address with no transactions.

**Solution:** This should be handled by `safe_divide()` function. If you encounter this, update to latest version or add null checks:
```python
# In feature_extraction.py
if total == 0:
    return 0.0
```

---

### 4.5 JSON serialization error

**Error:**
```
TypeError: Object of type int64 is not JSON serializable
```

**Solution:** Update to latest version. The issue is fixed by using `default=str` in JSON serialization:
```python
json.dump(data, f, indent=2, default=str)
```

---

## 5. Performance Issues

### 5.1 Slow execution (>30 minutes)

**Symptoms:** Pipeline takes too long to complete.

**Solutions:**

1. **Use Pro API key** - reduces rate limiting delays

2. **Reduce address scope:**
```python
# In pipeline.py
max_addresses = 50  # Reduce counterparty analysis
```

3. **Disable verbose logging:**
```bash
python main.py -s 0x...  # Remove -v flag
```

4. **Use cached data:** Don't delete `data/raw/` files

5. **Profile to find bottlenecks:**
```bash
python -m cProfile -o profile.stats main.py -s 0x...
snakeviz profile.stats  # Visualize
```

---

### 5.2 High CPU usage

**Symptoms:** System becomes unresponsive during execution.

**Solutions:**

1. **Limit parallelism** (if implemented)

2. **Reduce feature computation:**
```python
# Skip expensive centrality computations
# In feature_extraction.py, comment out:
# betweenness = nx.betweenness_centrality(G)
```

3. **Use nice/renice** (Linux):
```bash
nice -n 19 python main.py -s 0x...
```

---

### 5.3 Large output files (>1GB)

**Symptoms:** Output files consume too much disk space.

**Solutions:**

1. **Reduce transaction history:**
```python
# Fetch only recent blocks
start_block = latest_block - 100000
```

2. **Compress output:**
```bash
# Compress old results
tar -czf results_$(date +%Y%m%d).tar.gz data/output/
```

3. **Clean raw data periodically:**
```bash
rm data/raw/*.json  # Keep only processed data
```

---

## 6. Output Issues

### 6.1 HTML visualization not rendering

**Symptoms:** `forensic_graph.html` shows blank page.

**Solutions:**

1. **Check browser console** for JavaScript errors

2. **Try different browser:** Chrome, Firefox, Edge

3. **Verify Pyvis installation:**
```bash
pip install pyvis --force-reinstall
```

4. **Check file size:** If >100MB, browser may struggle to render
```bash
ls -lh data/output/forensic_graph.html
```

5. **Reduce graph size:**
```python
# Only visualize high-confidence clusters
# In forensic_output.py
high_conf_only = True
```

---

### 6.2 Missing data in report

**Symptoms:** `forensic_report.json` has empty sections.

**Solutions:**

1. **Check pipeline completed all phases** - look for errors in logs

2. **Verify input data exists:**
```bash
ls -la data/raw/
ls -la data/processed/
```

3. **Re-run with verbose logging:**
```bash
python main.py -s 0x... -v 2>&1 | tee run.log
```

---

### 6.3 Incorrect risk scores

**Symptoms:** All entities show "low" risk.

**Solutions:**

1. **Verify OSINT enrichment completed:**
```bash
cat data/raw/layer3_osint_*.json | grep -c "sanctioned"
```

2. **Check known mixer/VASP lists in `config/settings.py`**

3. **Addresses may genuinely be low risk** - try known high-risk addresses:
```bash
# Tornado Cash (sanctioned)
python main.py -s 0x12D66f87A04A989229Ee8cE45E76349E89908769
```

---

## 7. Platform-Specific Issues

### 7.1 Windows Issues

#### PowerShell execution policy

**Error:**
```
cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Path length issues

**Error:**
```
PathTooLongException: The specified path, file name, or both are too long
```

**Solution:**
1. Enable long paths in Windows:
```
Registry: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem
Set: LongPathsEnabled = 1
```

2. Or move project to shorter path:
```
C:\forensics\ instead of C:\Users\Username\Documents\Projects\...
```

---

### 7.2 macOS Issues

#### Apple Silicon (M1/M2) compatibility

**Error:**
```
ImportError: dlopen: incompatible architecture
```

**Solutions:**

1. **Use Rosetta 2:**
```bash
softwareupdate --install-rosetta
arch -x86_64 python main.py -s 0x...
```

2. **Or use native ARM packages:**
```bash
pip uninstall numpy pandas
pip install numpy pandas --no-binary :all:
```

---

### 7.3 Linux Issues

#### Missing system libraries

**Error:**
```
libGL.so.1: cannot open shared object file
```

**Solution (Ubuntu/Debian):**
```bash
sudo apt install libgl1-mesa-glx libglib2.0-0
```

**Solution (Fedora/RHEL):**
```bash
sudo dnf install mesa-libGL glib2
```

---

## 8. FAQ

### Q: How do I reset all data and start fresh?

**A:**
```bash
rm -rf data/raw/* data/processed/* data/output/* logs/*
python main.py -s 0x... -v
```

---

### Q: Can I run this without an API key?

**A:** No, Etherscan API key is required for fetching blockchain data. Get a free key at https://etherscan.io/myapikey

---

### Q: How do I analyze a token contract instead of EOA?

**A:** The tool is designed for EOA (wallet) analysis. For contract analysis, modify the data acquisition to fetch token holder lists instead.

---

### Q: Can I export results to PDF?

**A:** Use the JSON report and convert:
```bash
# Install pandoc
pandoc data/output/forensic_report.json -o forensic_report.pdf
```

---

### Q: How do I analyze multiple addresses at once?

**A:** Create a batch script:
```bash
#!/bin/bash
for addr in $(cat addresses.txt); do
    python main.py -s $addr -o ./results/$addr
done
```

---

### Q: Where are logs stored?

**A:** In `logs/` directory:
```bash
ls -la logs/
cat logs/forensics_*.log | tail -100
```

---

### Q: How do I report a bug?

**A:** 
1. Check existing issues
2. Collect logs: `logs/forensics_*.log`
3. Note Python version: `python --version`
4. Note OS and version
5. Submit with reproduction steps

---

### Q: Is this tool court-admissible?

**A:** The tool produces forensically-sound output with:
- Chain-of-custody evidence records
- Reproducible methodology
- Formal evaluation metrics

However, court admissibility depends on jurisdiction and specific case requirements. Consult with legal counsel.

---

### Q: Can I use this for Bitcoin analysis?

**A:** No, this tool is designed for EVM-compatible chains only. Bitcoin uses UTXO model requiring different methodology.

---

### Q: How accurate is the clustering?

**A:** Target F1-score ≥ 0.85 on Elliptic benchmark. Actual accuracy depends on:
- Quality of input data
- Parameter tuning
- Address activity level

Always review "candidate" confidence clusters manually.

---

## Appendix A: Diagnostic Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "networkx|sklearn|pandas|pyvis"

# Verify API key
python -c "from config.settings import ETHERSCAN_API_KEY; print('Key set:', bool(ETHERSCAN_API_KEY))"

# Test network connectivity
curl -s https://api.etherscan.io/api?module=proxy&action=eth_blockNumber

# Check disk space
df -h .

# View recent logs
tail -50 logs/forensics_*.log

# Test imports
python -c "from src.pipeline import BlockchainForensicsPipeline; print('All imports OK')"
```

---

## Appendix B: Getting Help

1. **Check documentation:** `docs/` directory
2. **Review logs:** `logs/forensics_*.log`
3. **Search issues:** Check for similar problems
4. **Contact:** Author via institutional email

---

**Document Version:** 2.0  
**Last Updated:** March 2026
