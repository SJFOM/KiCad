# Vovp parameters
R1 = 9.09e3
R2 = 10e3

# Vout parameters
Rtop = 71.5e3
Rbot = 10e3

V_OVP = 1.245 * (67e3 * (R1 + R2))/(15e3 * R2)

V_OUT = 1.234 * ((Rtop/Rbot) + 1)

print(f"Vovp: {V_OVP:.2f} V")
print(f"Vout: {V_OUT:.2f} V")
