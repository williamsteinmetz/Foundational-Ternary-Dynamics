#!/usr/bin/env python3
"""
Enhanced 3D Fermat Coil with Master Quadratic Encoding

Multiple 3D projection modes for visualizing the Fermat spiral
encoded with the master quadratic x² - 16G*²x + 16G*³ = 0.

Modes:
1. Helical Coil - z = quadratic value
2. Torus Mapping - spiral wrapped around a torus
3. Spherical Embedding - spiral on sphere with radial modulation
4. Double Helix - intertwined positive/negative branches

The visualization encodes:
- Framework integers {3, 4, 7, 13} as harmonic modulations
- Quadratic roots x₊ = 1/α ≈ 137, x₋ ≈ 3 (Nᶜ)
- Lemniscatic constant G* ≈ 2.9587
"""

import numpy as np
from scipy.special import gamma
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
import warnings

# Import visualization libraries
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    warnings.warn("Plotly not available. Install with: pip install plotly")

try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Import core framework
try:
    from .ftd_core import FTDFramework
except ImportError:
    try:
        from ftd_core import FTDFramework
    except ImportError:
        # Minimal inline implementation if ftd_core not available
        class FTDFramework:
            def __init__(self):
                self.lemniscatic = type('obj', (object,), {'value': np.sqrt(2) * gamma(0.25)**2 / (2 * np.pi)})()
                self.alpha = 1/137.036
                g = self.lemniscatic.value
                self.quadratic = type('obj', (object,), {
                    'x_plus': 8*g**2 + 8*g**2*np.sqrt(1 - 1/g),
                    'x_minus': 8*g**2 - 8*g**2*np.sqrt(1 - 1/g)
                })()
                self.integers = type('obj', (object,), {
                    'N_c': 3, 'N_base': 4, 'b_3': 7, 'N_eff': 13
                })()


class CoilMode(Enum):
    """Available 3D coil projection modes."""
    HELICAL = "helical"
    TORUS = "torus"
    SPHERICAL = "spherical"
    DOUBLE_HELIX = "double_helix"
    LEMNISCATE_3D = "lemniscate_3d"


@dataclass
class CoilParameters:
    """Parameters for the Fermat coil visualization."""
    n_turns: int = 137          # Number of turns (1/α)
    points_per_turn: int = 100  # Resolution
    g_star_scale: float = 1.0   # Scaling factor for G*
    harmonic_amplitude: float = 0.1  # Strength of integer harmonics
    torus_major_radius: float = 10.0  # For torus mode
    torus_minor_radius: float = 3.0   # For torus mode
    sphere_radius: float = 10.0       # For spherical mode
    helix_pitch: float = 1.0          # Vertical spacing for helical mode


class FermatCoil3D:
    """
    Enhanced 3D Fermat Coil with multiple projection modes.

    The Fermat spiral r = G*·√θ represents the geometric boundary
    at n=2 (last FLT-allowed exponent). The 3D encoding maps the
    master quadratic structure onto the vertical dimension.
    """

    def __init__(self, framework: Optional[FTDFramework] = None,
                 params: Optional[CoilParameters] = None):
        self.framework = framework or FTDFramework()
        self.params = params or CoilParameters()

        # Extract constants
        self.G_star = self.framework.lemniscatic.value
        self.alpha = self.framework.alpha
        self.x_plus = self.framework.quadratic.x_plus
        self.x_minus = self.framework.quadratic.x_minus

        # Framework integers
        self.N_c = self.framework.integers.N_c
        self.N_base = self.framework.integers.N_base
        self.b_3 = self.framework.integers.b_3
        self.N_eff = self.framework.integers.N_eff

        # Precompute base theta array
        self._init_theta()

    def _init_theta(self):
        """Initialize the base parameter array."""
        n = self.params.n_turns * self.params.points_per_turn
        self.theta = np.linspace(0, 2 * np.pi * self.params.n_turns, n)
        self.t_normalized = self.theta / self.theta.max()

    def _fermat_radius(self, theta: np.ndarray) -> np.ndarray:
        """Compute Fermat spiral radius: r = G*·√θ with harmonic modulation."""
        r_base = self.G_star * self.params.g_star_scale * np.sqrt(np.abs(theta))

        # Add framework integer harmonics
        amp = self.params.harmonic_amplitude
        modulation = (
            amp * np.sin(self.N_c * theta) +        # 3-fold (color)
            amp * 0.7 * np.sin(self.b_3 * theta) +  # 7-fold (beta)
            amp * 0.5 * np.sin(self.N_eff * theta)  # 13-fold (effective DoF)
        )

        return r_base * (1 + modulation)

    def _evaluate_quadratic(self, r: np.ndarray) -> np.ndarray:
        """Evaluate master quadratic at radius values."""
        # Normalize r to range around roots
        r_scaled = r / r.max() * (self.x_plus + 10)

        # Master quadratic: x² - 16G*²x + 16G*³
        a, b, c = 1, -16 * self.G_star**2, 16 * self.G_star**3
        return a * r_scaled**2 + b * r_scaled + c

    # =========================================================================
    # PROJECTION MODES
    # =========================================================================

    def helical_coil(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate helical coil where z = quadratic value.

        This is the canonical representation where the vertical axis
        directly encodes the master quadratic evaluated at each point.

        Returns: (x, y, z, quadratic_value)
        """
        r = self._fermat_radius(self.theta)
        x = r * np.cos(self.theta)
        y = r * np.sin(self.theta)

        # Z is the quadratic value, normalized
        quad_val = self._evaluate_quadratic(r)
        z = quad_val / np.abs(quad_val).max() * self.params.n_turns * self.params.helix_pitch

        return x, y, z, quad_val

    def torus_coil(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Map Fermat spiral onto a torus surface.

        The spiral wraps around the torus with:
        - Toroidal angle φ = θ (turns around the donut)
        - Poloidal angle ψ = θ·(N_c/N_eff) (turns around the tube)
        - Minor radius modulated by quadratic value

        Returns: (x, y, z, quadratic_value)
        """
        R = self.params.torus_major_radius
        r_base = self.params.torus_minor_radius

        # Toroidal and poloidal angles
        phi = self.theta  # Around the hole
        psi = self.theta * (self.N_c / self.N_eff) * 2  # Around the tube

        # Modulate minor radius with Fermat spiral growth and quadratic
        fermat_r = self._fermat_radius(self.theta)
        fermat_normalized = fermat_r / fermat_r.max()
        quad_val = self._evaluate_quadratic(fermat_r)
        quad_normalized = (quad_val - quad_val.min()) / (quad_val.max() - quad_val.min())

        # Minor radius varies with position
        r_minor = r_base * (0.5 + 0.5 * fermat_normalized) * (0.7 + 0.3 * quad_normalized)

        # Parametric torus equations
        x = (R + r_minor * np.cos(psi)) * np.cos(phi)
        y = (R + r_minor * np.cos(psi)) * np.sin(phi)
        z = r_minor * np.sin(psi)

        return x, y, z, quad_val

    def spherical_coil(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Project Fermat spiral onto a sphere with radial modulation.

        The spiral traces a path on the sphere where:
        - Polar angle θ_sphere = arccos(1 - 2t) (uniform coverage)
        - Azimuthal angle φ = θ (spiral winding)
        - Radius modulated by quadratic value

        Returns: (x, y, z, quadratic_value)
        """
        R = self.params.sphere_radius

        # Spherical angles for uniform coverage
        theta_sphere = np.arccos(1 - 2 * self.t_normalized)  # 0 to π
        phi = self.theta  # Azimuthal winding

        # Compute quadratic for color/modulation
        fermat_r = self._fermat_radius(self.theta)
        quad_val = self._evaluate_quadratic(fermat_r)
        quad_normalized = (quad_val - quad_val.min()) / (quad_val.max() - quad_val.min())

        # Modulate radius
        r_mod = R * (0.9 + 0.2 * quad_normalized)

        # Spherical to Cartesian
        x = r_mod * np.sin(theta_sphere) * np.cos(phi)
        y = r_mod * np.sin(theta_sphere) * np.sin(phi)
        z = r_mod * np.cos(theta_sphere)

        return x, y, z, quad_val

    def double_helix(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray,
                                     np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate double helix with positive and negative branches.

        Represents the duality between x₊ (matter/1/α) and x₋ (color/Nᶜ).
        The two helices are phase-shifted by π.

        Returns: (x1, y1, z1, x2, y2, z2, quad_val)
        """
        r = self._fermat_radius(self.theta)
        quad_val = self._evaluate_quadratic(r)
        z = quad_val / np.abs(quad_val).max() * self.params.n_turns * self.params.helix_pitch

        # First helix (positive branch)
        x1 = r * np.cos(self.theta)
        y1 = r * np.sin(self.theta)
        z1 = z

        # Second helix (negative branch, phase-shifted by π)
        x2 = r * np.cos(self.theta + np.pi)
        y2 = r * np.sin(self.theta + np.pi)
        z2 = -z  # Inverted z for duality

        return x1, y1, z1, x2, y2, z2, quad_val

    def lemniscate_3d(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate a 3D lemniscate (figure-8) that grows with Fermat dynamics.

        Combines:
        - Lemniscate of Bernoulli: r² = cos(2θ)
        - Fermat spiral growth
        - Quadratic z-encoding

        Returns: (x, y, z, quadratic_value)
        """
        # Lemniscate parameter
        t_lemn = self.theta * self.N_base  # 4-fold gives figure-8

        # Lemniscate of Bernoulli: r² = a² cos(2θ)
        # We use |cos| to keep positive and modulate with Fermat growth
        cos_2t = np.cos(2 * t_lemn / self.params.n_turns)
        lemn_factor = np.sqrt(np.maximum(0.1, np.abs(cos_2t)))

        # Combine with Fermat growth
        growth = self.G_star * self.params.g_star_scale * np.sqrt(np.abs(self.theta) + 1)
        r = growth * lemn_factor

        # Add harmonic modulation
        amp = self.params.harmonic_amplitude * 0.5
        modulation = 1 + amp * np.sin(self.N_c * self.theta) + amp * 0.5 * np.sin(self.b_3 * self.theta)
        r *= modulation

        x = r * np.cos(self.theta)
        y = r * np.sin(self.theta)

        # Z encodes the quadratic
        quad_val = self._evaluate_quadratic(r)
        z = quad_val / np.abs(quad_val).max() * self.params.n_turns * self.params.helix_pitch * 0.5

        return x, y, z, quad_val

    # =========================================================================
    # MARKER GENERATION
    # =========================================================================

    def get_root_markers(self, mode: CoilMode = CoilMode.HELICAL) -> List[Dict]:
        """Get marker positions for quadratic roots in the specified mode."""
        markers = []

        # Get coordinates based on mode
        if mode == CoilMode.HELICAL:
            x, y, z, qv = self.helical_coil()
        elif mode == CoilMode.TORUS:
            x, y, z, qv = self.torus_coil()
        elif mode == CoilMode.SPHERICAL:
            x, y, z, qv = self.spherical_coil()
        elif mode == CoilMode.LEMNISCATE_3D:
            x, y, z, qv = self.lemniscate_3d()
        else:
            x, y, z, qv = self.helical_coil()

        # x_plus marker (turn 137)
        idx_plus = int(137 * self.params.points_per_turn) if 137 < self.params.n_turns else -1
        if idx_plus < len(x):
            markers.append({
                'x': x[idx_plus], 'y': y[idx_plus], 'z': z[idx_plus],
                'label': f'x₊ = {self.x_plus:.4f}',
                'description': '1/α (fine structure)',
                'color': '#ff0000',
                'turn': 137
            })

        # x_minus marker (turn 3)
        idx_minus = int(3 * self.params.points_per_turn)
        markers.append({
            'x': x[idx_minus], 'y': y[idx_minus], 'z': z[idx_minus],
            'label': f'x₋ = {self.x_minus:.4f}',
            'description': 'Nᶜ (color charges)',
            'color': '#00ff00',
            'turn': 3
        })

        return markers

    def get_integer_markers(self, mode: CoilMode = CoilMode.HELICAL) -> List[Dict]:
        """Get marker positions for framework integers."""
        markers = []

        # Get coordinates based on mode
        if mode == CoilMode.HELICAL:
            x, y, z, qv = self.helical_coil()
        elif mode == CoilMode.TORUS:
            x, y, z, qv = self.torus_coil()
        elif mode == CoilMode.SPHERICAL:
            x, y, z, qv = self.spherical_coil()
        elif mode == CoilMode.LEMNISCATE_3D:
            x, y, z, qv = self.lemniscate_3d()
        else:
            x, y, z, qv = self.helical_coil()

        integers = [
            (self.N_c, 'Nᶜ = 3', 'Color charges', '#00ff88'),
            (self.N_base, 'Nbase = 4', 'Base dimension', '#0088ff'),
            (self.b_3, 'b₃ = 7', 'QCD beta function', '#ff00ff'),
            (self.N_eff, 'Neff = 13', 'Effective DoF (F₇)', '#ff8800'),
        ]

        for n, label, desc, color in integers:
            idx = int(n * self.params.points_per_turn)
            if idx < len(x):
                markers.append({
                    'x': x[idx], 'y': y[idx], 'z': z[idx],
                    'label': label,
                    'description': desc,
                    'color': color,
                    'turn': n
                })

        return markers

    # =========================================================================
    # PLOTLY VISUALIZATION
    # =========================================================================

    def plot_interactive(self, mode: CoilMode = CoilMode.HELICAL,
                         show_roots: bool = True,
                         show_integers: bool = True,
                         save_path: Optional[str] = None,
                         show: bool = True) -> 'go.Figure':
        """
        Create an interactive 3D visualization using Plotly.

        Args:
            mode: Projection mode (HELICAL, TORUS, SPHERICAL, etc.)
            show_roots: Whether to mark quadratic roots
            show_integers: Whether to mark framework integers
            save_path: Optional path to save as HTML
            show: Whether to display in browser

        Returns:
            Plotly figure object
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required. Install with: pip install plotly")

        # Generate coil data based on mode
        if mode == CoilMode.HELICAL:
            x, y, z, qv = self.helical_coil()
            title_mode = "Helical Coil"
        elif mode == CoilMode.TORUS:
            x, y, z, qv = self.torus_coil()
            title_mode = "Torus Mapping"
        elif mode == CoilMode.SPHERICAL:
            x, y, z, qv = self.spherical_coil()
            title_mode = "Spherical Embedding"
        elif mode == CoilMode.DOUBLE_HELIX:
            x1, y1, z1, x2, y2, z2, qv = self.double_helix()
            x, y, z = x1, y1, z1  # Use first helix for markers
            title_mode = "Double Helix"
        elif mode == CoilMode.LEMNISCATE_3D:
            x, y, z, qv = self.lemniscate_3d()
            title_mode = "3D Lemniscate"
        else:
            x, y, z, qv = self.helical_coil()
            title_mode = "Helical Coil"

        # Normalize quadratic for coloring
        qv_norm = (qv - qv.min()) / (qv.max() - qv.min())

        # Create hover text
        turn_num = self.theta / (2 * np.pi)
        hover_text = [
            f"<b>Turn:</b> {t:.2f}<br>"
            f"<b>Radius:</b> {np.sqrt(xi**2 + yi**2):.3f}<br>"
            f"<b>Quadratic:</b> {q:.2f}<br>"
            f"<b>Position:</b> ({xi:.2f}, {yi:.2f}, {zi:.2f})"
            for xi, yi, zi, t, q in zip(x, y, z, turn_num, qv)
        ]

        traces = []

        # Main coil trace
        if mode == CoilMode.DOUBLE_HELIX:
            # Two helices
            traces.append(go.Scatter3d(
                x=x1, y=y1, z=z1,
                mode='lines',
                line=dict(color=qv, colorscale='Plasma', width=4),
                name='Positive Branch (x₊)',
                text=hover_text,
                hoverinfo='text'
            ))
            traces.append(go.Scatter3d(
                x=x2, y=y2, z=z2,
                mode='lines',
                line=dict(color=qv, colorscale='Viridis', width=4),
                name='Negative Branch (x₋)',
                hoverinfo='text'
            ))
        else:
            traces.append(go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines',
                line=dict(
                    color=qv,
                    colorscale='Plasma',
                    width=4,
                    colorbar=dict(
                        title='Quadratic<br>x² - 16G*²x + 16G*³',
                        thickness=20,
                        len=0.7
                    )
                ),
                text=hover_text,
                hoverinfo='text',
                name='Fermat Coil'
            ))

        # Add root markers
        if show_roots:
            for marker in self.get_root_markers(mode):
                traces.append(go.Scatter3d(
                    x=[marker['x']], y=[marker['y']], z=[marker['z']],
                    mode='markers+text',
                    marker=dict(size=12, color=marker['color'], symbol='circle'),
                    text=[marker['label']],
                    textposition='top center',
                    textfont=dict(size=12, color=marker['color']),
                    hovertext=f"<b>{marker['label']}</b><br>{marker['description']}<br>Turn {marker['turn']}",
                    hoverinfo='text',
                    name=marker['label']
                ))

        # Add integer markers
        if show_integers:
            for marker in self.get_integer_markers(mode):
                traces.append(go.Scatter3d(
                    x=[marker['x']], y=[marker['y']], z=[marker['z']],
                    mode='markers+text',
                    marker=dict(size=10, color=marker['color'], symbol='diamond'),
                    text=[marker['label']],
                    textposition='top center',
                    textfont=dict(size=10, color=marker['color']),
                    hovertext=f"<b>{marker['label']}</b><br>{marker['description']}<br>Turn {marker['turn']}",
                    hoverinfo='text',
                    name=marker['label']
                ))

        # Create figure
        fig = go.Figure(data=traces)

        # Update layout
        fig.update_layout(
            title=dict(
                text=(
                    f"<b>3D Fermat Coil — {title_mode}</b><br>"
                    f"<sup>Master Quadratic: x² - 16G*²x + 16G*³ = 0 | "
                    f"G* = {self.G_star:.6f} | "
                    f"x₊ = {self.x_plus:.4f} | x₋ = {self.x_minus:.4f}</sup>"
                ),
                x=0.5,
                font=dict(size=16)
            ),
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z (Quadratic)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.0),
                    up=dict(x=0, y=0, z=1)
                ),
                aspectmode='data'
            ),
            showlegend=True,
            legend=dict(
                yanchor="top", y=0.99,
                xanchor="left", x=0.01,
                bgcolor="rgba(255,255,255,0.8)"
            ),
            margin=dict(l=0, r=0, t=100, b=0),
            annotations=[
                dict(
                    text=(
                        f"<b>Framework Integers:</b> {{3, 4, 7, 13}}<br>"
                        f"<b>Turns:</b> {self.params.n_turns}<br>"
                        f"<b>Mode:</b> {title_mode}"
                    ),
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.02, y=0.02,
                    align="left",
                    font=dict(size=11),
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="gray",
                    borderwidth=1
                )
            ]
        )

        # Add view control buttons
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=[
                        dict(args=[{"scene.camera.eye": {"x": 1.5, "y": 1.5, "z": 1.0}}],
                             label="Default", method="relayout"),
                        dict(args=[{"scene.camera.eye": {"x": 0, "y": 0, "z": 2.5}}],
                             label="Top", method="relayout"),
                        dict(args=[{"scene.camera.eye": {"x": 2.5, "y": 0, "z": 0}}],
                             label="Side", method="relayout"),
                        dict(args=[{"scene.camera.eye": {"x": 0.5, "y": 0.5, "z": 2.0}}],
                             label="Angled", method="relayout"),
                    ],
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.5, xanchor="center",
                    y=1.12, yanchor="top"
                )
            ]
        )

        if save_path:
            fig.write_html(save_path, include_plotlyjs=True, full_html=True)
            print(f"Saved interactive visualization to: {save_path}")

        if show:
            fig.show()

        return fig

    def plot_all_modes(self, save_dir: Optional[str] = None, show: bool = True) -> Dict[str, 'go.Figure']:
        """
        Generate visualizations for all projection modes.

        Args:
            save_dir: Directory to save HTML files
            show: Whether to display each visualization

        Returns:
            Dictionary of {mode_name: figure}
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required. Install with: pip install plotly")

        figures = {}
        modes = [CoilMode.HELICAL, CoilMode.TORUS, CoilMode.SPHERICAL,
                 CoilMode.DOUBLE_HELIX, CoilMode.LEMNISCATE_3D]

        for mode in modes:
            save_path = None
            if save_dir:
                import os
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"fermat_coil_3d_{mode.value}.html")

            fig = self.plot_interactive(mode=mode, save_path=save_path, show=show)
            figures[mode.value] = fig

        return figures

    def plot_comparison(self, save_path: Optional[str] = None, show: bool = True) -> 'go.Figure':
        """
        Create a 2x2 subplot comparing different projection modes.
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required. Install with: pip install plotly")

        # Use lower resolution for subplot
        original_ppt = self.params.points_per_turn
        self.params.points_per_turn = 30
        self._init_theta()

        # Generate data for each mode
        x_h, y_h, z_h, qv_h = self.helical_coil()
        x_t, y_t, z_t, qv_t = self.torus_coil()
        x_s, y_s, z_s, qv_s = self.spherical_coil()
        x_l, y_l, z_l, qv_l = self.lemniscate_3d()

        # Restore resolution
        self.params.points_per_turn = original_ppt
        self._init_theta()

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'scene'}, {'type': 'scene'}],
                   [{'type': 'scene'}, {'type': 'scene'}]],
            subplot_titles=('Helical Coil', 'Torus Mapping',
                          'Spherical Embedding', '3D Lemniscate'),
            horizontal_spacing=0.05,
            vertical_spacing=0.1
        )

        # Add traces
        fig.add_trace(go.Scatter3d(
            x=x_h, y=y_h, z=z_h, mode='lines',
            line=dict(color=qv_h, colorscale='Plasma', width=3),
            showlegend=False
        ), row=1, col=1)

        fig.add_trace(go.Scatter3d(
            x=x_t, y=y_t, z=z_t, mode='lines',
            line=dict(color=qv_t, colorscale='Viridis', width=3),
            showlegend=False
        ), row=1, col=2)

        fig.add_trace(go.Scatter3d(
            x=x_s, y=y_s, z=z_s, mode='lines',
            line=dict(color=qv_s, colorscale='Cividis', width=3),
            showlegend=False
        ), row=2, col=1)

        fig.add_trace(go.Scatter3d(
            x=x_l, y=y_l, z=z_l, mode='lines',
            line=dict(color=qv_l, colorscale='Inferno', width=3),
            showlegend=False
        ), row=2, col=2)

        # Update layout
        fig.update_layout(
            title=dict(
                text=(
                    f"<b>3D Fermat Coil — Mode Comparison</b><br>"
                    f"<sup>G* = {self.G_star:.6f} | "
                    f"x₊ = {self.x_plus:.4f} (1/α) | "
                    f"x₋ = {self.x_minus:.4f} (Nᶜ)</sup>"
                ),
                x=0.5
            ),
            height=900,
            margin=dict(l=0, r=0, t=100, b=0)
        )

        if save_path:
            fig.write_html(save_path, include_plotlyjs=True, full_html=True)
            print(f"Saved comparison to: {save_path}")

        if show:
            fig.show()

        return fig

    # =========================================================================
    # TEXT OUTPUT
    # =========================================================================

    def summary(self) -> str:
        """Generate text summary of the coil parameters."""
        return f"""
================================================================================
3D FERMAT COIL WITH MASTER QUADRATIC ENCODING
================================================================================

FERMAT SPIRAL: r = G*·√θ
------------------------
The Fermat spiral (n=2) represents the last FLT-allowed exponent.
This geometric boundary generates the framework integers.

LEMNISCATIC CONSTANT:
  G* = √2 · Γ(1/4)² / (2π) = {self.G_star:.10f}

MASTER QUADRATIC: x² - 16G*²x + 16G*³ = 0
-----------------------------------------
Roots:
  x₊ = {self.x_plus:.10f} = 1/α (fine structure)
  x₋ = {self.x_minus:.10f} ≈ Nᶜ = 3 (color charges)

FRAMEWORK INTEGERS (encoded as harmonics):
  Nᶜ    = {self.N_c}   (color charges)
  Nbase = {self.N_base}   (base dimension)
  b₃    = {self.b_3}   (QCD beta function)
  Neff  = {self.N_eff}  (effective DoF = F₇)

PROJECTION MODES:
  - HELICAL:    z = quadratic value (canonical)
  - TORUS:      spiral mapped to torus surface
  - SPHERICAL:  spiral on sphere with radial modulation
  - DOUBLE_HELIX: intertwined x₊/x₋ branches
  - LEMNISCATE_3D: figure-8 with Fermat growth

VISUALIZATION PARAMETERS:
  Turns: {self.params.n_turns}
  Points/turn: {self.params.points_per_turn}
  Harmonic amplitude: {self.params.harmonic_amplitude}

================================================================================
"""


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================

def main():
    """Main entry point for command-line usage."""
    import sys

    coil = FermatCoil3D()

    if len(sys.argv) < 2:
        print(coil.summary())
        if PLOTLY_AVAILABLE:
            print("\nLaunching interactive helical coil visualization...")
            coil.plot_interactive(mode=CoilMode.HELICAL)
        return

    arg = sys.argv[1].lower()

    if arg == "--help" or arg == "-h":
        print("""
Usage: python fermat_coil_3d.py [OPTIONS]

Options:
  --helical      Show helical coil (default)
  --torus        Show torus mapping
  --spherical    Show spherical embedding
  --double       Show double helix
  --lemniscate   Show 3D lemniscate
  --comparison   Show all modes in 2x2 grid
  --all          Generate all modes as separate HTML files
  --text         Print text summary only
  --help, -h     Show this help message
""")
    elif arg == "--text":
        print(coil.summary())
    elif arg == "--helical":
        coil.plot_interactive(mode=CoilMode.HELICAL)
    elif arg == "--torus":
        coil.plot_interactive(mode=CoilMode.TORUS)
    elif arg == "--spherical":
        coil.plot_interactive(mode=CoilMode.SPHERICAL)
    elif arg == "--double":
        coil.plot_interactive(mode=CoilMode.DOUBLE_HELIX)
    elif arg == "--lemniscate":
        coil.plot_interactive(mode=CoilMode.LEMNISCATE_3D)
    elif arg == "--comparison":
        coil.plot_comparison(save_path="fermat_coil_3d_comparison.html")
    elif arg == "--all":
        coil.plot_all_modes(save_dir="figures", show=False)
        print("All visualizations saved to figures/")
    else:
        print(f"Unknown option: {arg}")
        print("Use --help for usage information.")


if __name__ == "__main__":
    main()
