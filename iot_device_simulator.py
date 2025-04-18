import random
from typing import List, Dict

DEVICE_TYPES = [
    "Smart Light", "Smart Fan", "Smart TV", "Smart AC",
    "Smart Door Lock", "Smart Fridge", "Smart Speaker", "Security Camera"
]

TASK_POOL = {
    "Smart Light": ["toggle", "dim", "status-update"],
    "Smart Fan": ["rotate", "adjust-speed"],
    "Smart TV": ["stream-frame", "change-channel", "volume-adjust"],
    "Smart AC": ["temp-update", "cooling-mode", "fan-speed"],
    "Smart Door Lock": ["lock", "unlock", "battery-status"],
    "Smart Fridge": ["temp-check", "defrost", "inventory-scan"],
    "Smart Speaker": ["play-audio", "set-volume", "voice-command"],
    "Security Camera": ["record", "motion-detect", "stream-feed"]
}

# Task complexity ranges per device type
TASK_COMPLEXITY_RANGES = {
    "Smart Light": (200, 800),
    "Smart Fan": (400, 1200),
    "Smart TV": (1500, 3000),
    "Smart AC": (1200, 2500),
    "Smart Door Lock": (300, 900),
    "Smart Fridge": (800, 1600),
    "Smart Speaker": (800, 1800),
    "Security Camera": (1500, 3000)
}

def generate_iot_devices(n: int = 8) -> List[Dict]:
    devices = []
    for i in range(n):
        device_type = DEVICE_TYPES[i % len(DEVICE_TYPES)]
        
        task_queue = []
        # Select 2 tasks randomly for each device
        for task in random.sample(TASK_POOL[device_type], k=2):
            low, high = TASK_COMPLEXITY_RANGES[device_type]  # Get the complexity range for the device type
            complexity = random.randint(low, high)  # Assign complexity based on the device type
            task_queue.append({
                "task": task,
                "complexity": complexity
            })

        device = {
            "id": f"Device-{i+1}",
            "type": device_type,
            "cpu": random.randint(500, 3000),               # MIPS
            "ram": round(random.uniform(0.5, 4), 2),         # GB
            "bandwidth": round(random.uniform(1, 5), 2),     # Mbps
            "throughput": round(random.uniform(0.1, 1.0), 2),# MB/s
            "task_queue": task_queue,
            "availability": round(random.uniform(0.85, 0.99), 2),  # uptime %
            "role": "worker",  # initially all are workers
            "priority_score": random.randint(50, 100),  # optional metric
            "status": "active"
        }
        devices.append(device)
    return devices

if __name__ == "__main__":
    devices = generate_iot_devices()
    for d in devices:
        print(d)