import streamlit as st
from iot_device_simulator import generate_iot_devices

devices = generate_iot_devices()

st.title("IoT Device Simulator Output")

for device in devices:
    with st.expander(f"{device['id']} - {device['type']}"):
        st.write(f"**CPU:** {device['cpu']} MIPS")
        st.write(f"**RAM:** {device['ram']} GB")
        st.write(f"**Bandwidth:** {device['bandwidth']} Mbps")
        st.write(f"**Throughput:** {device['throughput']} MB/s")
        st.write(f"**Availability:** {device['availability'] * 100:.1f}%")
        st.write(f"**Priority Score:** {device['priority_score']}")
        st.write(f"**Role:** {device['role']}")
        st.write(f"**Status:** {device['status']}")
        st.subheader("Task Queue")
        for task in device["task_queue"]:
            st.markdown(f"- `{task['task']}` (Complexity: `{task['complexity']}`)")