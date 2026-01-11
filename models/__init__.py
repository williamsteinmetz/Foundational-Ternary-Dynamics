"""
FTD Scientific Models Package

Comprehensive computational models implementing the Foundational Ternary Dynamics
framework for deriving Standard Model parameters from first principles.

Modules:
    ftd_core: Core framework constants and mathematical foundations
    particle_physics: Particle masses, couplings, and quantum numbers
    mixing_matrices: CKM and PMNS mixing matrix predictions
    cosmology: Inflation, baryogenesis, and dark matter models
    visualization: Derivation chain and parameter relationship visualizations
    fermat_coil: Complex Fermat spiral encoding the master quadratic
"""

from .ftd_core import FTDFramework
from .particle_physics import ParticlePhysicsModel
from .mixing_matrices import MixingMatrixModel
from .cosmology import CosmologyModel
from .fermat_coil import FermatCoil

__version__ = "1.0.0"
__author__ = "FTD Framework"
__all__ = [
    'FTDFramework',
    'ParticlePhysicsModel',
    'MixingMatrixModel',
    'CosmologyModel',
    'FermatCoil'
]
