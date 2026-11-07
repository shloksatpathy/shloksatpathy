# Hi, I'm Shlok

I work on amateur rocketry and student CanSat projects. I write flight software and firmware for CanSat payloads (attitude control, parafoil recovery and navigation, telemetry and failsafes) and ground station software for model rocket and CanSat launches.

My interest is in real launch vehicles and spacecraft, and working on them is where I'm headed. These projects are how I'm building toward it.

![satellites orbiting Earth](assets/orbits.svg)

## Tech stack

### 🛰️ Flight software and embedded

![C++](https://img.shields.io/badge/C++-0B1D3A?style=for-the-badge&logo=cplusplus&logoColor=659AD2)
![Arduino](https://img.shields.io/badge/Arduino-0B1D3A?style=for-the-badge&logo=arduino&logoColor=00C2CB)
![ESP32-S3](https://img.shields.io/badge/ESP32--S3-0B1D3A?style=for-the-badge&logo=espressif&logoColor=E7352C)
![LoRa](https://img.shields.io/badge/LoRa-0B1D3A?style=for-the-badge)
![I2C](https://img.shields.io/badge/I2C-0B1D3A?style=for-the-badge)

Flight computer firmware on the ESP32-S3: PID attitude control with control-moment-gyro actuation, IMU and barometer drivers written directly over I2C, sensor fusion, a recovery state machine with parafoil guidance to a GNSS target, and failsafes for every subsystem. Telemetry goes to the ground over LoRa.

### 📡 Ground segment

![Python](https://img.shields.io/badge/Python-0B1D3A?style=for-the-badge&logo=python&logoColor=FFD43B)
![PyQt5](https://img.shields.io/badge/PyQt5-0B1D3A?style=for-the-badge&logo=qt&logoColor=41CD52)
![pyqtgraph](https://img.shields.io/badge/pyqtgraph-0B1D3A?style=for-the-badge)
![NumPy](https://img.shields.io/badge/NumPy-0B1D3A?style=for-the-badge&logo=numpy&logoColor=4DABCF)
![pandas](https://img.shields.io/badge/pandas-0B1D3A?style=for-the-badge&logo=pandas&logoColor=FFCA00)
![Folium](https://img.shields.io/badge/Folium-0B1D3A?style=for-the-badge&logo=leaflet&logoColor=9BE15D)
![OpenGL](https://img.shields.io/badge/OpenGL-0B1D3A?style=for-the-badge&logo=opengl&logoColor=8FB7D4)
![pyserial](https://img.shields.io/badge/pyserial-0B1D3A?style=for-the-badge)

A real-time ground station for model rocket and CanSat launches: serial packet parsing, live telemetry plots, a GNSS ground-track map, derived telemetry, adaptive CSV logging, and packaged Linux and Windows builds.

### 🧠 ML inference

![PyTorch](https://img.shields.io/badge/PyTorch-0B1D3A?style=for-the-badge&logo=pytorch&logoColor=EE4C2C)
![ONNX Runtime](https://img.shields.io/badge/ONNX_Runtime-0B1D3A?style=for-the-badge&logo=onnx&logoColor=white)
![TensorRT](https://img.shields.io/badge/TensorRT-0B1D3A?style=for-the-badge&logo=nvidia&logoColor=76B900)
![YOLOv8](https://img.shields.io/badge/YOLOv8-0B1D3A?style=for-the-badge&logo=ultralytics&logoColor=white)
![Colab](https://img.shields.io/badge/Colab-0B1D3A?style=for-the-badge&logo=googlecolab&logoColor=F9AB00)

Taking vision models from a PyTorch baseline through ONNX Runtime to TensorRT FP16 and INT8, and measuring throughput, latency percentiles, accuracy and VRAM at each step.

### 🛡️ Web and LLM security

![Flask](https://img.shields.io/badge/Flask-0B1D3A?style=for-the-badge&logo=flask&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-0B1D3A?style=for-the-badge&logo=gunicorn&logoColor=6CC24A)
![Render](https://img.shields.io/badge/Render-0B1D3A?style=for-the-badge&logo=render&logoColor=white)

A REST API and dashboard that scan LLM prompts for injection attacks, decoding obfuscated payloads before matching, and score their risk.

### 🧰 Tools

![Linux](https://img.shields.io/badge/Linux-0B1D3A?style=for-the-badge&logo=linux&logoColor=FCC624)
![Bash](https://img.shields.io/badge/Bash-0B1D3A?style=for-the-badge&logo=gnubash&logoColor=4EAA25)
![Git](https://img.shields.io/badge/Git-0B1D3A?style=for-the-badge&logo=git&logoColor=F05032)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-0B1D3A?style=for-the-badge&logo=githubactions&logoColor=2088FF)

![rocket launch close-up with engine plume](assets/rocket.svg)

## Contribution graph

![satellite contribution graph](https://raw.githubusercontent.com/shloksatpathy/shloksatpathy/output/satellite-graph.svg)
