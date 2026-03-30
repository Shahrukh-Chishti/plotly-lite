# plotting.py

A lightweight Plotly wrapper for fast prototyping of common scientific and ML charts — minimal boilerplate, consistent styling out of the box.

## Installation

```bash
pip install plotly kaleido scikit-learn matplotlib numpy
```

## Usage

```python
from plotting import plotBox, plotCompare, plotHeatmap  # etc.
```

Every function accepts a `title`, `x_label` / `y_label`, an optional `size=(height, width)` tuple, and two output modes:

| Param | Default | Effect |
|---|---|---|
| `html=False` | `False` | Save a self-contained `.html` file instead of displaying inline |
| `export=None` | `None` | Save a static image — `'png'`, `'svg'`, `'pdf'`, … |

---

## Functions

### `plotBox` — grouped box plots

```python
plotBox(
    {'Model A': array_a, 'Model B': array_b},
    title='Accuracy by Model',
    y_label='Accuracy',
    ylimit=[0.5, 1.0],
)
```

### `plotCompare` — line chart with shared x axis

Best for training curves, time series, anything where all series share the same x values.

```python
epochs = np.arange(1, 51)
plotCompare(
    epochs,
    {'Train': train_loss, 'Val': val_loss},
    title='Loss Curves',
    x_label='Epoch', y_label='Loss',
)
```

### `plotCombine` — multi-series with independent x arrays

Use when each series has its own x domain or resolution.

```python
plotCombine(
    {'sin': (t, np.sin(t)), 'cos': (t, np.cos(t))},
    title='Trig Functions',
    mode='lines',  # 'markers' or 'lines+markers' also accepted
)
```

### `plotScatter` — scatter plot, shared x

```python
plotScatter(
    x_vals,
    {'Group A': y_a, 'Group B': y_b},
    title='Feature vs Target',
    dot_size=4,
)
```

### `plotMap` — raw heatmap (no interpolation)

Good for confusion matrices, correlation grids, any discrete 2-D matrix.

```python
plotMap(z=matrix, x=col_labels, y=row_labels, title='Confusion Matrix')
```

### `plotHeatmap` — contour plot with heatmap fill

For continuous surfaces where you want to highlight level sets.

```python
plotHeatmap(z=Z, x=grid_x, y=grid_y, title='Loss Surface', ncontours=15)
```

### `plotTrajectory` — 2-D paths with time-varying marker size

Markers grow over time so you can track direction at a glance.

```python
plotTrajectory(
    evo=np.arange(T),           # drives marker size (normalised to [0, 15])
    plot={'Agent': path},       # path is an (N, 2) array
    title='Agent Trajectory',
)
```

### `plotOptimization` — loss landscape + optimiser paths

Overlays one or more optimiser trajectories on a filled contour map.

```python
plotOptimization(
    z=loss_surface, x=w1, y=w2,
    paths={'SGD': sgd_path, 'Adam': adam_path},
    title='Optimiser Comparison',
)
```

### `viewPCA` — 2-D PCA projection *(matplotlib)*

Reduces high-dimensional data to 2 components and colours points by a given index.

```python
viewPCA(X, index=labels, title='PCA Projection', x='PC 1', y='PC 2')
```

---

## Exporting

```python
# Save a PNG (written twice to avoid kaleido race condition)
plotCompare(epochs, data, title='loss', export='png')

# Save an interactive HTML file
plotCompare(epochs, data, title='loss', html=True)
```
