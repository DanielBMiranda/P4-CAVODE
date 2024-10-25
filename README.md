# P4-CAVODE

P4-CAVODE is a lightweight network anomaly detection system designed for identifying port scans, a common technique employed during the initial stages of cyberattacks to gather information about a target. It is able to detect irregularities caused by multiple variations of port scans, as it considers target multiplicity and is independent of the headers used. However, its focus lies in the timeframe used, namely on slow scans which consist of a main challenge due to their extended duration, especially in data planes where available memory is limited.
The developed solution manages to sustain a throughput that closely matches the theoretical capabilities of the hardware, even when using multiple services, which demonstrates its scalability. Furthermore,
despite its focus on slow port scanning, deviations caused by port scan probes do not require large periods to be identified. As such, their detection occurs practically in real-time, ensuring that actions against
imminent threats could be taken with minimal delay. These characteristics highlight the role of data plane
programmability in the realm of cybersecurity.
