# Stock News Scraper — Benzinga & Nasdaq
**Author:** Vincent Sham  

---

Automated **Selenium-based scrapers** for collecting stock and ETF news headlines from **Benzinga** and **Nasdaq**.  
Designed for **Google Colab** or local execution, the scripts support **incremental updates**, **headless browsers**, and **CSV exports** for downstream AI/ML analysis.

---

## 🚀 Features

- ✅ Scrapes from:
  - [Benzinga](https://www.benzinga.com/)
  - [Nasdaq](https://www.nasdaq.com/)
- ✅ Supports both **stocks** and **ETFs**
- ✅ Headless **Chrome** or **Firefox** automation
- ✅ Incremental mode with resume (`--restart` optional)
- ✅ Time-zone-safe timestamps (Eastern → UTC)
- ✅ CSV outputs for each ticker
- ✅ Compatible with **Google Colab** out-of-the-box

---

## 📁 Project Structure

```
.
├── find_headlines_benzinga.py
├── find_headlines_nasdaq.py
├── list_stocks_benzinga.csv
├── list_stocks_nasdaq.csv
├── README.md
├── requirements.txt
└── headlines/
```

---

## ⚙️ Installation (Google Colab or Local)

### 🧱 1️⃣ System Setup (Colab)

```bash
!apt-get update -y
!apt-get install -y chromium-browser chromium-chromedriver
```

### 🧱 2️⃣ Install Dependencies

```bash
!pip install -r requirements.txt
```

> 💡 *Your Colab runtime already includes Python 3.12+ and most base packages.*

### 🧱 3️⃣ (Optional) Create the list CSV

Each scraper references a file like:
```
data/list/list_stocks_benzinga.csv
```

Example format:

| tic | type | desired_page | last_date | last_headline | last_url | no_headlines |
|-----|------|---------------|------------|----------------|----------|---------------|
| AAPL | stocks | 0 | 2025-10-10 | Apple launches new product | https://www.benzinga.com/... | 10 |

The scraper updates `desired_page` and `no_headlines` automatically.

---

## ▶️ Running the Scraper

### **Benzinga Example**

```bash
!python find_headlines_benzinga.py --browser_type chrome --type stocks
# Restart from scratch:
# !python find_headlines_benzinga.py --browser_type chrome --type stocks --restart
```

### **Nasdaq Example**

```bash
!python find_headlines_nasdaq.py --browser_type chrome --type stocks
```

### Common Arguments

| Flag | Type | Description |
|------|------|--------------|
| `--dir` | str | Base directory where CSV files are stored (default `/content/drive/MyDrive/`) |
| `--browser_type` | str | `chrome` or `firefox` |
| `--type` | str | `all`, `stocks`, or `etf` |
| `--restart` | flag | Start fresh instead of resuming previous progress |

---

## 🧩 Requirements

All packages are listed in `requirements.txt`, tested on **Google Colab** (Python 3.12):

```
pandas==2.2.2
pytz==2025.2
selenium==4.35.0
tqdm==4.67.1
webdriver-manager==4.0.2
fake-useragent==2.2.0
google-colab-selenium==1.0.15
undetected-chromedriver==3.5.5
```

Optional extras (for your extended analysis):
```
pandas_market_calendars==5.1.1
einops==0.8.1
fuzzywuzzy==0.18.0
sentence-transformers==5.1.0
yfinance==0.2.65
```

---

## 🧠 Notes & Best Practices

- Use **headless Chrome** in Colab (`--browser_type chrome`).
- Chrome binary is automatically located via:
  ```python
  options.binary_location = "/usr/bin/chromium-browser"
  ```
- To avoid rate limits, throttle your scraping (`time.sleep` is built-in).
- Respect site Terms of Service — these scripts are for **research and personal use** only.

---

## 🧾 License

MIT License © 2025 Vincent Sham  
You may use, modify, and distribute this project freely with attribution.

---

## 🌟 Acknowledgments

- [Selenium](https://www.selenium.dev/)
- [Benzinga](https://www.benzinga.com/)
- [Nasdaq](https://www.nasdaq.com/)
- [Google Colab](https://colab.research.google.com/)
