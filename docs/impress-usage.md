# How to install and run IMPRESS / EXACT / IMPISH flight code
Follow _[Raspberry Pi  Setup Procedure - Current](https://docs.google.com/document/d/1JNEULauzhiDdBZC1ucpm0O6bZ41J6PDBBEvh_yHYQEM)_ to set up a new Pi if needed.

## Table of contents
1. [Installation](#installation)
3. [Detector hardware setup](#detector-setup)
2. [Usage](#usage)
4. [Data Analysis](#data-analysis)


## Installation
Build and install [Nebula](https://github.com/UMN-SSRL/Nebula).

### PPS Setup
#### _Use only 3.3V level PPS signals!_

A PPS is required for nominal science mode to have very accurate timestamps.
The PPS must be buffered properly e.g. through an op amp voltage follower.

The PPS is not required for the Bridgeport boards to function properly,
    but for nominal science mode,
    the X-123 requires a 1Hz hardware strobe to step through its data collection buffers.
We are using the
["hardware-controlled sequential buffer operation" (pg 219)](https://www.amptek.com/-/media/ametekamptek/documents/resources/products/user-manuals/amptek-digital-products-programmers-guide-b3.pdf)

**For the X-123**,
    you need to plug the PPS (or equivalent 1Hz strobe) into the AUX_IN_2 port on the back of it.
A pinout for the X-123 can be found [here, pg 6](https://www.amptek.com/-/media/ametekamptek/documents/resources/products/user-manuals/dp5-user-manual-b0.pdf).

**For the Bridgeport boards**,
    you need to plug the PPS (or equivalent 1Hz strobe)
    into [GPIO pin S0](https://www.bridgeportinstruments.com/products/sipm/sipm3k/sipm3k_pinout.pdf).
The cables that MSU and UMN have made should have that connection already.

**For the Raspberry Pi**,
    the code is expecting a PPS to come in on GPIO pin 31,
    so make sure that pin is configured for input on the Pi.

## Usage
To collect IMPRESS data, run `det_start_impress_sci`.
Files will accumulate in `/SAT/LIVE/DET-SCI`,
    and will be transferred to the ground station if norm is proprely configured.

## Data Analysis -- see `python/examples`