# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS uv

# Install required packages for GUI libraries and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsoup2.4-dev \
    libwebkit2gtk-4.0-dev \
    build-essential \
    python3-dev \
    libpq-dev \
    gettext \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Optional: Install and compile TA-Lib (comment out if not needed)
# Uncomment these lines if you want ta-lib support in Docker
# ENV TALIB_DIR=/usr/local
# RUN wget https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz \
#     && tar -xzf ta-lib-0.6.4-src.tar.gz \
#     && cd ta-lib-0.6.4/ \
#     && ./configure --prefix=$TALIB_DIR \
#     && make -j$(nproc) \
#     && make install \
#     && cd .. \
#     && rm -rf ta-lib-0.6.4-src.tar.gz ta-lib-0.6.4/ \
#     && ldconfig

# Set the working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy pyproject.toml and uv.lock for dependencies
COPY pyproject.toml uv.lock* ./

# Install the project's dependencies using the lockfile and settings
# Note: We're installing base dependencies only (not talib optional)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Copy the entire source code into the container
COPY src/ ./src/

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Set environment variables
ENV TIINGO_API_KEY=your_api_key_here
ENV BINANCE_API_KEY=your_binance_api_key_here
ENV BINANCE_API_SECRET=your_binance_api_secret_here

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Default command to run the MCP server
CMD ["uv", "run", "mcp-trader"]