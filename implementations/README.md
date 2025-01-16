## Definitions

This section contains basic definitions for Ethernet type values and protocol matching values, which are used to define transitions in the parser. It also includes definitions for some specific packet fields.

For example, the IPv4 matching type can be defined as:
```c
#define TYPE_IPV4 0x0800
```
Additionally, an IPv4 address type can be declared as:
```c
typedef bit<32> ip4Addr_t;
```

## Headers

This block contains the definitions of protocol headers and metadata used throughout the program.

The primary headers - Ethernet, IPv4, MAC, and ports - are matched upon packet arrival. The port information, applicable to both TCP and UDP, is extracted by retrieving the first 32 bits of the packet header, which represent the ports.

The remaining headers pertain to metadata utilized during data processing and manipulation, as well as alarms generated in the event of anomalies. These alarms provide detailed information, including the current distinct count, the difference between the current and previous counts, the previous variation, the current variation, and the alarm's timestamp.

## Parsers

It includes both the Parser and Deparser blocks.

The Parser is responsible for extracting headers from each packet and mapping them using a state machine model.

The process begins with the Ethernet headers, transitioning to the IPv4 state if the EtherType matches. In the IPv4 state, the Parser checks the protocol field, transitioning to the next state if it matches either TCP or UDP. In this state, it extracts the port information and initializes all metadata required for subsequent processing to 0.

The Deparser rebuilds the packet by combining all the necessary headers so it can be sent out.

## Checksums

Checksum mechanisms were not implemented.

## Actions

Provides a function that maps a key (destination IP and destination port) to its position in the table, without inserting it, by returning the position where it would be inserted.

Actions defined in the main file could be relocated here instead.

# Hardware specifics

## Registers

In the Netronome SmartNIC, registers are not synchronized with the in-hardware flow cache. This lack of synchronization, combined with cached lookups, can lead to unpredictable behavior when accessing registers that influence control flow. To mitigate this issue, the cache-flow option can be disabled by using the directive:

```#pragma netro no_lookup_caching <action name>;```

However, in the latest version of P4 (P4_16), the Netronome compiler ignores this directive entirely when generating intermediate code. As a result, manual modifications to the intermediate code are required to achieve the desired behavior.
For more information check [`Netronome P4 Template Repository`](https://github.com/RuiCunhaM/template-netronome-p4) and the official product documentation.

## Locking mechanisms

Additionally, the Netronome SmartNIC features multiple threads, enabling it to process multiple packets simultaneously. However, this requires the implementation of critical sections to prevent unintended changes to the program flow.

The code in [`src/pif_plugin.c`](src/pif_plugin.c) implements spin-locks to define the critical sections for each individual element register, as well as separate spin-locks for each position within multi-element structures.

The implementation of the spin-locks was inspired by [`FastReact`](https://github.com/andrkass/FastReact).

## Ingress Processing

The block starts by declaring the registers, which are the structures used through the solution. Those are the cyclic buffer, frequency table, first index/oldest element, distinct counter, old distinct counter and the variation.

For instance:

```c
register<bit<32>>(550) cfb;
```

The cyclic buffer can store 550 elements, with 32 bits allocated to each element.  
As for the solution process itself, it can be divided into four main steps:

---

### 1. Key Generation  
The process begins by calling the function that generates the corresponding position of the key, as described in [`Actions`](#actions).

---

### 2. Buffer Process  
The following steps are performed within the buffer process:

1. Acquire the position/index within the buffer of the element to be replaced.  
2. Check if the element needs to be reset.  
3. Increment the position/index.  
4. Acquire the distinct count to be used in case of a reset.
5. Acquire the fingerprint to be removed.  
6. Replace the fingerprint to be removed with the new one.

> **Note**:
> In the hardware version, the cyclic buffer locks use ```meta.myParams.index``` as the lock index.
> ```c
> meta.myParams.index = meta.index + 11000;
> ```
> The value ```11000``` is added to adjust the lock identifiers for each structure, preventing potential collisions with locks from other structures.

---

### 3. Update Frequency Table and Distinct Counter  
1. Acquire the frequency of the fingerprint to be removed and decrement its frequency.  
2. Acquire the frequency of the new fingerprint and increment it.  
3. If the frequency of the removed fingerprint decreases from 1 to 0, it is no longer in the cycle. In this case, the distinct counter is incremented.  

---

### 4. Calculate Variation and Decide on Notification  
1. Acquire the value of the distinct counter from the previous cycle.  
2. Acquire the previous variation.  
3. Use the previous counter, the current counter, and the previous variation to determine the new variation.  
    > **Note**: This calculation requires floating-point operations, which P4 does not natively support. However, approximate results can be achieved using bitwise shifts, as described in [this guide](https://github.com/jafingerhut/p4-guide/blob/master/docs/floating-point-operations.md).

4. Update the metadata information for use in the event of an alarm.
During this step, timestamps are also recorded. The timestamps in the hardware version are 64 bits in size and consist of:
   - The upper 32 bits holding a 32-bit value representing seconds;
   - The lower 32 bits holding a 32-bit value representing nanoseconds.

## Egress Processing

Includes an action that sends a notification according to its definition, utilizing a digest mechanism to transfer messages from the data plane to the control plane.

The notification is triggered only when the flag meta.flag is set to 1. This matching process is configured as specified in the file [`configs/config.json`](configs/config.json) as follows:

```json
"egress::notification_table": {
    "rules": [
        {
            "action": {
                "type": "egress::send_notification"
            }, 
            "name": "notify", 
            "match": {
                "scalars.metadata_t@alarm": {
                    "value": "1"
```

This ensures that notifications are sent only when the specified condition is met, streamlining communication between the data plane and the control plane.