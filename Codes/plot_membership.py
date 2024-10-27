import numpy as np
import matplotlib.pyplot as plt
import membership_functions as membership


psi_value = np.linspace(0, 1, 100)
latency_value = np.linspace(0, 100, 300)

psi_low = [membership.triangular(psi, 0, 0, 0.3) for psi in psi_value]
psi_medium = [membership.trapezoidal(
    psi, 0.2, 0.4, 0.6, 0.8) for psi in psi_value]
psi_high = [membership.triangular(psi, 0.7, 1.0, 1.0) for psi in psi_value]


latency_short = [membership.trapezoidal(
    latency, 0, 0, 5, 8) for latency in latency_value]
latency_moderate = [membership.triangular(
    latency, 4, 11, 15) for latency in latency_value]
latency_long = [membership.trapezoidal(
    latency, 12, 18, 300, 300) for latency in latency_value]


plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(psi_value, psi_low, label='low')
plt.plot(psi_value, psi_medium, label='medium')
plt.plot(psi_value, psi_high, label='high')
plt.title("PSI Membership Functions")
plt.xlabel("PSI")
plt.ylabel("Membership Degree")
plt.legend()


plt.subplot(1, 2, 2)
plt.plot(latency_value, latency_short, label='short')
plt.plot(latency_value, latency_moderate, label='moderate')
plt.plot(latency_value, latency_long, label='long')
plt.title("Latency Membership Functions")
plt.xlabel("Latency")
plt.ylabel("Membership Degree")
plt.xlim(-1, 20)
plt.legend()

plt.show()

decision_range = np.linspace(0, 1, 500)

high_confidence = [membership.triangular(
    decision, 0.7, 1.0, 1.0) for decision in decision_range]
moderate_confidence = [membership.triangular(
    decision, 0.4, 0.6, 0.7) for decision in decision_range]
low_confidence = [membership.triangular(
    decision, 0.1, 0.3, 0.4) for decision in decision_range]
deny = [membership.trapezoidal(decision, 0, 0, 0.1, 0.2)
        for decision in decision_range]

plt.figure(figsize=(12, 5))

plt.plot(decision_range, high_confidence, label="high_confidence")
plt.plot(decision_range, moderate_confidence, label="moderate_confidence")
plt.plot(decision_range, low_confidence, label="low_confidence")
plt.plot(decision_range, deny, label="deny")
plt.title("Fuzzy Admission Membership Functions")
plt.xlabel("Fuzzy Decision")
plt.ylabel("Membership Degree")
plt.legend()
plt.show()
