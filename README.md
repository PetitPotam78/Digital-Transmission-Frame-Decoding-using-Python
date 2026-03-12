# Digital-Transmission-Frame-Decoding-using-Python

# Digital Transmission & Layer 2 Protocol Emulation

This repository hosts a comprehensive suite of **Python-based simulations** modeling a full digital communication chain. The project bridges the gap between **Physical Layer (L1)** signal processing and **Data Link Layer (L2)** frame encapsulation, using industry-standard tools like **Scapy**.

## Project Overview

The core objective is to simulate the end-to-end transmission of network data through a noisy channel. Unlike generic simulations, this project validates the transmission by encoding, modulating, and subsequently decoding real **ICMP/Ethernet frames**, ensuring data integrity at the bit level.

### Key Technical Competencies:
* **Modulation Schemes:** Implementation of PAM-4, QPSK, and 16-QAM.
* **Signal Processing:** Pulse shaping, upsampling, frequency translation (carrier modulation), and noisy channel modeling (AWGN).
* **Network Protocol Analysis:** Leveraging **Scapy** for Layer 2 frame generation, encapsulation, and field-by-field verification post-decoding.

---

## System Architecture

The simulation is built using a modular Object-Oriented Programming (OOP) approach:

1. **Source:** Generates pseudo-random bitstreams or captures real network frames (e.g., ICMP Echo Requests).
2. **Modem:** Handles bit-to-symbol mapping, constellation management, and root-raised-cosine filtering.
3. **Channel:** Models an AWGN (Additive White Gaussian Noise) environment to test system robustness.
4. **Receiver:** Performs frequency down-conversion, downsampling, symbol detection, and bit de-mapping.
5. **Analytics:** Evaluates performance via Bit Error Rate (BER) calculation and Power Spectral Density (PSD) analysis.

---

## Repository Structure

* **`Module.py`**: Core signal processing engine containing modular classes for Modulation, Measurement, and Channel simulation.
* **`PAM Transmission.ipynb`**: Implementation of Pulse Amplitude Modulation and Baseband Pulse Shaping (Nyquist criterion).
* **`4PSK Transmission.ipynb`**: Transition to passband transmission using Quadrature Phase Shift Keying (QPSK) with complex symbol mapping.
* **`16QAM Transmission.ipynb`**: Advanced passband transmission utilizing 16-QAM constellations to maximize spectral efficiency in bandwidth-limited channels.

---

## Performance Analysis & Visualisation

The project implements several diagnostic tools to monitor signal quality:
* **Constellation Diagrams:** Real-time observation of symbol clusters and noise-induced deviations.
* **Power Spectral Density (PSD):** Evaluating the frequency footprint and bandwidth efficiency of different modulations.
* **Scapy Frame Validation:** Final verification using the `.show()` method to ensure that the decoded Ethernet/IP/ICMP headers match the source data.

---

## Technical Stack

* **Language:** Python 3.10+
* **Networking:** [Scapy](https://scapy.net/) (Packet manipulation)
* **Scientific Computing:** NumPy, SciPy
* **Data Visualisation:** Matplotlib
