# Modifications to the Original Code

This document lists the changes made to the original code sourced from the [p4lang/tutorials repository](https://github.com/p4lang/tutorials), which is licensed under the [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0).

## Summary of Changes

### 1. [`Topology`](topology)
- Updated the topology configuration (JSON files) to suit the project’s needs, with customizations to the node and link setups.

### 2. [`Makefile`](Makefile)
- Simplified the Makefile to focus on a single type of code being tested, as opposed to the original version, which supported multiple exercises.

### 3. [`utils/run_exercise`](utils/run_exercise)
- Added code segments that enable hosts to automatically execute specific scripts upon startup, streamlining testing scenarios.

### 4. [`topology/controller/controller.py`](topology/controller/controller.py)
- Modified the controller logic to process digests, allowing notifications to be received and their associated data to be extracted and handled.
