"""
plotting.py — Lightweight Plotly wrapper for fast prototyping.

Provides a set of convenience functions for common chart types:
    - Box plots            (plotBox)
    - Multi-line / scatter (plotCombine, plotCompare, plotScatter)
    - Heatmaps & contours  (plotMap, plotHeatmap)
    - Trajectory & optim.  (plotTrajectory, plotOptimization)
    - PCA projection       (viewPCA)

All Plotly-based functions share a common `render()` helper that
applies consistent styling, optional export, and HTML/inline output.
"""

import plotly.offline as py
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import time


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def render(fig, title, size, html, export):
    """
    Apply shared layout settings and output the figure.

    Parameters
    ----------
    fig    : go.Figure  — the Plotly figure to render
    title  : str        — chart title (also used as the output filename)
    size   : tuple | None — (height, width) in pixels; None keeps Plotly defaults
    html   : bool       — if True, write an interactive .html file instead of
                          displaying inline (useful in non-notebook environments)
    export : str | None — static image format to save, e.g. 'png', 'svg', 'pdf';
                          None skips static export. Written twice with a short
                          sleep to work around kaleido race conditions.
    """
    # Global font size and tight margins (overridden below after optional export)
    fig.update_layout(font={'size': 30})
    fig.update_layout(margin_t=10, margin_r=10)

    # Legend: top-right corner, semi-transparent background
    fig.update_layout(legend=dict(
        yanchor="top", y=0.99,
        xanchor="right", x=0.99,
        bgcolor="rgba(0,0,0,.05)"
    ))

    # Optional fixed canvas size
    if size:
        height, width = size
        fig.update_layout(width=width, height=height)

    # Static image export (written twice to avoid kaleido blank-frame bug)
    if export:
        fig.write_image('./' + title + '.' + export)
        time.sleep(2)
        fig.write_image('./' + title + '.' + export)

    # Add title and restore top margin now that image export is done
    fig.update_layout(title=title)
    fig.update_layout(margin_t=100)

    if html:
        # Save a self-contained interactive HTML file
        fig.write_html('./' + title + '.html')
    else:
        # Display inline (Jupyter / Colab)
        py.iplot(fig)


# ---------------------------------------------------------------------------
# Chart functions
# ---------------------------------------------------------------------------

def plotBox(plot, title=None, x_label=None, y_label=None,
            size=None, html=False, export=None, ylimit=None):
    """
    Render a grouped box-plot from a dictionary of distributions.

    Parameters
    ----------
    plot    : dict[str, array-like]
              Keys become box labels; values are the raw data arrays.
              Example: {'GroupA': [1,2,3], 'GroupB': [4,5,6]}
    title   : str        — chart title & export filename
    x_label : str        — x-axis label
    y_label : str        — y-axis label
    size    : tuple      — (height, width) in pixels
    html    : bool       — write HTML instead of displaying inline
    export  : str | None — static export format ('png', 'svg', …)
    ylimit  : list | None — [y_min, y_max] to fix the y-axis range
    """
    fig = go.Figure()
    for name, dist in plot.items():
        fig.add_trace(go.Box(y=dist, name=name))

    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
    fig.update_layout(showlegend=False)   # Labels already on x-axis
    fig.update_layout(yaxis_range=ylimit)
    render(fig, title, size, html, export)


def plotCombine(plot, title=None, x_label=None, y_label=None,
                mode='lines', width=5, size=None,
                html=False, export=None, legend=True):
    """
    Overlay multiple (x, y) series on a single chart.

    Unlike `plotCompare` (which shares a common x array), each series
    here supplies its own x values — useful when series have different
    resolutions or domains.

    Parameters
    ----------
    plot  : dict[str, (array-like, array-like)]
            Keys are series names; values are (x, y) tuples.
            Example: {'sin': (x, np.sin(x)), 'cos': (x, np.cos(x))}
    mode  : str  — Plotly scatter mode: 'lines', 'markers', 'lines+markers'
    width : int  — line width and marker size
    (remaining params same as plotBox)
    """
    fig = go.Figure()
    for name, (x, y) in plot.items():
        fig.add_trace(go.Scatter(
            x=x, y=y, name=name, mode=mode,
            line={'width': width}, marker={'size': width}
        ))

    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
    fig.update_layout(showlegend=legend)
    render(fig, title, size, html, export)


def plotScatter(x, plot, title=None, x_label=None, y_label=None,
                size=None, dot_size=1, html=False, export=None, legend=True):
    """
    Scatter plot with a shared x array and multiple y series.

    Parameters
    ----------
    x        : array-like — shared x values for all series
    plot     : dict[str, array-like] — series name → y values
    dot_size : int — marker size in pixels
    (remaining params same as plotBox)
    """
    fig = go.Figure()
    for name, values in plot.items():
        fig.add_trace(go.Scatter(
            x=x, y=values, name=name,
            mode='markers', marker={'size': dot_size}
        ))

    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
    fig.update_layout(showlegend=legend)
    render(fig, title, size, html, export)


def plotCompare(x, plot, title=None, x_label=None, y_label=None,
                width=5, size=None, html=False, export=None, legend=True):
    """
    Line chart comparing multiple y series against a single shared x array.

    Use this when all series share the same x axis (e.g. time, epochs).
    For series with different x domains, use `plotCombine` instead.

    Parameters
    ----------
    x     : array-like               — shared x axis
    plot  : dict[str, array-like]    — series name → y values
    width : int                      — line width
    (remaining params same as plotBox)
    """
    fig = go.Figure()
    for name, values in plot.items():
        fig.add_trace(go.Scatter(x=x, y=values, name=name, line={'width': width}))

    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
    fig.update_layout(showlegend=legend)
    render(fig, title, size, html, export)


def plotMap(z, x, y, title=None, xaxis=None, yaxis=None,
            size=None, html=False, export=None, legend=True, log=False):
    """
    Render a 2-D heatmap (flat colour blocks, no interpolation).

    Parameters
    ----------
    z      : 2-D array-like — matrix of values (rows = y, cols = x)
    x      : array-like     — x-axis tick labels / coordinates
    y      : array-like     — y-axis tick labels / coordinates
    xaxis  : str            — x-axis label
    yaxis  : str            — y-axis label
    log    : bool           — use log scale on both axes
    (remaining params same as plotBox)
    """
    fig = go.Figure()
    heatmap = go.Heatmap(z=z, y=y, x=x)
    fig.add_trace(heatmap)

    fig.update_layout(showlegend=legend)
    fig.update_traces(showscale=legend)
    fig.update_layout(coloraxis_showscale=legend)
    fig.update_layout(xaxis_title=xaxis, yaxis_title=yaxis)

    if log:
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")

    render(fig, title, size, html, export)


def plotHeatmap(z, x, y, title=None, xaxis=None, yaxis=None,
                size=None, html=False, export=None,
                ncontours=10, legend=True, log=False):
    """
    Contour plot with heatmap colour-fill (smoothed / interpolated).

    Prefer this over `plotMap` when the underlying surface is continuous
    and you want to highlight level sets (iso-lines).

    Parameters
    ----------
    z         : 2-D array-like — surface values
    x         : array-like     — x coordinates
    y         : array-like     — y coordinates
    ncontours : int            — number of contour levels (default 10)
    (remaining params same as plotMap)
    """
    fig = go.Figure()
    start = z.min()
    end = z.max()
    contours = dict(start=start, end=end, size=(end - start) / ncontours)
    heatmap = go.Contour(z=z, y=y, x=x, contours_coloring='heatmap', contours=contours)
    fig.add_trace(heatmap)

    fig.update_layout(showlegend=legend)
    fig.update_traces(showscale=legend)
    fig.update_layout(coloraxis_showscale=legend)
    fig.update_layout(xaxis_title=xaxis, yaxis_title=yaxis)

    if log:
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")

    render(fig, title, size, html, export)


def plotTrajectory(evo, plot, title=None, x_label=None, y_label=None,
                   size=None, html=False, export=None, legend=False):
    """
    Animate 2-D paths with marker sizes that grow over time.

    Useful for visualising agent trajectories, particle paths, or
    any sequential 2-D motion where recency should be visually salient.

    Parameters
    ----------
    evo  : array-like              — 1-D sequence whose values drive marker
                                     sizes (normalised to [0, 15]); typically
                                     frame indices or timestamps
    plot : dict[str, ndarray]      — name → (N, 2) array of (x, y) positions
    (remaining params same as plotBox)
    """
    fig = go.Figure()
    # Normalise evolution values so marker sizes stay in a readable range
    evo = evo / max(evo) * 15

    for name, path in plot.items():
        fig.add_trace(go.Scatter(
            x=path[:, 0], y=path[:, 1], name=name,
            mode='lines+markers',
            marker={'size': evo},
            line={'width': 5}
        ))

    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
    fig.update_layout(showlegend=legend)
    render(fig, title, size, html, export)


def plotOptimization(z, x, y, paths, title=None, xaxis=None, yaxis=None,
                     size=None, html=False, export=None, legend=False, log=False):
    """
    Visualise optimiser trajectories overlaid on a loss-landscape contour.

    The loss surface is drawn as a filled contour map; each optimiser path
    is drawn as a line whose markers grow linearly so you can track progress
    from start (small dot) to end (large dot).

    Parameters
    ----------
    z     : 2-D array-like        — loss surface values
    x     : array-like            — x-axis grid values (e.g. weight₁ range)
    y     : array-like            — y-axis grid values (e.g. weight₂ range)
    paths : dict[str, ndarray]    — optimiser name → (N, 2) array of (x, y)
                                    parameter positions at each step
    (remaining params same as plotMap)
    """
    fig = go.Figure()

    # Background: loss surface as a filled contour map
    heatmap = go.Contour(z=z, y=y, x=x, name='loss', contours_coloring='heatmap')
    fig.add_trace(heatmap)
    fig.update_layout(xaxis_title=xaxis, yaxis_title=yaxis)

    # Overlay each optimiser path with linearly growing markers
    for name, path in paths.items():
        evo = [i * 15 / len(path) for i in range(len(path))]
        fig.add_trace(go.Scatter(
            x=path[:, 0], y=path[:, 1], name=name,
            mode='lines+markers',
            marker={'size': evo},
            line={'width': 3}
        ))

    fig.update_layout(showlegend=legend)
    if log:
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")

    render(fig, title, size, html, export)


# ---------------------------------------------------------------------------
# Matplotlib helpers
# ---------------------------------------------------------------------------

def viewPCA(X, index, size=(8, 6), title=None, x=None, y=None):
    """
    Project high-dimensional data to 2-D via PCA and render a scatter plot.

    Uses matplotlib (not Plotly) so it renders without a running Plotly server.
    Points are coloured by `index`, making it easy to spot clusters.

    Parameters
    ----------
    X     : array-like, shape (n_samples, n_features) — input data matrix
    index : array-like, shape (n_samples,)            — colour values per point
                                                        (e.g. cluster labels, targets)
    size  : tuple — figure size as (width, height) in inches (default (8, 6))
    title : str   — plot title
    x     : str   — x-axis label (PCA component 1)
    y     : str   — y-axis label (PCA component 2)
    """
    from sklearn.decomposition import PCA

    # Fit PCA and reduce to 2 components
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    plt.figure(figsize=size)
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=index, cmap='viridis')
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    plt.colorbar(label='index')
    plt.show()