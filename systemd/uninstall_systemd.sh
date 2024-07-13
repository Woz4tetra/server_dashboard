#!/usr/bin/env bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

echo "Running server_dashboard_logger systemd service uninstall script"

SERVICE_NAME=server_dashboard_logger.service
SERVICE_ROOT_DIR=/etc/systemd/system/

rm ${SERVICE_ROOT_DIR}/${SERVICE_NAME}

echo "Disabling systemd services"
systemctl daemon-reload
systemctl stop ${SERVICE_NAME}
systemctl disable ${SERVICE_NAME}

echo "server_dashboard_logger systemd service uninstallation complete"
