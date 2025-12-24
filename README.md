# Stop Spying On Me - Minimal Prototype

Email privacy service that forwards emails from aliases to real addresses.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
```

Edit `.env` and set:
- `RELAY_HOST`, `RELAY_PORT`: Your SMTP server for forwarding
- `RELAY_USER`, `RELAY_PASSWORD`: SMTP credentials
- `ALIASES`: Comma-separated alias=destination pairs

Example for Gmail:
```
RELAY_HOST=smtp.gmail.com
RELAY_PORT=587
RELAY_USER=your-email@gmail.com
RELAY_PASSWORD=your-app-password
ALIASES=test@localhost=your-email@gmail.com
```

**Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)

### 3. Run Server
```bash
python server.py
```

### 4. Test
In another terminal:
```bash
python test_send.py test@localhost
```

Check your destination inbox for the forwarded email.

## How It Works

1. SMTP server listens on `localhost:8025`
2. Receives email to alias (e.g., `test@localhost`)
3. Looks up destination in `ALIASES` config
4. Forwards email via SMTP relay
5. Logs all activity to console

## Testing with Real Email Clients

Send email using any SMTP client:
```bash
# Using swaks (if installed)
swaks --to test@localhost --server localhost:8025

# Using telnet
telnet localhost 8025
EHLO localhost
MAIL FROM: sender@example.com
RCPT TO: test@localhost
DATA
Subject: Test
This is a test.
.
QUIT
```

## Development

### Running Tests
```bash
pip install -r test-requirements.txt
pytest test_server.py -v --cov=server
```

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

For commercial licensing options, contact: [lloydculpepper4@gmail.com]
