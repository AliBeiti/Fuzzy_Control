import numpy as np
import socket
import struct
import select
import time
import random
import membership_functions as membership


def fuzzify_psi(psi):
    low = membership.triangular(psi, 0, 0, 0.4)
    medium = membership.trapezoidal(psi, 0.3, 0.5, 0.6, 0.8)
    high = membership.triangular(psi, 0.7, 1.0, 1.0)
    return {'low': low, 'medium': medium, 'high': high}


def fuzzify_latency(latency):
    short = membership.trapezoidal(latency, 0, 0, 5, 8)
    moderate = membership.triangular(latency, 4, 11, 15)
    long = membership.trapezoidal(latency, 12, 18, 300, 300)
    return {'short': short, 'moderate': moderate, 'long': long}


def evaluate_rules(fuzzy_psi, fuzzy_latency):

    # Rule 1: IF PSI is low AND latency is short, THEN confidently admit (high confidence)
    high_confidence = min(fuzzy_psi['low'], fuzzy_latency['short'])

    # Rule 2: IF PSI is low AND latency is moderate, THEN cautiously admit (moderate confidence)
    moderate_confidence_1 = min(fuzzy_psi['low'], fuzzy_latency['moderate'])

    # Rule 3: IF PSI is low AND latency is long, THEN admit with low confidence
    low_confidence_1 = min(fuzzy_psi['low'], fuzzy_latency['long'])

    # Rule 4: IF PSI is medium AND latency is short, THEN consider admission (moderate confidence)
    moderate_confidence_2 = min(fuzzy_psi['medium'], fuzzy_latency['short'])

    # Rule 5: IF PSI is medium AND latency is moderate, THEN admit cautiously (moderate confidence)
    moderate_confidence_3 = min(fuzzy_psi['medium'], fuzzy_latency['moderate'])

    # Rule 6: IF PSI is medium AND latency is long, THEN deny admission
    deny_1 = min(fuzzy_psi['medium'], fuzzy_latency['long'])

    # Rule 7: IF PSI is high AND latency is short, THEN cautious admission (low confidence)
    low_confidence_2 = min(fuzzy_psi['high'], fuzzy_latency['short'])

    # Rule 8: IF PSI is high AND latency is moderate, THEN deny admission
    deny_2 = min(fuzzy_psi['high'], fuzzy_latency['moderate'])

    # Rule 9: IF PSI is high AND latency is long, THEN reject outright (deny admission)
    deny_3 = min(fuzzy_psi['high'], fuzzy_latency['long'])

    return {
        'high_confidence': high_confidence,
        'moderate_confidence': max(moderate_confidence_1, moderate_confidence_2, moderate_confidence_3),
        'low_confidence': max(low_confidence_1, low_confidence_2),
        'deny': max(deny_1, deny_2, deny_3)
    }


def fuzzify_admission(decision, fuzzy_set):
    if fuzzy_set == 'high_confidence':
        return membership.triangular(decision, 0.7, 1.0, 1.0)
    elif fuzzy_set == 'moderate_confidence':
        return membership.triangular(decision, 0.4, 0.6, 0.7)
    elif fuzzy_set == 'low_confidence':
        return membership.triangular(decision, 0.1, 0.3, 0.4)
    elif fuzzy_set == 'deny':
        return membership.trapezoidal(decision, 0, 0, 0.1, 0.2)


def defuzzify_admission(rules_output):
    decision_range = np.linspace(0, 1, 400)
    aggregated_output = np.zeros_like(decision_range)

    for i, decision in enumerate(decision_range):
        aggregated_output[i] = max(fuzzify_admission(decision, 'high_confidence') * rules_output['high_confidence'],
                                   fuzzify_admission(
                                       decision, 'moderate_confidence') * rules_output['moderate_confidence'],
                                   fuzzify_admission(
                                       decision, 'low_confidence') * rules_output['low_confidence'],
                                   fuzzify_admission(
                                       decision, 'deny') * rules_output['deny']
                                   )

    # Centroid Method
    numerator = np.sum(decision_range * aggregated_output)
    denominator = np.sum(aggregated_output)

    # crisp decision
    if denominator == 0:
        return 0
    else:
        return numerator / denominator


def read_cpu_pressure():
    try:
        with open('/proc/pressure/cpu') as file:
            for line in file:
                if line.startswith('some'):
                    total_value = line.split('total=')[1].strip()
                    return float(total_value)
    except Exception as e:
        print(f"Error: {e}")
        return None


def fetchPsi(interval):
    prevTotal = read_cpu_pressure()
    time.sleep(interval)
    current = read_cpu_pressure()
    diff = current - prevTotal
    percentage_change = (diff / (interval * 1000000)) * 100
    return percentage_change


interval = 0.3


def listen_for_latency(duration):
    latency_list = []
    time_list = []
    host = '127.0.0.1'
    port = 9090
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))
    print("Listening for UDP packets...")

    start_time = time.time()

    try:
        while time.time() - start_time < duration:
            try:
                data, addr = udp_socket.recvfrom(1024)
                if data:

                    latency = struct.unpack('>f', data)[0]
                    latency_list.append(latency)
                    time_list.append(time.time())
                    psi = fetchPsi(interval)

                    fuzzified_latency = fuzzify_latency(latency)
                    fuzzfied_psi = fuzzify_psi(psi)

                    evaluated_rules = evaluate_rules(
                        fuzzfied_psi, fuzzified_latency)

                    crisp_output = defuzzify_admission(evaluated_rules)

                    if crisp_output >= 0.7:
                        # contianer admission must be done here
                        print("admit confidently \n A new container admitted")
                    elif 0.4 < crisp_output < 0.7:
                        # container admission is done cautiously this is for the time that we have some other facotrs for admittion
                        print("admit cautiously \n A new container admitted")
                    else:
                        print("deny admission")

                    print(f"received from {addr} | Latency: {latency} ms , PSI: {
                          psi}, Admission decision: {crisp_output}")

            except socket.timeout:
                continue
    finally:
        udp_socket.close()


listen_for_latency(700)
