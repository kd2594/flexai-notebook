# Development Guide

## Project Structure

```
flexai-notebook/
├── backend/                    # Backend API server
│   ├── main.py                # FastAPI application
│   ├── flexai_client.py       # FlexAI platform client
│   └── session_manager.py     # Session management
├── frontend/                   # Jupyter frontend
│   ├── extension/             # Custom Jupyter extension
│   │   ├── flexai_compute.js  # JavaScript extension
│   │   └── flexai_compute.py  # Python server extension
│   └── static/                # Static assets
│       └── custom.css         # Custom styles
├── notebooks/                  # Sample notebooks
├── docker/                     # Docker configurations
└── docker-compose.yml         # Docker Compose setup
```

## Backend API

### FlexAI Client

The `flexai_client.py` module handles communication with the FlexAI compute platform. Key methods:

- `get_available_gpus()`: Fetch available GPU types
- `provision_instance()`: Provision a new compute instance
- `get_instance_status()`: Check instance status
- `stop_instance()`: Stop a running instance
- `delete_instance()`: Delete an instance

### Session Manager

The `session_manager.py` module manages user sessions and compute instance mappings:

- `create_session()`: Create a new session
- `get_session()`: Retrieve session by ID
- `update_session()`: Update session details
- `delete_session()`: Remove a session

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/compute/available` | GET | Get available GPU types |
| `/api/compute/select` | POST | Select and provision compute |
| `/api/compute/instance/{id}` | GET | Get instance status |
| `/api/compute/instance/{id}/stop` | POST | Stop instance |
| `/api/sessions/create` | POST | Create new session |
| `/api/sessions/{id}` | GET | Get session details |
| `/api/sessions/{id}` | DELETE | Delete session |

## Frontend Extension

### JavaScript Extension

The `flexai_compute.js` extension adds:

- GPU selection button in Jupyter toolbar
- Modal dialog for GPU selection
- Communication with backend API
- Session persistence in notebook metadata

### Python Server Extension

The `flexai_compute.py` server extension:

- Bridges Jupyter and backend API
- Handles proxy requests from frontend
- Manages environment configuration

## Adding New Features

### Adding a New GPU Type

1. Update FlexAI API to return new GPU type
2. The frontend will automatically display it in the selection dialog

### Adding Authentication

1. Update `backend/main.py` to add authentication middleware
2. Implement JWT token generation and validation
3. Update frontend to send authentication headers

### Customizing the UI

1. Edit `frontend/extension/flexai_compute.js` for functionality
2. Edit `frontend/static/custom.css` for styling
3. Rebuild Docker containers: `docker-compose up --build`

## Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Manual Testing

1. Start the platform:
   ```bash
   ./start.sh
   ```

2. Open Jupyter: http://localhost:8888
3. Click the FlexAI Compute button
4. Select a GPU and verify provisioning

### Testing Backend API

```bash
# Health check
curl http://localhost:8000/health

# Get available GPUs
curl http://localhost:8000/api/compute/available

# Create session
curl -X POST http://localhost:8000/api/sessions/create
```

## Deployment

### Production Deployment

1. Update `.env` with production credentials
2. Use production-grade database (PostgreSQL)
3. Enable HTTPS
4. Set up load balancing
5. Configure monitoring and logging

### Security Considerations

- Never commit `.env` file
- Use strong SECRET_KEY
- Implement rate limiting
- Add authentication and authorization
- Use HTTPS in production
- Regularly update dependencies

## Troubleshooting

### Jupyter can't connect to backend

- Verify backend is running: `docker ps`
- Check backend logs: `docker logs flexai-backend`
- Verify BACKEND_API_URL is correct

### GPU not available in notebook

- Ensure GPU was provisioned successfully
- Check instance status via API
- Verify FlexAI platform credentials

### Extension not loading

- Check Jupyter logs: `docker logs flexai-jupyter`
- Verify extension is installed: `jupyter nbextension list`
- Clear browser cache and reload

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
