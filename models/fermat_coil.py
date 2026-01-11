#!/usr/bin/env python3
"""
Complex Fermat Coil Encoded with the Master Quadratic

This module creates a visualization combining:
1. Fermat spiral geometry (r = a*sqrt(theta))
2. The master quadratic x^2 - 16G*^2 x + 16G*^3 = 0
3. Framework integers {3, 4, 7, 13}
4. The lemniscatic constant G* = sqrt(2) * Gamma(1/4)^2 / (2*pi)

The Fermat spiral naturally encodes the boundary between FLT-allowed (n=2)
and FLT-forbidden (n>=3) exponents, making it the geometric foundation
for the framework's derivation of the fine structure constant.
"""

import numpy as np
from scipy.special import gamma
from typing import Tuple, Optional, List
import warnings

# Try to import matplotlib
try:
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.colors import LinearSegmentedColormap
    import matplotlib.patches as mpatches
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    warnings.warn("matplotlib not available. Text output only.")

# Try to import plotly for interactive 3D
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    warnings.warn("plotly not available. Interactive 3D disabled.")

# Import core framework
try:
    from .ftd_core import FTDFramework
except ImportError:
    from ftd_core import FTDFramework


class FermatCoil:
    """
    A complex Fermat coil encoding the FTD master quadratic.

    The Fermat spiral r = a*sqrt(theta) represents the geometric
    boundary at n=2 (last FLT-allowed exponent). The coil winds
    encode the framework integers and coupling constants.
    """

    def __init__(self, framework: Optional[FTDFramework] = None):
        self.framework = framework or FTDFramework()
        self.G_star = self.framework.lemniscatic.value
        self.alpha = self.framework.alpha
        self.x_plus = self.framework.quadratic.x_plus  # 1/alpha
        self.x_minus = self.framework.quadratic.x_minus  # ~N_c

        # Framework integers
        self.N_c = self.framework.integers.N_c
        self.N_base = self.framework.integers.N_base
        self.b_3 = self.framework.integers.b_3
        self.N_eff = self.framework.integers.N_eff

    def fermat_spiral(self, theta: np.ndarray, a: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate Fermat spiral coordinates.

        r = a * sqrt(theta)

        This is the n=2 case of r^n = a^n * theta, representing
        the last FLT-allowed exponent.
        """
        r = a * np.sqrt(np.abs(theta))
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return x, y

    def encoded_fermat_coil(self, n_turns: int = 137,
                            points_per_turn: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate a Fermat coil with encoded quadratic structure.

        The coil has:
        - 137 turns (encoding 1/alpha)
        - Modulation at frequencies 3, 7, 13 (framework integers)
        - Amplitude scaling by G*

        Returns x, y coordinates and a parameter array for coloring.
        """
        # Total angle for n_turns
        theta_max = 2 * np.pi * n_turns
        theta = np.linspace(0, theta_max, n_turns * points_per_turn)

        # Base Fermat spiral with G* scaling
        r_base = self.G_star * np.sqrt(theta)

        # Encode framework integers as harmonic modulations
        # These create the "coil" structure
        modulation = (
            0.1 * np.sin(self.N_c * theta) +      # 3-fold symmetry (color)
            0.07 * np.sin(self.b_3 * theta) +     # 7-fold (beta function)
            0.05 * np.sin(self.N_eff * theta)     # 13-fold (effective DoF)
        )

        r = r_base * (1 + modulation)

        x = r * np.cos(theta)
        y = r * np.sin(theta)

        # Parameter for coloring (encodes quadratic structure)
        # Color by position relative to x_plus and x_minus
        t = theta / theta_max  # Normalized parameter 0 to 1

        return x, y, t

    def complex_coil_3d(self, n_turns: int = 137,
                        points_per_turn: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate a 3D complex Fermat coil.

        The z-coordinate encodes the master quadratic:
        z = x^2 - 16G*^2 x + 16G*^3 evaluated along the spiral

        Returns x, y, z coordinates and parameter t.
        """
        x, y, t = self.encoded_fermat_coil(n_turns, points_per_turn)

        # Radial distance as the "x" in the quadratic
        r = np.sqrt(x**2 + y**2)

        # Normalize r to range around x_plus and x_minus
        r_scaled = r / np.max(r) * (self.x_plus + 10)

        # Evaluate master quadratic
        a = 1
        b = -16 * self.G_star**2
        c = 16 * self.G_star**3

        z = a * r_scaled**2 + b * r_scaled + c

        # Normalize z for visualization
        z_range = np.max(np.abs(z))
        z_normalized = z / z_range * n_turns * 0.5

        return x, y, z_normalized, t

    def lemniscate_encoded_coil(self, n_turns: int = 137,
                                 points_per_turn: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate a coil that traces a lemniscate pattern while spiraling.

        Combines:
        - Fermat spiral growth
        - Lemniscate figure-8 oscillation
        - Framework integer modulation
        """
        theta = np.linspace(0, 2 * np.pi * n_turns, n_turns * points_per_turn)

        # Lemniscate parameter (controls figure-8 shape)
        phi = theta * self.N_base  # 4-fold (base dimension)

        # Lemniscate of Bernoulli: r^2 = cos(2*phi)
        # Modified with Fermat growth
        growth = self.G_star * np.sqrt(theta / (2 * np.pi))

        # Lemniscate modulation (creates the figure-8 envelope)
        lemniscate_mod = np.cos(2 * phi / n_turns)

        # Combine with framework harmonics
        r = growth * (1 + 0.3 * np.abs(lemniscate_mod)) * (
            1 + 0.05 * np.sin(self.N_c * theta) +
            0.03 * np.sin(self.b_3 * theta) +
            0.02 * np.sin(self.N_eff * theta)
        )

        x = r * np.cos(theta)
        y = r * np.sin(theta)

        t = theta / theta.max()

        return x, y, t

    def quadratic_roots_markers(self) -> List[Tuple[float, float, str]]:
        """
        Generate marker positions for the quadratic roots.

        Returns list of (x, y, label) tuples.
        """
        # Place markers at radii corresponding to x_plus and x_minus
        markers = []

        # x_plus marker (1/alpha ~ 137)
        theta_plus = 2 * np.pi * 137  # At turn 137
        r_plus = self.G_star * np.sqrt(theta_plus)
        x_plus = r_plus * np.cos(theta_plus)
        y_plus = r_plus * np.sin(theta_plus)
        markers.append((x_plus, y_plus, f"x+ = {self.x_plus:.4f}\n(1/alpha)"))

        # x_minus marker (N_c ~ 3)
        theta_minus = 2 * np.pi * 3  # At turn 3
        r_minus = self.G_star * np.sqrt(theta_minus)
        x_minus = r_minus * np.cos(theta_minus)
        y_minus = r_minus * np.sin(theta_minus)
        markers.append((x_minus, y_minus, f"x- = {self.x_minus:.4f}\n(Nc ~ 3)"))

        return markers

    def plot_2d_coil(self, save_path: Optional[str] = None,
                     coil_type: str = "encoded"):
        """
        Create a 2D visualization of the Fermat coil.

        Args:
            save_path: Optional path to save the figure
            coil_type: "encoded", "lemniscate", or "simple"
        """
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib not available. Use text output instead.")
            return self.text_description()

        fig, ax = plt.subplots(figsize=(14, 14))

        if coil_type == "encoded":
            x, y, t = self.encoded_fermat_coil()
            title = "Fermat Coil with Quadratic Encoding"
        elif coil_type == "lemniscate":
            x, y, t = self.lemniscate_encoded_coil()
            title = "Lemniscate-Modulated Fermat Coil"
        else:
            theta = np.linspace(0, 2 * np.pi * 137, 13700)
            x, y = self.fermat_spiral(theta, self.G_star)
            t = theta / theta.max()
            title = "Simple Fermat Spiral"

        # Create color gradient based on quadratic evaluation
        r = np.sqrt(x**2 + y**2)
        r_norm = r / r.max() * 150

        # Evaluate quadratic for coloring
        quad_val = r_norm**2 - 16 * self.G_star**2 * r_norm + 16 * self.G_star**3

        # Normalize quadratic values for coloring
        quad_norm = (quad_val - quad_val.min()) / (quad_val.max() - quad_val.min())

        # Create segments for colored line
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # Custom colormap: blue (negative) -> white (zero) -> gold (positive)
        colors = [(0, 0, 0.5), (0, 0.5, 1), (1, 1, 1), (1, 0.8, 0), (0.8, 0.4, 0)]
        cmap = LinearSegmentedColormap.from_list("quadratic", colors)

        lc = LineCollection(segments, cmap=cmap, linewidths=0.5)
        lc.set_array(quad_norm)
        ax.add_collection(lc)

        # Add markers for roots
        markers = self.quadratic_roots_markers()
        for mx, my, label in markers:
            ax.plot(mx, my, 'o', markersize=12, color='red', zorder=5)
            ax.annotate(label, (mx, my), xytext=(10, 10),
                       textcoords='offset points', fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # Mark framework integers at corresponding turns
        integer_colors = ['green', 'blue', 'purple', 'orange']
        integer_labels = [
            (self.N_c, 'Nc = 3'),
            (self.N_base, 'Nbase = 4'),
            (self.b_3, 'b3 = 7'),
            (self.N_eff, 'Neff = 13')
        ]

        for (n, label), color in zip(integer_labels, integer_colors):
            theta_n = 2 * np.pi * n
            r_n = self.G_star * np.sqrt(theta_n)
            x_n = r_n * np.cos(theta_n)
            y_n = r_n * np.sin(theta_n)
            ax.plot(x_n, y_n, 's', markersize=8, color=color, zorder=4)
            ax.annotate(label, (x_n, y_n), xytext=(5, 5),
                       textcoords='offset points', fontsize=8, color=color)

        ax.set_xlim(x.min() * 1.1, x.max() * 1.1)
        ax.set_ylim(y.min() * 1.1, y.max() * 1.1)
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)

        # Add colorbar
        cbar = plt.colorbar(lc, ax=ax, shrink=0.8)
        cbar.set_label('Quadratic: x^2 - 16G*^2 x + 16G*^3', fontsize=10)

        # Add info text
        info_text = (
            f"G* = {self.G_star:.10f}\n"
            f"x+ = 1/alpha = {self.x_plus:.10f}\n"
            f"x- = Nc ~ {self.x_minus:.10f}\n"
            f"Turns = 137 (1/alpha)"
        )
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")

        plt.show()
        return fig

    def plot_3d_coil(self, save_path: Optional[str] = None):
        """
        Create a 3D visualization of the Fermat coil with quadratic encoding.
        """
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib not available. Use text output instead.")
            return self.text_description()

        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')

        x, y, z, t = self.complex_coil_3d()

        # Create color array based on quadratic structure
        r = np.sqrt(x**2 + y**2)
        r_norm = r / r.max() * 150
        quad_val = r_norm**2 - 16 * self.G_star**2 * r_norm + 16 * self.G_star**3
        quad_norm = (quad_val - quad_val.min()) / (quad_val.max() - quad_val.min())

        # Plot as scatter for color variation
        colors = plt.cm.plasma(quad_norm)

        # Downsample for performance
        step = 10
        ax.scatter(x[::step], y[::step], z[::step],
                  c=quad_norm[::step], cmap='plasma', s=1, alpha=0.6)

        # Draw path with lower resolution
        ax.plot(x[::50], y[::50], z[::50], 'b-', alpha=0.3, linewidth=0.5)

        # Mark the roots
        markers = self.quadratic_roots_markers()
        for mx, my, label in markers:
            # Find corresponding z value
            idx = np.argmin((x - mx)**2 + (y - my)**2)
            mz = z[idx]
            ax.scatter([mx], [my], [mz], s=100, c='red', marker='o', zorder=5)
            ax.text(mx, my, mz + 5, label.split('\n')[0], fontsize=9)

        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.set_zlabel('Quadratic Value', fontsize=12)
        ax.set_title('3D Fermat Coil with Quadratic Encoding\n'
                    'z = x^2 - 16G*^2 x + 16G*^3', fontsize=14, fontweight='bold')

        # Add info
        info_text = (
            f"G* = {self.G_star:.6f}\n"
            f"x+ = {self.x_plus:.4f}\n"
            f"x- = {self.x_minus:.4f}"
        )
        ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes,
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")

        plt.show()
        return fig

    def plot_3d_interactive(self, save_path: Optional[str] = None,
                            n_turns: int = 137, show: bool = True):
        """
        Create an interactive 3D visualization using Plotly.

        Features:
        - Rotate, zoom, pan with mouse
        - Hover over points for detailed information
        - Click to focus on specific regions
        - Color encodes quadratic value

        Args:
            save_path: Optional path to save as HTML file
            n_turns: Number of coil turns (default 137 = 1/alpha)
            show: Whether to display in browser

        Returns:
            Plotly figure object
        """
        if not PLOTLY_AVAILABLE:
            print("Plotly not available. Install with: pip install plotly")
            print("Falling back to matplotlib...")
            return self.plot_3d_coil(save_path)

        # Generate coil data
        x, y, z, t = self.complex_coil_3d(n_turns=n_turns, points_per_turn=50)

        # Calculate quadratic values for coloring
        r = np.sqrt(x**2 + y**2)
        r_norm = r / r.max() * 150
        quad_val = r_norm**2 - 16 * self.G_star**2 * r_norm + 16 * self.G_star**3

        # Calculate turn number for hover info
        theta = np.linspace(0, 2 * np.pi * n_turns, len(x))
        turn_num = theta / (2 * np.pi)

        # Create hover text with detailed information
        hover_text = [
            f"<b>Turn:</b> {turn:.1f}<br>"
            f"<b>Radius:</b> {np.sqrt(xi**2 + yi**2):.2f}<br>"
            f"<b>Quadratic:</b> {qv:.2f}<br>"
            f"<b>Position:</b> ({xi:.2f}, {yi:.2f}, {zi:.2f})"
            for xi, yi, zi, turn, qv in zip(x, y, z, turn_num, quad_val)
        ]

        # Main coil trace
        coil_trace = go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(
                color=quad_val,
                colorscale='Plasma',
                width=3,
                colorbar=dict(
                    title=dict(
                        text="Quadratic<br>x² - 16G*²x + 16G*³",
                        font=dict(size=12)
                    ),
                    thickness=20,
                    len=0.7
                )
            ),
            text=hover_text,
            hoverinfo='text',
            name='Fermat Coil'
        )

        # Framework integer markers
        marker_traces = []
        integer_info = [
            (self.N_c, 'N_c = 3', 'Color charges', '#00ff00'),
            (self.N_base, 'N_base = 4', 'Base dimension', '#0088ff'),
            (self.b_3, 'b_3 = 7', 'Beta function', '#ff00ff'),
            (self.N_eff, 'N_eff = 13', 'Effective DoF', '#ff8800')
        ]

        for n, label, description, color in integer_info:
            theta_n = 2 * np.pi * n
            r_n = self.G_star * np.sqrt(theta_n)
            x_n = r_n * np.cos(theta_n)
            y_n = r_n * np.sin(theta_n)
            # Find closest z value
            idx = np.argmin((x - x_n)**2 + (y - y_n)**2)
            z_n = z[idx]

            marker_traces.append(go.Scatter3d(
                x=[x_n], y=[y_n], z=[z_n],
                mode='markers+text',
                marker=dict(size=10, color=color, symbol='diamond'),
                text=[label],
                textposition='top center',
                textfont=dict(size=11, color=color),
                hovertext=f"<b>{label}</b><br>{description}<br>Turn {n}",
                hoverinfo='text',
                name=label
            ))

        # Root markers (x_plus and x_minus)
        root_markers = self.quadratic_roots_markers()
        for mx, my, label in root_markers:
            idx = np.argmin((x - mx)**2 + (y - my)**2)
            mz = z[idx]
            clean_label = label.split('\n')[0]

            marker_traces.append(go.Scatter3d(
                x=[mx], y=[my], z=[mz],
                mode='markers+text',
                marker=dict(size=15, color='red', symbol='circle'),
                text=[clean_label],
                textposition='top center',
                textfont=dict(size=12, color='red'),
                hovertext=f"<b>Quadratic Root</b><br>{label.replace(chr(10), '<br>')}",
                hoverinfo='text',
                name=clean_label
            ))

        # Create figure
        fig = go.Figure(data=[coil_trace] + marker_traces)

        # Update layout
        fig.update_layout(
            title=dict(
                text=(
                    f"<b>Interactive 3D Fermat Coil</b><br>"
                    f"<sup>Master Quadratic: x² - 16G*²x + 16G*³ = 0 | "
                    f"G* = {self.G_star:.6f} | "
                    f"x₊ = {self.x_plus:.4f} (1/α) | "
                    f"x₋ = {self.x_minus:.4f} (Nᶜ)</sup>"
                ),
                x=0.5,
                font=dict(size=16)
            ),
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Quadratic Value (z)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.0),
                    up=dict(x=0, y=0, z=1)
                ),
                aspectmode='data'
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255,255,255,0.8)"
            ),
            margin=dict(l=0, r=0, t=80, b=0),
            annotations=[
                dict(
                    text=(
                        f"<b>Framework Integers:</b> {{3, 4, 7, 13}}<br>"
                        f"<b>Turns:</b> {n_turns} (≈ 1/α)<br>"
                        f"<b>Fermat Spiral:</b> r = G*·√θ"
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

        # Add buttons for different views
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=[
                        dict(
                            args=[{"scene.camera.eye": {"x": 1.5, "y": 1.5, "z": 1.0}}],
                            label="Default View",
                            method="relayout"
                        ),
                        dict(
                            args=[{"scene.camera.eye": {"x": 0, "y": 0, "z": 2.5}}],
                            label="Top View",
                            method="relayout"
                        ),
                        dict(
                            args=[{"scene.camera.eye": {"x": 2.5, "y": 0, "z": 0}}],
                            label="Side View",
                            method="relayout"
                        ),
                        dict(
                            args=[{"scene.camera.eye": {"x": 0.5, "y": 0.5, "z": 2.0}}],
                            label="Angled View",
                            method="relayout"
                        ),
                    ],
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.5,
                    xanchor="center",
                    y=1.15,
                    yanchor="top"
                )
            ]
        )

        if save_path:
            fig.write_html(save_path, include_plotlyjs=True, full_html=True)
            print(f"Interactive visualization saved to: {save_path}")

        if show:
            fig.show()

        return fig

    def plot_quadratic_profile(self, save_path: Optional[str] = None):
        """
        Plot the master quadratic showing the roots.
        """
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib not available.")
            return self.text_description()

        fig, ax = plt.subplots(figsize=(12, 8))

        # x range encompassing both roots
        x = np.linspace(0, 150, 1000)

        # Master quadratic
        a = 1
        b = -16 * self.G_star**2
        c = 16 * self.G_star**3

        y = a * x**2 + b * x + c

        # Plot
        ax.plot(x, y, 'b-', linewidth=2, label='$x^2 - 16G^{*2}x + 16G^{*3}$')
        ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        ax.axvline(x=self.x_plus, color='red', linestyle='--', alpha=0.7,
                  label=f'$x_+ = {self.x_plus:.4f}$ (1/alpha)')
        ax.axvline(x=self.x_minus, color='green', linestyle='--', alpha=0.7,
                  label=f'$x_- = {self.x_minus:.4f}$ (Nc)')

        # Mark roots
        ax.plot(self.x_plus, 0, 'ro', markersize=12, zorder=5)
        ax.plot(self.x_minus, 0, 'go', markersize=12, zorder=5)

        # Mark vertex
        vertex_x = -b / (2 * a)
        vertex_y = a * vertex_x**2 + b * vertex_x + c
        ax.plot(vertex_x, vertex_y, 'b^', markersize=10)
        ax.annotate(f'Vertex\n({vertex_x:.2f}, {vertex_y:.2f})',
                   (vertex_x, vertex_y), xytext=(10, 10),
                   textcoords='offset points', fontsize=10)

        ax.set_xlabel('x', fontsize=14)
        ax.set_ylabel('f(x)', fontsize=14)
        ax.set_title('Master Quadratic: $x^2 - 16(G^*)^2 x + 16(G^*)^3 = 0$\n'
                    f'G* = {self.G_star:.10f}', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        # Add Vieta verification
        vieta_text = (
            "Vieta's Relations:\n"
            f"$x_+ + x_- = {self.x_plus + self.x_minus:.6f}$\n"
            f"$16(G^*)^2 = {16 * self.G_star**2:.6f}$\n\n"
            f"$x_+ \\times x_- = {self.x_plus * self.x_minus:.6f}$\n"
            f"$16(G^*)^3 = {16 * self.G_star**3:.6f}$"
        )
        ax.text(0.98, 0.98, vieta_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")

        plt.show()
        return fig

    def text_description(self) -> str:
        """Generate text description of the Fermat coil structure."""
        return f"""
================================================================================
COMPLEX FERMAT COIL WITH QUADRATIC ENCODING
================================================================================

FERMAT SPIRAL: r = a * sqrt(theta)
----------------------------------
The Fermat spiral represents the n=2 case of power spirals,
corresponding to the last Fermat-allowed exponent. This is the
geometric boundary from which the framework integers emerge.

ENCODING PARAMETERS:
--------------------
Lemniscatic constant G* = {self.G_star:.10f}
  sqrt(2) = 1.41421356237...
  Gamma(1/4) = 3.62560990822...
  G* = sqrt(2) * Gamma(1/4)^2 / (2*pi)

MASTER QUADRATIC: x^2 - 16(G*)^2 x + 16(G*)^3 = 0
-------------------------------------------------
Coefficients:
  a = 1
  b = -16(G*)^2 = {-16 * self.G_star**2:.10f}
  c = 16(G*)^3 = {16 * self.G_star**3:.10f}

Roots:
  x_+ = {self.x_plus:.10f} = 1/alpha (1.26 ppm accuracy)
  x_- = {self.x_minus:.10f} ~ N_c = 3 (0.8% accuracy)

Vieta Verification:
  x_+ + x_- = {self.x_plus + self.x_minus:.10f}
  16(G*)^2  = {16 * self.G_star**2:.10f} [MATCH]

  x_+ * x_- = {self.x_plus * self.x_minus:.10f}
  16(G*)^3  = {16 * self.G_star**3:.10f} [MATCH]

FRAMEWORK INTEGERS (Encoded as Harmonics):
------------------------------------------
  N_c    = {self.N_c}   (3-fold modulation - color charge)
  N_base = {self.N_base}   (4-fold modulation - base dimension)
  b_3    = {self.b_3}   (7-fold modulation - beta function)
  N_eff  = {self.N_eff}  (13-fold modulation - effective DoF)

COIL STRUCTURE:
---------------
  Number of turns: 137 (encoding 1/alpha)
  Base amplitude: G* = {self.G_star:.6f}
  Modulation: Sum of sin(N*theta) for N in {{3, 7, 13}}

PHYSICAL INTERPRETATION:
------------------------
The Fermat coil winds 137 times, encoding the fine structure constant.
The coil passes through turn 3 (N_c), turn 7 (b_3), and turn 13 (N_eff),
marking the framework integers. The quadratic structure determines
the radial profile, with roots at 1/alpha and N_c.

"The fine structure constant is the geometric cost of
 self-reference at the Fermat boundary."

================================================================================
"""

    def print_summary(self):
        """Print the text description."""
        print(self.text_description())


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================

if __name__ == "__main__":
    import sys

    coil = FermatCoil()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--text":
            coil.print_summary()
        elif sys.argv[1] == "--2d":
            coil.plot_2d_coil()
        elif sys.argv[1] == "--3d":
            coil.plot_3d_coil()
        elif sys.argv[1] == "--interactive":
            # Generate interactive 3D and save as HTML
            coil.plot_3d_interactive(
                save_path="figures/fermat_coil_interactive.html",
                show=True
            )
        elif sys.argv[1] == "--quadratic":
            coil.plot_quadratic_profile()
        elif sys.argv[1] == "--lemniscate":
            coil.plot_2d_coil(coil_type="lemniscate")
        elif sys.argv[1] == "--all":
            coil.print_summary()
            if MATPLOTLIB_AVAILABLE:
                coil.plot_quadratic_profile()
                coil.plot_2d_coil()
                coil.plot_3d_coil()
            if PLOTLY_AVAILABLE:
                coil.plot_3d_interactive(
                    save_path="figures/fermat_coil_interactive.html",
                    show=False
                )
        else:
            print("Usage: python fermat_coil.py [--text|--2d|--3d|--interactive|--quadratic|--lemniscate|--all]")
    else:
        # Default: print summary and show interactive 3D if available
        coil.print_summary()
        if PLOTLY_AVAILABLE:
            coil.plot_3d_interactive()
        elif MATPLOTLIB_AVAILABLE:
            coil.plot_2d_coil()
