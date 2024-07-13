#!/usr/bin/env bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

echo "Running server_dashboard systemd services uninstall script"

SERVICE_ROOT_DIR=/etc/systemd/system/

rm ${SERVICE_ROOT_DIR}/server_dashboard_logger.service
rm ${SERVICE_ROOT_DIR}/server_dashboard_frontend.service

echo "Disabling systemd services"
systemctl daemon-reload
systemctl stop server_dashboard_logger.service
systemctl stop server_dashboard_frontend.service

systemctl disable server_dashboard_logger.service
systemctl disable server_dashboard_frontend.service

echo "server_dashboard systemd services uninstallation complete"
