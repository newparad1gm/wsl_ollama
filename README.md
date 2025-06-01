# Running Ollama in Windows 11 with WSL2 on an NVIDIA GPU

## BIOS/UEFI VM Features enabled
- SVM for AMD
- Intel Virtualization Technology or VT-d for Intel
  
## Windows Features
- Search for Turn Windows Features on or off in Windows Search
- Enable Virtual Machine Platform and Windows Subsystem for Linux

## NVIDIA Drivers
- Make sure latest NVIDIA Drivers are installed, currently using Game-Ready drivers
  - https://www.nvidia.com/en-us/geforce/drivers/
- Can install with Display Driver Uninstaller
  - https://www.wagnardsoft.com/display-driver-uninstaller-DDU-
- Make sure other branded GPUs are disabled with Windows Device Manager or disabled in UEFI/BIOS, and drivers are not installed for them
- In my situation the CPU was the 9950X3D with the Radeon IGP, disabled in Windows Device Manager

## Powershell and WSL2
- Start Powershell as admin
- Install Ubuntu on WSL2
  - `wsl --install -d ubuntu`
- Verify it is installed with WSL2
  - `wsl -l -v`

## Ubuntu NVIDIA Setup
- Search for Ubuntu app, should be installed in Start Menu
- Opens up terminal for Ubuntu
- `sudo apt-get update && sudo apt-get upgrade`
- Verify NVIDIA drivers are installed and Ubuntu recognizes the GPU
  - `nvidia-smi`
- Install NVIDIA CUDA Toolkit
  - Follow instructions at https://developer.nvidia.com/cuda-downloads
  - I ended up with https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=WSL-Ubuntu&target_version=2.0&target_type=deb_local
  - Follow installation instructions
  - Add to bashrc
    - ```
      export CUDA_HOME=/usr/local/cuda
      export PATH=$CUDA_HOME/bin:$PATH
      export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
      source ~/.bashrc
      ```
  - `nvcc --version` to verify

## Ollama Setup and Run
- Ollama setup
  - `curl https://ollama.ai/install.sh | sh`
- Serve Ollama for network access
  - `OLLAMA_HOST=0.0.0.0:11434 ollama serve`
- May need to turn off Ollama first
  - `sudo lsof -i :11434`
  - `kill -9 <PID>`
  - If Ollama comes back up by itself, means systemd is keeping it up
- Ollama run model
  - Can browse model names here: https://ollama.com/library
  - `ollama run <model name>` e.g. `deepseek-r1:32b`
 
## Network Communication with Ollama
- `ipconfig` in PowerShell or Terminal in Windows
  - Look for IPv4 Address of something like `192.168.x.x` - IP Address of host machine in network
- On other machine, run `curl http://192.168.x.x:11434/api/tags`
  - Should successfully give models currently deployed in Ollama

## Open WebUI
- Front end like ChatGPT to use the LLM: https://github.com/open-webui/open-webui
- Docker installed on other machine that can contact Ollama server
- Pull latest Open WebUI image
  - `docker pull ghcr.io/open-webui/open-webui:main`
- Current Docker command to get Open WebUI container running
  - ```
    docker run -d -p 3000:8080 -e OLLAMA_BASE_URL=http://192.168.x.x:11434 -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
    ```
- `localhost:3000` or ip of this machine at port 3000 for other machines on the network to access

## Turn off Ollama
- `ollama serve` - `CTRL+C` to exit
- `ollama run` - `/bye` the model or `CTRL+C`
- Ollama could be running as a `systemd` service that restarts it if it is closed
  - `sudo systemctl stop ollama`
  - `sudo systemctl disable ollama`
- Exiting Ubuntu terminal should stop the VM if no processes are running
- `wsl -l -v` in Powershell to make sure Ubuntu is in Stopped state


## MCP Testing
- `pip install mcp` with Python version specified
- `python mcp_server.py` to start MCP Server
- `python mcp_client.py` to run MCP client to test the server

## Continue.dev VSCode Integration
- Install Continue.dev plugin for VSCode
- Open `config.yaml` in `~/.continue` (or wherever this yaml file is, can open with `Ctrl+Shift+P` -> `Continue: Open Settings`)
- In models section of yml
  - ```
    models:
      - name: Qwen3 32B
        provider: ollama
        model: qwen3:32b (name of model deployed)
        roles:
          - chat
          - edit
          - apply
        apiBase: http://192.168.x.x:11434
    ```
