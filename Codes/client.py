import socket
import struct
import io
import time
from PIL import Image
import pygame
import matplotlib.pyplot as plt
import sys
import csv
import time


def get_cpu_load():
    # Sample function to return fixed CPU load
    return 100


def plot_data(latencies, cpu_loads, elapsed_times):
    """ Plot the average latency and CPU load in a vertical layout. """
    plt.figure(figsize=(6, 12))

    # Plot for Average Latency
    plt.subplot(2, 1, 1)
    plt.plot(elapsed_times, latencies, label='Average Latency (ms)')
    plt.xlabel('Time (s)')
    plt.ylabel('Average Latency (ms)')
    plt.title('Average Latency Over Time')
    plt.grid(True)

    # Plot for CPU Load
    plt.subplot(2, 1, 2)
    plt.plot(elapsed_times, cpu_loads, label='CPU Load (%)')
    plt.xlabel('Time (s)')
    plt.ylabel('CPU Load (%)')
    plt.title('CPU Load Over Time')
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def main(duration):
    HOST, PORT = '172.22.174.196', 8080
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

    CONTROLLER_HOST = '172.22.174.196'
    CONTROLLER_PORT = 9090

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Image Viewer")

    total_rtt = 0
    request_count = 0
    latencies = []
    cpu_loads = []
    elapsed_times = []

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as controller_socket, open('ProxmoxDocker_withoutcgroupPID_.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Elapsed Time (s)', 'Average RTT (ms)',
                        'Current RTT (ms)', 'Current time'])
        s.settimeout(10)
        start_time = time.time()

        while time.time() - start_time < duration:
            try:
                send_time = time.time()
                s.sendto(b"Request", (HOST, PORT))

                num_chunks_data, _ = s.recvfrom(4)
                num_chunks = struct.unpack(">I", num_chunks_data)[0]
                image_data = bytearray()

                for _ in range(num_chunks):
                    chunk, _ = s.recvfrom(65507)
                    image_data.extend(chunk)
                receive_time = time.time()

                rtt = (receive_time - send_time) * 1000
                total_rtt += rtt
                request_count += 1
                average_rtt = total_rtt / request_count
                latencies.append(average_rtt)

                elapsed_time = receive_time - start_time
                elapsed_times.append(elapsed_time)

                cpu_load = get_cpu_load()
                cpu_loads.append(cpu_load if cpu_load is not None else 0)

                latency_message = struct.pack('>f', average_rtt)
                controller_socket.sendto(
                    latency_message, (CONTROLLER_HOST, CONTROLLER_PORT))

                print(f"RTT: {rtt} ms, Average RTT: {
                      average_rtt} ms, CPU Load: {cpu_load}%")

                # Write data to CSV
                writer.writerow([elapsed_time, average_rtt, rtt, receive_time])

                if len(image_data) > 0:
                    try:
                        image = Image.open(io.BytesIO(image_data))
                        frame = pygame.image.frombuffer(
                            image.tobytes(), image.size, image.mode)
                        screen.blit(frame, (0, 0))
                        pygame.display.flip()
                    except IOError:
                        print(
                            "Received data is not a valid image, ignoring this frame.")
                time.sleep(0.3)
            except socket.timeout:
                print("Request timed out. No response from server.")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    plot_data(latencies, cpu_loads, elapsed_times)
                    pygame.quit()
                    return

        plot_data(latencies, cpu_loads, elapsed_times)

    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python client.py <duration_seconds>")
        sys.exit(1)

    duration_seconds = int(sys.argv[1])
    main(duration_seconds)
