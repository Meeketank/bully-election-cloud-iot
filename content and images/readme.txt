# Bully Election Algorithm for Cloud Computing and IoT Devices

## 📌 Overview

This project focuses on the implementation and analysis of the **Bully Election Algorithm** specifically tailored for **Cloud Computing** and **IoT (Internet of Things)** environments. The algorithm is essential for **leader election** in distributed systems, ensuring a new coordinator is chosen automatically in case of node failures.

The objective is to demonstrate how the classical Bully algorithm can be adapted and optimized for modern use cases in fault-tolerant, latency-sensitive, and heterogeneous network environments.

---

## ⚙️ Features

- ✅ Simulates Bully Algorithm in a distributed network
- 🌐 Supports Cloud-based and IoT device node structures
- 🔄 Handles dynamic node failures and recoveries
- ⏱️ Measures election time and performance metrics
- 📊 Logs leader election steps and decisions
- 📡 Lightweight protocol for resource-constrained IoT nodes

---

## 📚 Use Cases

- Distributed cloud services requiring coordination
- Edge computing clusters in smart cities
- Sensor networks in industrial IoT systems
- Fog computing architecture coordination
- Emergency failover systems in smart homes

---

## 🏗️ Architecture

- Nodes (Processes) represent cloud/IoT instances
- Each node is assigned a unique ID and can communicate via simulated RPC or sockets
- In the event of leader failure, an election is triggered using the Bully protocol
- The node with the highest ID becomes the new leader

---

## 🧠 Algorithm: Bully Election

1. A node detects the coordinator is down
2. It sends election messages to all higher-ID nodes
3. If no response, it becomes the leader
4. If any higher node responds, that node takes over the election
5. Leader broadcasts its victory to all others

---

## 🚀 Technologies Used

- Python 3 / Java (choose one based on your implementation)
- Socket programming / Threading
- Matplotlib / Seaborn (for visualization)
- Docker (optional for simulating multiple nodes)
- MQTT / CoAP (optional for IoT simulation)

---

## 🧪 How to Run

```bash
# Clone the repository
git clone https://github.com/your-username/bully-election-cloud-iot.git
cd bully-election-cloud-iot

# Run the simulation
python main.py
