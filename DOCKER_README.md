# Docker Deployment Guide

## Quick Start

1. Build and run all services:
   `
   docker-compose up --build
   `

2. Run in background:
   `
   docker-compose up -d --build
   `

3. View logs:
   `
   docker-compose logs -f
   `

4. Stop services:
   `
   docker-compose down
   `

## Access URLs

- Frontend (Streamlit): http://localhost:8501
- Backend (FastAPI): http://localhost:8000
- API Docs: http://localhost:8000/docs

## Rebuild After Changes

`
docker-compose down
docker-compose up --build
`
