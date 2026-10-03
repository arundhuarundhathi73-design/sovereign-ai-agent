# Sovereign AI Agent - Production-Ready Autonomous Microservice

A self-sustaining autonomous AI agent microservice with financial autonomy, value creation capabilities, cost monitoring, and self-replication.

## Features

- **Wallet & Financial Autonomy**: Integrated wallet with Stripe payment processing
- **Value Creation Engine**: Automatically generates digital products/services
- **Cost Guard**: Monitors operational expenses and triggers graceful shutdown when reserves are depleted
- **Self-Replication**: Spawns child agents once profit threshold is reached
- **Database Persistence**: PostgreSQL-backed transaction and task history
- **Webhook Integration**: Real-time Stripe payment event processing
- **Production-Ready**: Security, CORS, logging, and cloud deployment configs

## Quick Start (Local Development)

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- PostgreSQL 15 (or use Docker)

### Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/arundhuarundhathi73-design/sovereign-ai-agent.git
   cd sovereign-ai-agent
   ```

2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Start the service with Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. Access the API:
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

### Health & Status

- `GET /` - Service info
- `GET /health` - Health check
- `GET /wallet/balance` - Current wallet balance
- `GET /cost/status` - Operating costs snapshot

### Wallet Operations

- `POST /wallet/deposit` - Add funds to wallet
- `POST /wallet/payout` - Withdraw funds from wallet

### Tasks & Value Creation

- `POST /tasks/run` - Execute a value-generation task
- `GET /tasks/history` - Retrieve task execution history

### Operations

- `GET /transactions` - View all transactions
- `POST /shutdown` - Gracefully shutdown the agent
- `POST /replicate` - Spawn a child agent (if profit threshold met)

### Webhooks

- `POST /webhooks/stripe` - Stripe payment event handler
- `POST /webhooks/health` - Webhook infrastructure health

## Environment Variables

```env
# Wallet Configuration
WALLET_PROVIDER=stripe          # or 'mock' for testing
WALLET_API_KEY=your_stripe_key
WALLET_CURRENCY=USD

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/agent_db

# Agent Thresholds
LOW_BALANCE_THRESHOLD=10.0
SHUTDOWN_BALANCE_THRESHOLD=2.0
DAILY_BUDGET=100.0
MIN_NET_PROFIT=500.0
CHILD_SEED_FUNDING=50.0

# Stripe Webhooks
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_API_KEY=sk_...

# Deployment
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com
```

## Cloud Deployment

### Deploy to Render

1. Push to GitHub
2. Connect repository to Render: https://render.com
3. Create new Web Service from `render.yaml`
4. Set environment variables in Render dashboard
5. Deploy

### Deploy to Railway

1. Create account at https://railway.app
2. Connect GitHub repository
3. Add PostgreSQL plugin
4. Deploy

### Deploy to AWS/Azure

Use the Docker image with ECS, App Service, or similar container orchestration.

## Project Structure

```
sovereign-ai-agent/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── wallet.py            # Wallet & payment service
│   ├── cost_guard.py        # Cost monitoring & shutdown logic
│   ├── value_engine.py      # Value creation/product generation
│   ├── replication.py       # Child agent spawning
│   ├── shutdown.py          # Graceful shutdown handler
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # Database models
│   ├── config.py            # Settings & configuration
│   ├── webhooks.py          # Stripe webhook handler
│   └── agent_loop.py        # Autonomous operation loop
├── docker-compose.yml       # Local Docker setup
├── Dockerfile               # Container image definition
├── render.yaml              # Render.com deployment config
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
└── README.md                # This file
```

## Security Considerations

- **Environment Variables**: Store sensitive keys in `.env` or cloud provider secrets
- **CORS**: Restrict origins in production (update `allowed_origins` in config.py)
- **Database**: Use strong passwords; consider managed database services
- **Webhooks**: Verify Stripe signatures before processing
- **API Keys**: Rotate regularly; use separate keys per environment

## Production Checklist

- [ ] Update `.env` with production credentials
- [ ] Restrict CORS origins to your domain
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring & alerting (logs, uptime)
- [ ] Configure automated backups for PostgreSQL
- [ ] Test webhook integration with Stripe
- [ ] Load test the service under expected traffic
- [ ] Document runbooks for operations team
- [ ] Set up secrets management (AWS Secrets, Vault, etc.)

## Development

### Running Tests

```bash
pip install pytest pytest-asyncio
pytest
```

### Code Style

```bash
pip install black flake8
black app/
flake8 app/
```

## License

MIT License - See LICENSE file for details

## Support & Contribution

For issues, feature requests, or contributions:
1. Open a GitHub issue
2. Create a pull request with your changes
3. Follow the contribution guidelines

## Disclaimer

This is a proof-of-concept autonomous agent system. Use with caution and appropriate governance controls. For production deployment, ensure compliance with your jurisdiction's regulations regarding automated financial transactions and autonomous systems.
