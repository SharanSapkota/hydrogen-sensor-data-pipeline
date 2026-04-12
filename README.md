# Hydrogen Leak Detection System

![System Banner](https://github.com/user-attachments/assets/5cd5ee38-0ef2-4a6c-9887-70c5ba91c2a3)

## Overview

An AI-powered hydrogen leak detection system that runs on a Raspberry Pi. The system monitors multiple sensor inputs in real time, uses a trained XGBoost model to distinguish genuine leaks from false alarms, and delivers instant alerts to your phone.

---

## Repository Structure
- /app
- working.py
- readme.md

## Two Codebases — One System

**`working.py`** is the file currently running on the Raspberry Pi. It is live, tested, and functional. This is what powers the system right now.

**`/app`** is the refactored, maintainable version of the same system — modular, scalable, and built for long-term development. As the project matures, we are gradually migrating from `working.py` to `/app`.

> Think of `working.py` as the proof of concept, and `/app` as the production path.

---

## How It Works

The system reads five signals simultaneously from wireless sensors:

- Hydrogen concentration (ppm)
- Temperature
- Humidity
- Rate of change in hydrogen level
- Rolling average over time

A trained XGBoost model processes these signals and classifies each reading as a real leak or normal variance. If a leak is detected, the system identifies the affected zone and pushes a live alert.

---

## Hardware

- Raspberry Pi (edge inference)
- Wireless gas sensors (hydrogen, temperature, humidity)
- Local network for dashboard access

---

## Getting Started

### Run the current live version
```bash
python working.py
```

### Run the app version
```bash
cd app
pip install -r requirements.txt
python main.py
```

---

## Project Status

| Component | Status |
|---|---|
| Sensor data collection | ✅ Live |
| XGBoost leak classification | ✅ Live |
| Real-time dashboard | ✅ Live |
| Modular `/app` refactor | 🔄 In Progress |
| Real-world hydrogen test data | 🔜 Planned |
| Multi-zone sensor scaling | 🔜 Planned |