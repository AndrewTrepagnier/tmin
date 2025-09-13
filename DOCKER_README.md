# TMIN Docker Setup

This directory contains Docker configuration for the TMIN package, allowing you to spin up fresh containers for testing and development.

## Quick Start

### 1. Build All Images
```bash
./docker.sh build
```

### 2. Run Tests in Fresh Container
```bash
./docker.sh test
```

### 3. Start Development Environment
```bash
./docker.sh dev
```

## Available Commands

### Docker Management Script (`./docker.sh`)

| Command | Description |
|---------|-------------|
| `build` | Build all Docker images (dev, test, prod) |
| `dev` | Start development container with volume mounting |
| `test` | Run tests in fresh container |
| `test-cov` | Run tests with coverage in fresh container |
| `lint` | Run linting in fresh container |
| `format` | Format code in fresh container |
| `clean` | Clean up Docker resources |
| `jupyter` | Start Jupyter notebook server |
| `shell` | Open shell in development container |
| `logs` | Show container logs |
| `stop` | Stop all containers |

### Docker Compose Commands

| Command | Description |
|---------|-------------|
| `docker-compose up -d tmin-dev` | Start development container |
| `docker-compose up -d tmin-test` | Start testing container |
| `docker-compose up -d tmin-prod` | Start production container |
| `docker-compose up -d tmin-jupyter` | Start Jupyter notebook |
| `docker-compose down` | Stop all containers |

## Docker Images

### 1. Development Image (`tmin-dev`)
- **Purpose**: Interactive development environment
- **Features**: 
  - All dependencies installed
  - Volume mounting for live code changes
  - Bash shell access
  - Jupyter notebook support
- **Usage**: `./docker.sh dev`

### 2. Testing Image (`tmin-test`)
- **Purpose**: Fresh testing environment
- **Features**:
  - Clean environment for each test run
  - All test dependencies
  - Coverage reporting
- **Usage**: `./docker.sh test`

### 3. Production Image (`tmin-prod`)
- **Purpose**: Production deployment
- **Features**:
  - Minimal dependencies
  - Non-root user
  - Optimized for size
- **Usage**: `docker run tmin-prod`

## Testing Workflows

### Fresh Container Testing
```bash
# Run all tests in fresh container
./docker.sh test

# Run tests with coverage
./docker.sh test-cov

# Run specific test file
docker run --rm -v "$(pwd)":/app tmin-test python -m pytest tests/test_core_dev.py -v

# Run tests with specific markers
docker run --rm -v "$(pwd)":/app tmin-test python -m pytest tests/ -m "not slow" -v
```

### Development Testing
```bash
# Start development environment
./docker.sh dev

# Access container shell
./docker.sh shell

# Inside container, run tests
python -m pytest tests/ -v

# Run specific tests
python -m pytest tests/test_core_dev.py::TestPIPECoreDev::test_pipe_creation -v
```

## Code Quality Workflows

### Linting
```bash
# Run linting in fresh container
./docker.sh lint

# Or manually
docker run --rm -v "$(pwd)":/app tmin-dev flake8 tmin tests
docker run --rm -v "$(pwd)":/app tmin-dev mypy tmin --ignore-missing-imports
```

### Code Formatting
```bash
# Format code in fresh container
./docker.sh format

# Or manually
docker run --rm -v "$(pwd)":/app tmin-dev black tmin tests
```

## Jupyter Notebook Development

### Start Jupyter Server
```bash
./docker.sh jupyter
```

### Access Jupyter
1. Open browser to `http://localhost:8888`
2. Use token from container logs
3. Create notebooks in `tutorials/` directory

### Stop Jupyter
```bash
docker-compose stop tmin-jupyter
```

## Multi-Python Version Testing

### Test Multiple Python Versions
```bash
# Python 3.8
docker build --build-arg PYTHON_VERSION=3.8 -t tmin-test-38 .

# Python 3.9
docker build --build-arg PYTHON_VERSION=3.9 -t tmin-test-39 .

# Python 3.10
docker build --build-arg PYTHON_VERSION=3.10 -t tmin-test-310 .

# Python 3.11
docker build --build-arg PYTHON_VERSION=3.11 -t tmin-test-311 .
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Docker Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build and test
      run: |
        docker build --target testing -t tmin-test .
        docker run --rm tmin-test
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x docker.sh
   ```

2. **Port Already in Use**
   ```bash
   docker-compose down
   ./docker.sh clean
   ```

3. **Out of Disk Space**
   ```bash
   ./docker.sh clean
   docker system prune -a
   ```

4. **Build Failures**
   ```bash
   # Check Dockerfile syntax
   docker build --target development -t tmin-dev .
   
   # Check dependencies
   docker run --rm tmin-dev pip list
   ```

### Debugging

1. **Check Container Status**
   ```bash
   docker-compose ps
   ```

2. **View Container Logs**
   ```bash
   ./docker.sh logs
   ```

3. **Access Container Shell**
   ```bash
   ./docker.sh shell
   ```

4. **Inspect Image**
   ```bash
   docker inspect tmin-dev
   ```

## Best Practices

### 1. Always Use Fresh Containers for Testing
- Ensures clean environment
- Catches dependency issues
- Mimics production environment

### 2. Use Volume Mounting for Development
- Live code changes
- Faster iteration
- Debugging support

### 3. Clean Up Regularly
```bash
./docker.sh clean
```

### 4. Test Multiple Python Versions
- Ensures compatibility
- Catches version-specific issues

## File Structure

```
.
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Service definitions
├── .dockerignore          # Files to exclude from build
├── docker.sh              # Management script
└── README.md              # This file
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTHONPATH` | Python path | `/app` |
| `PYTHONUNBUFFERED` | Unbuffered output | `1` |
| `PIP_NO_CACHE_DIR` | Disable pip cache | `1` |

## Security Notes

- All containers run as non-root user (`tmin`)
- Minimal base images used
- No unnecessary packages installed
- Volume mounts are read-only where possible
