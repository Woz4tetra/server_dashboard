#!/usr/bin/env bash
set -e

if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

BASE_DIR=$(realpath "$(dirname $0)")

echo "Running server_dashboard systemd services install script"

SERVICE_ROOT_DIR=/etc/systemd/system/

mkdir -p ${SERVICE_ROOT_DIR}
cp ${BASE_DIR}/${SERVICE_NAME} ${SERVICE_ROOT_DIR}

echo "Enabling systemd services"
systemctl daemon-reload
loginctl enable-linger $USER
systemctl enable server_dashboard_logger.service
systemctl enable server_dashboard_frontend.service

systemctl restart server_dashboard_logger.service
systemctl restart server_dashboard_frontend.service

echo "server_dashboard systemd services installation complete"
