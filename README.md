# P4-CAVODE

P4-CAVODE is a lightweight anomaly detection system designed for software-defined networks (SDNs), implemented on the data plane to address the unique demands of network security at high throughput levels. Its primary function is to detect anomalies caused by port scan activity, a commonly employed technique during the initial stages of cyberattacks to gather information about a target. The system's anomaly detection extends to multiple types of port scans by considering target multiplicity and operating independently of specific protocol headers. One of the system’s key strengths is its focus on detecting slow port scans. These types of scans are typically challenging to detect, as they can evade traditional detection due to their prolonged nature, especially within data planes where memory resources are constrained.

The developed solution achieves a throughput close to the line rate of the Netronome Agilio SmartNIC, maintaining a high detection ratio and scalability. Furthermore, despite its focus on slow port scanning, deviations caused by port scan probes do not require long periods to be identified. As such, detection occurs practically in real-time, ensuring that actions against imminent threats can be taken with minimal delay.

# Implementations

P4-CAVODE offers two distinct implementations, both located in the [`implementations`](implementations) directory:

- **Software-Based Prototype**: A proof-of-concept implementation designed for the BMv2 software switch, enabling straightforward testing and development. For details, see [`implementations/bmv2`](implementations/bmv2).
- **Hardware Deployment**: An optimized version running on the Netronome Agilio SmartNIC, providing accelerated, hardware-based processing. For details, see [`implementations/netronome`](implementations/netronome).

# Installation and usage

## BMv2

For the software version of the P4 program, BMv2, ensure all necessary dependencies are installed by following the installation guide available at [`P4 Guide - Installation Troubleshooting`](https://github.com/jafingerhut/p4-guide/blob/master/bin/README-install-troubleshooting.md).

Using the software is straightforward:

- Since Mininet requires root privileges, use ```sudo make``` to compile the program, start the simulated environment, and load the P4 program.
- To stop the environment and clean associated directories, use ```sudo make clean```.

### Attribution

This implementation makes use of several libraries and files licensed under the [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0), sourced from the repository [p4lang/tutorials](https://github.com/p4lang/tutorials).

The reused files are located in:
- [`implementations/bmv2/utils`](implementations/bmv2/utils)
- [`implementations/bmv2/topology`](implementations/bmv2/topology)

A list of modifications performed on the original code can be found at [`implementations/bmv2/README.md`](implementations/bmv2/README.md).

## Netronome

For the hardware version, using the ```Netronome Agilio Agilio CX 2x10GbE SmartNIC```, you will need software provided by the hardware vendor, such as the SDK Hosted Toolchain.

Additionally, you can refer to the [`Netronome P4 Template Repository`](https://github.com/RuiCunhaM/template-netronome-p4), which provides a helpful starting point for working with P4 programs on Netronome SmartNICs.