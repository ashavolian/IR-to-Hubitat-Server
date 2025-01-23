#!/bin/bash

# Print status message with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Stop all services
log "Stopping services..."
sudo systemctl stop ir-control.service
sudo systemctl stop lircd.service
sudo pkill -f "python3.*app.py"

# Wait for services to stop
sleep 2

# Start LIRC first
log "Starting LIRC..."
sudo systemctl start lircd.service
sleep 2

# Check if LIRC started successfully
if ! sudo systemctl is-active --quiet lircd.service; then
    log "ERROR: LIRC failed to start. Check logs with: sudo journalctl -u lircd.service"
    exit 1
fi

# Start IR control service
log "Starting IR control service..."
sudo systemctl start ir-control.service
sleep 2

# Check if IR control started successfully
if ! sudo systemctl is-active --quiet ir-control.service; then
    log "ERROR: IR control service failed to start. Check logs with: sudo journalctl -u ir-control.service"
    exit 1
fi

# Start the Flask app (assuming it's running as a service, otherwise adjust as needed)
log "Starting Flask app..."
sudo systemctl start flask-ir-app.service

# Final status check
log "Checking final status..."
echo "-------------------"
echo "LIRC Status:"
sudo systemctl status lircd.service | head -n 3
echo "-------------------"
echo "IR Control Status:"
sudo systemctl status ir-control.service | head -n 3
echo "-------------------"
echo "Flask App Status:"
sudo systemctl status flask-ir-app.service | head -n 3

log "Restart complete!"
