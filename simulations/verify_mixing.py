"""
Mixing Matrix Verification

Verifies CKM and PMNS mixing matrices derived from FTD framework integers.
"""

import numpy as np
from constants import N_c, N_base, b_3, N_eff, ALPHA, percent_error


# =============================================================================
# CKM MATRIX
# =============================================================================

def derive_ckm_angles():
    """
    Derive CKM mixing angles from framework integers.

    From TRD_VERIFICATION_REPORT.md:
    theta_12 = arcsin(sqrt(N_c/N_eff)) = arcsin(sqrt(3/13)) ~ 28.7 deg
    theta_23 = 10*alpha (radians) ~ 4.2 deg
    theta_13 = N_eff*alpha^2 (radians) ~ 0.40 deg
    delta    = arctan(b_3/N_c) = arctan(7/3) ~ 66.8 deg (CP phase)

    NOTE: CKM angles have known large errors vs experiment.
    Only the CP phase delta matches well (2.1% error).
    """
    # theta_12 from arcsin(sqrt(N_c/N_eff)) - this is actually ~28.7 deg
    # The report says arcsin(sqrt(3/13)) = 28.7 deg
    theta_12 = np.arcsin(np.sqrt(N_c / N_eff))  # radians

    # theta_23 = 10*alpha in radians
    theta_23 = 10 * ALPHA  # radians

    # theta_13 = N_eff*alpha^2 in radians
    theta_13 = N_eff * ALPHA**2  # radians

    # CP phase: arctan(b_3/N_c) - this one is excellent
    delta = np.arctan(b_3 / N_c)  # radians

    return {
        'theta_12': np.degrees(theta_12),
        'theta_23': np.degrees(theta_23),
        'theta_13': np.degrees(theta_13),
        'delta': np.degrees(delta),
        'sin_theta_12': np.sin(theta_12),
        'sin_theta_23': np.sin(theta_23),
        'sin_theta_13': np.sin(theta_13)
    }


def build_ckm_matrix():
    """Build the CKM matrix from derived angles."""
    angles = derive_ckm_angles()

    theta_12 = np.radians(angles['theta_12'])
    theta_23 = np.radians(angles['theta_23'])
    theta_13 = np.radians(angles['theta_13'])
    delta = np.radians(angles['delta'])

    c12, s12 = np.cos(theta_12), np.sin(theta_12)
    c23, s23 = np.cos(theta_23), np.sin(theta_23)
    c13, s13 = np.cos(theta_13), np.sin(theta_13)

    # Standard parameterization
    V = np.array([
        [c12*c13, s12*c13, s13*np.exp(-1j*delta)],
        [-s12*c23 - c12*s23*s13*np.exp(1j*delta),
         c12*c23 - s12*s23*s13*np.exp(1j*delta),
         s23*c13],
        [s12*s23 - c12*c23*s13*np.exp(1j*delta),
         -c12*s23 - s12*c23*s13*np.exp(1j*delta),
         c23*c13]
    ])

    return V, angles


# Experimental CKM values (PDG 2024)
CKM_EXPERIMENTAL = {
    'theta_12': 13.04,  # degrees (Cabibbo angle)
    'theta_23': 2.38,   # degrees
    'theta_13': 0.201,  # degrees
    'delta': 65.4,      # degrees (CP phase)
    'V_ud': 0.97373,
    'V_us': 0.2243,
    'V_ub': 0.00382,
    'V_cd': 0.221,
    'V_cs': 0.975,
    'V_cb': 0.0408,
    'V_td': 0.0080,
    'V_ts': 0.0388,
    'V_tb': 1.013,
}


def verify_ckm_matrix():
    """Verify CKM matrix elements."""
    print("=" * 70)
    print("CKM MATRIX VERIFICATION")
    print("=" * 70)

    V, angles = build_ckm_matrix()

    print("\nMixing Angles:")
    print(f"{'Parameter':<12} {'Derived':<12} {'Expt':<12} {'Error %':<10}")
    print("-" * 50)

    angle_params = [
        ('theta_12', angles['theta_12'], CKM_EXPERIMENTAL['theta_12']),
        ('theta_23', angles['theta_23'], CKM_EXPERIMENTAL['theta_23']),
        ('theta_13', angles['theta_13'], CKM_EXPERIMENTAL['theta_13']),
        ('delta', angles['delta'], CKM_EXPERIMENTAL['delta']),
    ]

    for name, derived, exp in angle_params:
        err = percent_error(derived, exp)
        print(f"{name:<12} {derived:<12.2f} {exp:<12.2f} {err:<10.1f}")

    print("\nCKM Matrix |V_ij|:")
    print(f"{'Element':<12} {'Derived':<12} {'Expt':<12} {'Error %':<10}")
    print("-" * 50)

    elements = [
        ('V_ud', 0, 0), ('V_us', 0, 1), ('V_ub', 0, 2),
        ('V_cd', 1, 0), ('V_cs', 1, 1), ('V_cb', 1, 2),
        ('V_td', 2, 0), ('V_ts', 2, 1), ('V_tb', 2, 2),
    ]

    for name, i, j in elements:
        derived = abs(V[i, j])
        exp = CKM_EXPERIMENTAL[name]
        err = percent_error(derived, exp)
        print(f"{name:<12} {derived:<12.5f} {exp:<12.5f} {err:<10.2f}")

    # Unitarity check
    print("\nUnitarity Check (should be identity):")
    VV_dag = V @ V.conj().T
    print("V * V^dag =")
    for row in VV_dag:
        print("  [" + ", ".join(f"{abs(x):.4f}" for x in row) + "]")

    # Jarlskog invariant
    # From matrix: J = Im(V_ud V_cs V*_us V*_cd)
    J_matrix = np.imag(V[0,0] * V[1,1] * np.conj(V[0,1]) * np.conj(V[1,0]))
    # From FTD formula: J = N_c * alpha^3 / 4 = 3 * alpha^3 / 4
    J_formula = N_c * ALPHA**3 / 4
    J_exp = 3.08e-5
    print(f"\nJarlskog invariant J:")
    print(f"  From matrix: {J_matrix:.2e}")
    print(f"  FTD formula (N_c*alpha^3/4): {J_formula:.2e}")
    print(f"  Expt: {J_exp:.2e}")
    print(f"  FTD formula error: {percent_error(J_formula, J_exp):.1f}%")

    return V, angles


# =============================================================================
# PMNS MATRIX
# =============================================================================

def derive_pmns_angles():
    """
    Derive PMNS mixing angles from framework integers.

    Corrected formulas (verified against experiment):
    sin^2(theta_12) = N_c/(N_c+b_3) = 3/10 = 0.30   -> 33.21 deg (0.7% error)
    sin^2(theta_23) = (N_eff+N_c)/(2*N_eff+N_c) = 16/29 -> 47.97 deg (2.5% error)
    sin^2(theta_13) = 1/(N_base*N_eff) = 1/52      -> 7.97 deg (7% error)
    delta_CP = arctan(b_3/N_c) = arctan(7/3)       -> 66.8 deg

    Note: PMNS CP phase is experimentally ~197 deg but has large uncertainty.
    """
    # theta_12: sin^2 = N_c/(N_c+b_3) = 3/10 = 0.30
    sin2_12 = N_c / (N_c + b_3)
    theta_12 = np.arcsin(np.sqrt(sin2_12))

    # theta_23: sin^2 = (N_eff+N_c)/(2*N_eff+N_c) = 16/29 ~ 0.552
    sin2_23 = (N_eff + N_c) / (2 * N_eff + N_c)
    theta_23 = np.arcsin(np.sqrt(sin2_23))

    # theta_13: sin^2 = 1/(N_base*N_eff) = 1/52 ~ 0.0192
    sin2_13 = 1 / (N_base * N_eff)
    theta_13 = np.arcsin(np.sqrt(sin2_13))

    # CP phase (same formula as CKM - less constrained experimentally)
    delta_CP = np.arctan(b_3 / N_c)

    return {
        'theta_12': np.degrees(theta_12),
        'theta_23': np.degrees(theta_23),
        'theta_13': np.degrees(theta_13),
        'delta_CP': np.degrees(delta_CP),
        'sin2_12': sin2_12,
        'sin2_23': sin2_23,
        'sin2_13': sin2_13
    }


def build_pmns_matrix():
    """Build the PMNS matrix from derived angles."""
    params = derive_pmns_angles()

    theta_12 = np.radians(params['theta_12'])
    theta_23 = np.radians(params['theta_23'])
    theta_13 = np.radians(params['theta_13'])
    delta_CP = np.radians(params['delta_CP'])

    s12, c12 = np.sin(theta_12), np.cos(theta_12)
    s23, c23 = np.sin(theta_23), np.cos(theta_23)
    s13, c13 = np.sin(theta_13), np.cos(theta_13)

    # Standard parameterization (ignoring Majorana phases)
    U = np.array([
        [c12*c13, s12*c13, s13*np.exp(-1j*delta_CP)],
        [-s12*c23 - c12*s23*s13*np.exp(1j*delta_CP),
         c12*c23 - s12*s23*s13*np.exp(1j*delta_CP),
         s23*c13],
        [s12*s23 - c12*c23*s13*np.exp(1j*delta_CP),
         -c12*s23 - s12*c23*s13*np.exp(1j*delta_CP),
         c23*c13]
    ])

    return U, params


# Experimental PMNS values (NuFIT 5.2, NO)
PMNS_EXPERIMENTAL = {
    'sin2_12': 0.304,      # +0.012 -0.012
    'sin2_23': 0.573,      # +0.016 -0.020
    'sin2_13': 0.02219,    # +0.00062 -0.00063
    'theta_12': 33.44,     # degrees
    'theta_23': 49.2,      # degrees
    'theta_13': 8.57,      # degrees
    'delta_CP': 197,       # degrees (NO, best fit)
}


def verify_pmns_matrix():
    """Verify PMNS matrix elements."""
    print("\n" + "=" * 70)
    print("PMNS MATRIX VERIFICATION")
    print("=" * 70)

    U, params = build_pmns_matrix()

    print("\nMixing Angles:")
    print(f"{'Parameter':<12} {'Derived':<12} {'Expt':<12} {'Error %':<10}")
    print("-" * 50)

    angle_params = [
        ('sin2_12', params['sin2_12'], PMNS_EXPERIMENTAL['sin2_12']),
        ('sin2_23', params['sin2_23'], PMNS_EXPERIMENTAL['sin2_23']),
        ('sin2_13', params['sin2_13'], PMNS_EXPERIMENTAL['sin2_13']),
        ('theta_12', params['theta_12'], PMNS_EXPERIMENTAL['theta_12']),
        ('theta_23', params['theta_23'], PMNS_EXPERIMENTAL['theta_23']),
        ('theta_13', params['theta_13'], PMNS_EXPERIMENTAL['theta_13']),
    ]

    for name, derived, exp in angle_params:
        err = percent_error(derived, exp)
        print(f"{name:<12} {derived:<12.4f} {exp:<12.4f} {err:<10.2f}")

    print(f"\nCP Phase:")
    print(f"  Derived: {params['delta_CP']:.1f} deg")
    print(f"  Expt: {PMNS_EXPERIMENTAL['delta_CP']} deg (large uncertainty)")

    print("\nPMNS Matrix |U|:")
    print("        nu_1     nu_2     nu_3")
    labels = ['nu_e', 'nu_mu', 'nu_tau']
    for i, label in enumerate(labels):
        row = [f"{abs(U[i,j]):.4f}" for j in range(3)]
        print(f"  {label:<6} " + "  ".join(row))

    # Unitarity check
    print("\nUnitarity Check:")
    UU_dag = U @ U.conj().T
    print("  Max deviation from identity:", np.max(np.abs(UU_dag - np.eye(3))))

    return U, params


# =============================================================================
# NEUTRINO MASS DIFFERENCES
# =============================================================================

def verify_neutrino_masses():
    """Verify neutrino mass squared differences."""
    print("\n" + "=" * 70)
    print("NEUTRINO MASS DIFFERENCES")
    print("=" * 70)

    # Mass squared differences from FTD
    # Ratio dm^2_31 / dm^2_21 ~ (b_3 + N_c)^2 / N_c = 100/3 ~ 33
    ratio_derived = (b_3 + N_c)**2 / N_c

    # Experimental values
    dm2_21_exp = 7.42e-5   # eV^2
    dm2_31_exp = 2.51e-3   # eV^2 (NO)
    ratio_exp = dm2_31_exp / dm2_21_exp

    print(f"\nMass squared ratio:")
    print(f"  Derived: dm^2_31/dm^2_21 = (b_3+N_c)^2/N_c = {ratio_derived:.1f}")
    print(f"  Expt: {ratio_exp:.1f}")
    print(f"  Error: {percent_error(ratio_derived, ratio_exp):.1f}%")

    print(f"\nExperimental values:")
    print(f"  dm^2_21 = {dm2_21_exp:.2e} eV^2")
    print(f"  dm^2_31 = {dm2_31_exp:.2e} eV^2")


def run_all_mixing_verifications():
    """Run all mixing matrix verifications."""
    print("\n" + "=" * 70)
    print("FTD MIXING MATRIX VERIFICATION SUITE")
    print("=" * 70)
    print(f"\nFramework integers: N_c={N_c}, N_base={N_base}, b_3={b_3}, N_eff={N_eff}")

    verify_ckm_matrix()
    verify_pmns_matrix()
    verify_neutrino_masses()

    print("\n" + "=" * 70)
    print("MIXING VERIFICATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_all_mixing_verifications()
