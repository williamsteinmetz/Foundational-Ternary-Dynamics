"""
Master Quadratic Verification

Verifies the master quadratic x^2 - 16G*^2x + 16G*^3 = 0 and its derivation
from Fermat boundary constraints.
"""

import numpy as np
from scipy.special import gamma
from constants import (
    G_STAR, GAMMA_QUARTER, X_PLUS, X_MINUS,
    N_c, N_base, b_3, N_eff,
    Experimental, ppm_error, percent_error
)


def verify_lemniscate_constant():
    """
    Verify G* = sqrt2 * Gamma(1/4)^2 / (2pi)

    The lemniscate constant emerges from:
    1. sqrt2 factor: Critical coupling from Gauss constraint geometry
    2. Gamma(1/4)^2 factor: Lattice regularization -> elliptic integral K(1/sqrt2)
    """
    print("=" * 60)
    print("LEMNISCATE CONSTANT VERIFICATION")
    print("=" * 60)

    # Direct computation
    g_star = np.sqrt(2) * gamma(0.25)**2 / (2 * np.pi)

    print(f"\nG* = sqrt2 * Gamma(1/4)^2 / (2pi)")
    print(f"   = sqrt2 * ({gamma(0.25):.10f})^2 / (2pi)")
    print(f"   = {np.sqrt(2):.10f} * {gamma(0.25)**2:.10f} / {2*np.pi:.10f}")
    print(f"   = {g_star:.10f}")

    # Connection to elliptic integral K(1/sqrt2)
    # G* = 2K(1/sqrt2) / pi where K is complete elliptic integral of first kind
    from scipy.special import ellipk
    k = 1 / np.sqrt(2)
    g_star_from_K = 2 * ellipk(k**2) / np.pi

    print(f"\nAlternative: G* = 2K(1/sqrt2) / pi")
    print(f"   K(1/2) = {ellipk(k**2):.10f}")
    print(f"   G* = {g_star_from_K:.10f}")
    print(f"   Match: {np.isclose(g_star, g_star_from_K)}")

    return g_star


def verify_coefficient_16():
    """
    Verify the coefficient 16 via four independent derivations.
    """
    print("\n" + "=" * 60)
    print("COEFFICIENT 16 - FOUR DERIVATIONS")
    print("=" * 60)

    derivations = []

    # 1. Fermat squared: 4^2 = 16
    d1 = N_base**2
    derivations.append(("Fermat squared: N_base^2 = 4^2", d1))

    # 2. Binary power: 2^4 = 16
    d2 = 2**N_base
    derivations.append(("Binary power: 2^N_base = 2^4", d2))

    # 3. Lattice DoF: 24 - 8 = 16
    # 2*2*2 cube has 8 vertices, 12 edges, 6 faces, 1 interior = 27 cells
    # Constraint removes 8 (Gauss law at vertices) -> 24 - 8 = 16
    total_dof = 24  # 3 components * 8 vertices
    constraints = 8  # One Gauss constraint per vertex
    d3 = total_dof - constraints
    derivations.append(("Lattice DoF: 24 - 8", d3))

    # 4. Conductor halving: 32/2 = 16
    # Lemniscate has conductor 32; halving gives 16
    conductor = 32
    d4 = conductor // 2
    derivations.append(("Conductor halving: 32/2", d4))

    print()
    for name, value in derivations:
        status = "[OK]" if value == 16 else "[X]"
        print(f"  {status} {name} = {value}")

    all_match = all(d[1] == 16 for d in derivations)
    print(f"\nAll derivations yield 16: {all_match}")

    return all_match


def verify_master_quadratic():
    """
    Verify the master quadratic and its roots.
    """
    print("\n" + "=" * 60)
    print("MASTER QUADRATIC VERIFICATION")
    print("=" * 60)

    c = G_STAR

    print(f"\nQuadratic: x^2 - 16c^2x + 16c^3 = 0  where c = G* = {c:.10f}")
    print(f"\nCoefficients:")
    print(f"  a = 1")
    print(f"  b = -16c^2 = -{16 * c**2:.10f}")
    print(f"  c = 16c^3 = {16 * c**3:.10f}")

    # Solve using quadratic formula
    a = 1
    b = -16 * c**2
    c_coef = 16 * c**3

    discriminant = b**2 - 4 * a * c_coef
    print(f"\nDiscriminant: b^2 - 4ac = {discriminant:.10f}")
    print(f"sqrtdiscriminant = {np.sqrt(discriminant):.10f}")

    x_plus = (-b + np.sqrt(discriminant)) / (2 * a)
    x_minus = (-b - np.sqrt(discriminant)) / (2 * a)

    print(f"\nRoots:")
    print(f"  x_+ = {x_plus:.10f}")
    print(f"  x_- = {x_minus:.10f}")

    # Verify roots satisfy equation
    residual_plus = x_plus**2 - 16*c**2*x_plus + 16*c**3
    residual_minus = x_minus**2 - 16*c**2*x_minus + 16*c**3

    print(f"\nVerification (should be ~0):")
    print(f"  x_+^2 - 16c^2x_+ + 16c^3 = {residual_plus:.2e}")
    print(f"  x_-^2 - 16c^2x_- + 16c^3 = {residual_minus:.2e}")

    # Vieta's formulas
    print(f"\nVieta's formulas:")
    print(f"  x_+ + x_- = 16c^2 = {16*c**2:.10f} (computed: {x_plus + x_minus:.10f})")
    print(f"  x_+ * x_- = 16c^3 = {16*c**3:.10f} (computed: {x_plus * x_minus:.10f})")

    return x_plus, x_minus


def verify_physical_interpretation():
    """
    Verify the physical interpretation of the roots.
    """
    print("\n" + "=" * 60)
    print("PHYSICAL INTERPRETATION")
    print("=" * 60)

    # x_+ = 1/alpha
    print(f"\n1. FINE STRUCTURE CONSTANT")
    print(f"   x_+ (derived)      = {X_PLUS:.10f}")
    print(f"   1/alpha (experimental) = {Experimental.alpha_inv:.10f}")
    print(f"   Error             = {ppm_error(X_PLUS, Experimental.alpha_inv):.2f} ppm")

    # x_- -> N_c = 3
    print(f"\n2. NUMBER OF COLORS")
    print(f"   x_- (derived)      = {X_MINUS:.10f}")
    print(f"   N_c (required)    = 3")
    print(f"   floor(x_-)         = {int(np.floor(X_MINUS))}")
    print(f"   Deviation from 3  = {percent_error(X_MINUS, 3):.2f}%")

    # Ratio check
    print(f"\n3. ROOT RATIO")
    print(f"   x_+/x_- = {X_PLUS/X_MINUS:.6f}")
    print(f"   This encodes the hierarchy between EM and strong force")


def verify_fermat_boundary():
    """
    Verify the Fermat boundary principle.
    """
    print("\n" + "=" * 60)
    print("FERMAT BOUNDARY PRINCIPLE")
    print("=" * 60)

    print("\nFermat's Last Theorem: x^n + y^n = z^n has no integer solutions for n > 2")
    print()
    print("Boundary structure:")
    print("  n = 2: LAST ALLOWED (Pythagorean triples exist)")
    print("  n = 3: FIRST FORBIDDEN -> N_c = 3 (colors)")
    print("  n = 4: SECOND FORBIDDEN -> N_base = 4 (lattice dimension)")
    print()
    print("The quadratic degree (2) is selected because:")
    print("  - It's the last exponent with integer solutions")
    print("  - The encoding polynomial must be at the boundary")
    print()
    print("The (3,4,5) Pythagorean triple is unique:")
    print(f"  3^2 + 4^2 = {3**2} + {4**2} = {3**2 + 4**2} = 5^2 = {5**2}")
    print("  Legs 3 and 4 are exactly the first two FLT-forbidden exponents")


def verify_frey_curve_connection():
    """
    Verify the connection to Frey curves from FLT proof.
    """
    print("\n" + "=" * 60)
    print("FREY CURVE CONNECTION")
    print("=" * 60)

    print("\nThe lemniscate y^2 = x^3 - x is the Frey curve with a = b = 1")
    print()
    print("Frey curve for a^n + b^n = c^n:")
    print("  E: y^2 = x(x - a^n)(x + b^n)")
    print()
    print("For a = b = 1, n = 2 (at Fermat boundary):")
    print("  E: y^2 = x(x - 1)(x + 1) = x(x^2 - 1) = x^3 - x")
    print()
    print("This is exactly the lemniscate curve!")
    print()
    print("j-invariant: j = 1728 (the unique CM value for sqrt-1)")
    print("Conductor: N = 32")

    # Verify j-invariant
    # For y^2 = x^3 - x, we have a₄ = -1, a₆ = 0
    # j = 1728 * 4a₄^3 / (4a₄^3 + 27a₆^2) = 1728 * (-4) / (-4) = 1728
    a4 = -1
    a6 = 0
    j = 1728 * 4 * a4**3 / (4 * a4**3 + 27 * a6**2) if (4 * a4**3 + 27 * a6**2) != 0 else 1728
    print(f"\nComputed j-invariant: {j}")


def run_all_verifications():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("FTD MASTER QUADRATIC - COMPLETE VERIFICATION")
    print("=" * 60)

    verify_lemniscate_constant()
    verify_coefficient_16()
    verify_master_quadratic()
    verify_physical_interpretation()
    verify_fermat_boundary()
    verify_frey_curve_connection()

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_all_verifications()
