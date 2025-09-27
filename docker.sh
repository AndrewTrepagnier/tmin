#!/bin/bash

# Simple Docker script for TMIN
# Usage: ./docker.sh [build|run|test]

set -e

IMAGE_NAME="tmin"
CONTAINER_NAME="tmin-container"

case "${1:-run}" in
    "build")
        echo "building TMIN Docker image..."
        docker build -t $IMAGE_NAME .
        echo "build complete!"
        ;;
    "run")
        echo "running TMIN container..."
        docker run -it --rm \
            -v $(pwd)/reports:/app/reports \
            --name $CONTAINER_NAME \
            $IMAGE_NAME bash
        ;;
    "test")
        echo "testing TMIN in container..."
        docker run --rm \
            -v $(pwd)/reports:/app/reports \
            $IMAGE_NAME python -c "
from tmin import PIPE

# Test basic functionality
pipe = PIPE(
    pressure=50,
    nps=2,
    schedule=40,
    pressure_class=150,
    metallurgy='Intermediate/Low CS',
    yield_stress=23333
)

results = pipe.analyze(measured_thickness=0.060)
print(f'Analyze test passed! Flag: {results[\"flag\"]}')

# Test report generation
report_path = pipe.generate_report(measured_thickness=0.060, filename='docker_test')
print(f'Report generated: {report_path}')
"
        ;;
    *)
        echo "Usage: $0 [build|run|test]"
        echo "  build - Build the Docker image"
        echo "  run   - Run interactive container"
        echo "  test  - Run quick test"
        exit 1
        ;;
esac
