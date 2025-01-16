# Results

## Alarms

The tests are meant to evaluate how the system reacts to both fast and slow scan scenarios, using the information provided by the alarm system.
In these tests, a single host continuously sends requests to four different services on another host, resulting in a distinct key for each service (combination of destination IP and destination port). For the first 2 hours, the host performs only normal activity. After this period, it begins performing port scan activity in addition to its normal activity.

For the slow scan, delays of 10, 20, and 30 seconds are introduced between packets. In contrast, the fast scan scenario introduces no delay between probes. The port scan is performed using ```nmap``` on 996 ports, with only 1 being open. Additionally, for each scenario, different sizes of the cyclic buffer are tested: 400, 450, 500, 550, and 10000. The frequency table size remains fixed at 1000.

The table below summarizes the delays used and the corresponding test durations for each scenario:

| **Delay used (s)** | **Test duration** |
|---------------------|-------------------|
| No delay used       | 8000             |
| 10                  | 18000            |
| 20                  | 28000            |
| 30                  | 38000            |

In addition to these scenarios, a similar test was conducted in which one of the four services operates intermittently, running only for 10 seconds every 5 minutes. This test aims to simulate more realistic scenarios where not all services are accessed with the same frequency.

## Throughput

Finally, throughput was evaluated for both software and hardware implementations.
These tests were conducted using ```iperf3``` over a 1-hour period. They include scenarios where a single service performs normal activity, as well as cases where four services operate concurrently. The test files contain the throughput data for each service, recorded every second.