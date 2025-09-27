FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the package
COPY tmin/ ./tmin/
COPY pyproject.toml .

# Install the package
RUN pip install -e .

# Create reports directory
RUN mkdir -p /app/reports

# Set default command
CMD ["python", "-c", "from tmin import PIPE; print('TMIN is ready! Use: docker run -it <image> python -c \"from tmin import PIPE; pipe = PIPE(...); print(pipe.analyze(...))\"')"]
