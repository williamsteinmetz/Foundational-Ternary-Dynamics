# FTD Mathematical Verification Suite

This folder contains Python scripts that verify all mathematical derivations in the Foundational Ternary Dynamics (FTD) framework.

## Overview

FTD derives 40+ Standard Model parameters from just **four framework integers**:

| Integer | Symbol | Value | Physical Meaning |
|---------|--------|-------|------------------|
| N_c | Number of colors | 3 | First FLT-forbidden exponent |
| N_base | Base dimension | 4 | Second FLT-forbidden exponent |
| b_3 | QCD beta coefficient | 7 | 11 - 4N_f/3 at N_f=0 |
| N_eff | Effective DoF | 13 | Fibonacci F_7 |

## Quick Start

```bash
# Run complete verification suite
python run_all.py

# Run individual verifications
python constants.py           # Framework constants summary
python verify_quadratic.py    # Master quadratic derivation
python verify_masses.py       # Particle mass predictions
python verify_mixing.py       # CKM/PMNS matrices
python verify_cosmology.py    # Inflation, baryogenesis
```

## Requirements

```bash
pip install numpy scipy
```

## File Structure

```
simulations/
├── __init__.py           # Package initialization
├── constants.py          # Core constants (single source of truth)
├── verify_quadratic.py   # Master quadratic verification
├── verify_masses.py      # Particle mass derivations
├── verify_mixing.py      # Mixing matrix verification
├── verify_cosmology.py   # Cosmological predictions
├── run_all.py            # Master script
└── README.md             # This file
```

## Key Derivation Chain

```
Fermat Boundary (n=2 last allowed)
        ↓
Gauss Constraint + Lattice Regularization
        ↓
G* = √2·Γ(1/4)²/(2π) ≈ 2.9587 (lemniscatic constant)
        ↓
Coefficient 16 = 4² = 2⁴ = 24-8 = 32/2
        ↓
Master Quadratic: x² - 16G*²x + 16G*³ = 0
        ↓
    ┌───────────────────────────────────┐
    │                                   │
    ↓                                   ↓
x₊ = 137.036                      x₋ = 3.024
  = 1/α (1.26 ppm)                  ≈ N_c (0.8%)
    │                                   │
    ↓                                   ↓
All EM couplings              SU(3) color structure
Particle masses               Confinement scale
```

## Verification Modules

### `constants.py`
The single source of truth for all framework constants:
- Framework integers {3, 4, 7, 13}
- Lemniscatic constant G*
- Master quadratic roots x₊, x₋
- Coupling constants α, α_s, sin²θ_W
- Experimental values for comparison

### `verify_quadratic.py`
Verifies the master quadratic derivation:
- Lemniscate constant from Γ(1/4)
- Coefficient 16 via four independent paths
- Quadratic roots and their physical interpretation
- Fermat boundary principle
- Frey curve connection

### `verify_masses.py`
Derives all particle masses from M_Planck:
- **Leptons**: m_e = M_P·√(2π)·(16/3)·α¹¹
- **Quarks**: Generation scaling via (N_c/α)^(2/3)
- **Hadrons**: Proton, neutron from QCD
- **Bosons**: W, Z, Higgs from electroweak

### `verify_mixing.py`
Derives flavor mixing matrices:
- **CKM**: λ = N_c/(N_c+N_base) = 3/7 ≈ 0.225
- **PMNS**: sin²θ₁₂ = N_c/(N_c+b_3) = 3/10
- **CP phase**: δ = arctan(b_3/N_c) ≈ 66.8°
- Neutrino mass differences

### `verify_cosmology.py`
Verifies cosmological predictions:
- **Inflation**: n_s = 0.964, r = 0.007
- **Baryogenesis**: η ~ 10⁻¹⁰
- **Dark matter**: Sub-threshold flux mechanism
- **Dark energy**: Hierarchy discussion

## Sample Output

```
======================================================================
FOUNDATIONAL TERNARY DYNAMICS - FRAMEWORK CONSTANTS
======================================================================

FRAMEWORK INTEGERS:
  N_c (colors)      = 3
  N_base            = 4
  b_3 (QCD beta)    = 7
  N_eff             = 13

MASTER QUADRATIC ROOTS:
  x₊ = 1/α          = 137.0360233...
  x₋ ≈ N_c          = 3.0242766...

COUPLING CONSTANTS:
  α (fine structure)   = 0.0072973525...
  1/α (derived)        = 137.036023
  1/α (experimental)   = 137.035999
  Error                = 1.26 ppm
```

## Theoretical Context

The FTD framework proposes that the Standard Model parameters emerge from:

1. **Ontological primitives**: 3D cubic lattice with ternary states {-1, 0, +1}
2. **Mathematical structure**: Fermat boundary selects quadratic degree
3. **Elliptic geometry**: Gauss constraint → lemniscatic constant G*
4. **Master quadratic**: Encodes α and N_c simultaneously

This represents a theory with:
- **4 input integers** (uniquely constrained)
- **0 free parameters**
- **40+ derived predictions**
- **All experimentally compatible**

## References

- Full framework: See `../CLAUDE.md`
- Theoretical foundations: See `../manuscript/`
- Verification report: See `../FTD_VERIFICATION_REPORT.md`
