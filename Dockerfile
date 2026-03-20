FROM alpine:3.19

RUN apk add --no-cache python3 py3-pip bash git github-cli

WORKDIR /rose

COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY cli.py .
COPY commands/ commands/

# rose init  — project template
COPY .claude/template/ template/

# rose install — global Claude config
COPY .claude/global/ global/

# rose add — registry configs
COPY .claude/registry/ registry/

WORKDIR /project

ENTRYPOINT ["python3", "/rose/cli.py"]
CMD ["--help"]
