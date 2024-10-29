# P4-CAVODE


P4-CAVODE is a lightweight anomaly detection system designed for software-defined networks (SDNs), implemented on the data plane to address the unique demands of network security at high throughput levels. Its primary function is to detect anomalies caused by port scan activity, a commonly employed technique during the initial stages of cyberattacks to gather information about a target. The system's anomaly detection extends to multiple types of port scans by considering target multiplicity and operating independently of specific protocol headers. One of the system’s key strengths is its focus on detecting slow port scans. These types of scans are typically challenging to detect, as they can evade traditional detection due to their prolonged nature, especially within data planes where memory resources are constrained.

The developed solution achieves a throughput close to line rate while maintaining a high detection ratio and scalability. Furthermore, despite its focus on slow port scanning, deviations caused by port scan probes do not require long periods to be identified. As such, detection occurs practically in real-time, ensuring that actions against imminent threats can be taken with minimal delay.

# Implementations

P4-CAVODE offers two distinct implementations:

- **Software-Based Prototype**: A proof-of-concept implementation designed for the BMv2 software switch, allowing for easier testing and development.
- **Hardware Deployment**: An optimized version running on the Netronome Agilio SmartNIC, providing accelerated, hardware-based processing.
