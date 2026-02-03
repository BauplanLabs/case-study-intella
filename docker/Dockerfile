FROM prefecthq/prefect:3-python3.12

WORKDIR /app

# Install uv for faster dependency installation
RUN pip install uv

# Copy dependency files first for better caching
COPY pyproject.toml ./
COPY case_study_telemetry/__init__.py ./case_study_telemetry/

# Install dependencies using uv
RUN uv pip install --system -e .

# Copy the rest of the application
COPY . .

# Default command - can be overridden in docker-compose
CMD ["prefect", "worker", "start", "--pool", "process-pool", "--type", "process"]
