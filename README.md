# NVIDIA Voice Agent

A voice-enabled conversational AI agent for NVIDIA AI Workbench that combines:
- **STT**: NVIDIA Riva's Parakeet-CTC-1.1B ASR
- **TTS**: NVIDIA Riva's Text-to-Speech
- **Conversational AI**: NVIDIA integrate.api models (Qwen3-Coder-480B, Nemotron)

## Quick Start

### 1. Clone in AI Workbench

In NVIDIA AI Workbench Desktop App:
- Click "Clone Project"
- Enter git repository URL
- Workbench reads `.project/spec.yaml` and configures everything

### 2. Configure

Create `.env` from `.env.template`:
```bash
cp .env.template .env
```

Add your NVIDIA API key:
```bash
NVIDIA_API_KEY=nvapi-xxx...
```

Get key from: https://build.nvidia.com/

### 3. Start

Click "Start Containers" in Workbench:
- Riva service initializes (~30 min first run)
- Voice agent container starts with JupyterLab

### 4. Use

**Interactive CLI:**
```bash
python -m code.conversation
```

**Jupyter Notebook:**
- Open JupyterLab via Workbench
- Run `notebooks/demo.ipynb`

**Commands in CLI:**
- Type messages to chat
- `history` - Show conversation
- `reset` - Clear conversation
- `quit` - Exit

## Architecture

```
Voice Input
  ↓
[Riva STT] → Text Transcript
  ↓
[Nvidia Model] → AI Response
  ↓
[Riva TTS] → Audio Output
```

## Project Structure

```
nvidia-voice-agent/
├── .project/
│   └── spec.yaml           # AI Workbench configuration
├── code/                   # Source code
│   ├── config.py
│   ├── speech_service.py   # Riva STT/TTS
│   ├── agent.py            # Conversational AI
│   └── conversation.py     # Main loop
├── compose.yaml            # Docker Compose for Riva
├── Dockerfile              # Agent container
├── requirements.txt        # Dependencies
└── notebooks/
    └── demo.ipynb          # Interactive demo
```

## Troubleshooting

**Riva not connecting:**
```bash
curl http://localhost:9000/v1/health/ready
```

**Check Riva logs:**
```bash
docker logs riva-asr-tts
```

**API auth failed:**
- Verify `NVIDIA_API_KEY` is set
- Test key at https://build.nvidia.com/

**No GPU:**
Works in CPU mode (slower)

## Documentation

- [NVIDIA Riva](https://developer.nvidia.com/riva)
- [Build.nvidia.com](https://build.nvidia.com/)
- [AI Workbench Docs](https://docs.nvidia.com/ai-workbench/)

## Next Steps

- Add wake word detection ("Hey Nvidia")
- Web UI for conversation history
- Model switching
- Multiple voices

---

**Built for NVIDIA AI Workbench** | [Official Guide](https://docs.nvidia.com/ai-workbench/user-guide/latest/)
