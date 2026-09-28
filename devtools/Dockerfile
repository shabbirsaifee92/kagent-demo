FROM python:3.12-slim
ARG TARGETARCH=arm64
RUN apt-get update && apt-get install -y --no-install-recommends \
      git curl ca-certificates make jq \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://get.helm.sh/helm-v3.16.3-linux-${TARGETARCH}.tar.gz \
      | tar -xz -C /tmp && mv /tmp/linux-${TARGETARCH}/helm /usr/local/bin/helm \
 && curl -fsSLo /usr/local/bin/kubectl \
      https://dl.k8s.io/release/v1.32.0/bin/linux/${TARGETARCH}/kubectl \
 && chmod +x /usr/local/bin/kubectl
RUN curl -fsSL https://github.com/moby/buildkit/releases/download/v0.17.2/buildkit-v0.17.2.linux-${TARGETARCH}.tar.gz \
      | tar -xz -C /tmp && mv /tmp/bin/buildctl /usr/local/bin/buildctl
RUN curl -fsSL https://github.com/tilt-dev/tilt/releases/download/v0.33.21/tilt.0.33.21.linux.$(echo $TARGETARCH | sed 's/amd64/x86_64/;s/arm64/arm64/').tar.gz \
      | tar -xz -C /tmp tilt && mv /tmp/tilt /usr/local/bin/tilt || echo "tilt install skipped"
RUN pip install --no-cache-dir pytest pytest-cov requests
COPY server.py /server.py
ENV WORKSPACE=/workspace \
    BUILDKIT_HOST=tcp://buildkitd.build.svc:1234 \
    REGISTRY=registry.build.svc:5000
RUN mkdir -p /workspace
ENTRYPOINT ["python", "-u", "/server.py"]
