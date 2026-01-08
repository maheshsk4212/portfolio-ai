# AI Portfolio Intelligence Platform

A secure, read-only, AI-powered investment analysis platform that connects to a Zerodha Demat account, continuously monitors the portfolio, and explains insights like a calm, 40-year experienced Indian investor.

## Setup

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**
    Copy `.env.example` to `.env` and fill in your keys.
    ```bash
    cp .env.example .env
    ```

3.  **Run Server**
    ```bash
    uvicorn app:app --reload
    ```

## Features
- Read-only Zerodha integration
- AI-powered portfolio analysis (calm, long-term focus)
- Daily background monitoring
