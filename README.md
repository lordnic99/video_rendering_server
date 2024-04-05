# Project Description

This project is designed to handle the completion messages received from qBittorrent when a torrent download finishes. Upon receiving these messages, the system interacts with a service called "Master" via RabbitMQ to process the information. 
After preparing necessary preconditions, the "Master" service then calls another service called "Render Service" to generate the video.

# Functionality
Integration with qBittorrent: The system is integrated with qBittorrent to receive completion messages when a torrent download finishes.

Communication via RabbitMQ: Upon receiving completion messages, the system communicates with a service called "Master" via RabbitMQ. This allows for efficient and reliable message passing between components of the system.

Video Generation: The "Master" service processes the received messages and prepares necessary preconditions. It then calls the "Render Service" to generate the video file. This involves combining a given audio file with a JPEG image file to create the desired video output.

# Components
qBittorrent Integration: This component manages the interaction with qBittorrent to receive completion messages.

RabbitMQ Communication Layer: Handles the message passing between the system and the "Master" service using RabbitMQ.

Master Service: Processes the received completion messages, prepares preconditions, and orchestrates the generation of the video file.

Render Service: Once the preconditions are prepared by the "Master" service, the "Render Service" is called to generate the video file.

# Contact
If you want to request design, implement, about the problem you want to solve
Telegram: https://t.me/jus_t_name