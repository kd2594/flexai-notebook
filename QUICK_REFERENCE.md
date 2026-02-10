# 🚀 Quick Reference Card

## Start Everything (with Docker)
```bash
./start.sh
```

## Access Services
- **Jupyter**: http://localhost:8888
  - Token: `local_demo_token_secure_123`
- **Backend API**: http://localhost:8000/docs
- **Mock FlexAI**: http://localhost:9000/docs

## Stop Everything
```bash
./stop.sh
```

## View Logs
```bash
docker compose logs -f              # All services
docker compose logs -f backend      # Just backend
docker compose logs -f jupyter      # Just Jupyter
docker compose logs -f mock-flexai  # Just mock API
```

## Restart a Service
```bash
docker compose restart backend
docker compose restart jupyter
```

## Clean Restart
```bash
./stop.sh
docker compose down -v
./start.sh
```

## Check Status
```bash
docker compose ps
```

## Access Database
```bash
docker compose exec postgres psql -U flexai_user -d flexai_notebook_db
```

## Access Redis
```bash
docker compose exec redis redis-cli
```

## Environment Variables (.env)
```env
# Switch between mock and production
MOCK_MODE=true              # Local mock mode
MOCK_MODE=false             # Production FlexAI

# Mock mode (default)
FLEXAI_API_URL=http://mock-flexai:9000

# Production mode
FLEXAI_API_URL=https://api.flexai.com
FLEXAI_API_KEY=your_real_key
FLEXAI_ORG_ID=your_real_org_id
```

## Troubleshooting

### Port already in use?
```bash
# Find what's using the port
lsof -i :8888
lsof -i :8000
lsof -i :9000

# Stop that service or change ports in docker-compose.yml
```

### Services won't start?
```bash
# Check Docker is running
docker ps

# Clean everything and rebuild
docker compose down -v
docker system prune -f
./start.sh
```

### Jupyter token not working?
Check the token in your `.env` file matches what you're entering.

## Key Files
- `.env` - Your local configuration
- `docker-compose.yml` - Service definitions
- `LOCAL_SETUP.md` - Detailed Docker setup
- `LOCAL_SETUP_NO_DOCKER.md` - Setup without Docker
- `SETUP_COMPLETE.md` - Full overview

## Mock GPU Types Available
- nvidia-t4 (16GB)
- nvidia-v100 (32GB)
- nvidia-a100-40gb (40GB)
- nvidia-a100-80gb (80GB)
- nvidia-h100 (80GB)
- nvidia-l4 (24GB)

## Demo Flow
1. Start platform: `./start.sh`
2. Open Jupyter: http://localhost:8888
3. Enter token: `local_demo_token_secure_123`
4. Open any notebook
5. Click "Select GPU" button
6. Choose a GPU (all simulated)
7. Run your code!

## Production Switch Checklist
- [ ] Get FlexAI API key
- [ ] Get FlexAI org ID
- [ ] Update `.env`: Set `MOCK_MODE=false`
- [ ] Update `.env`: Set real `FLEXAI_API_KEY`
- [ ] Update `.env`: Set real `FLEXAI_API_URL`
- [ ] Update `.env`: Set real `FLEXAI_ORG_ID`
- [ ] Restart: `./stop.sh && ./start.sh`
- [ ] Test with real FlexAI connection

---

**Need help?** See detailed guides:
- With Docker: [LOCAL_SETUP.md](LOCAL_SETUP.md)
- Without Docker: [LOCAL_SETUP_NO_DOCKER.md](LOCAL_SETUP_NO_DOCKER.md)
- Overview: [SETUP_COMPLETE.md](SETUP_COMPLETE.md)
