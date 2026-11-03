"""Point reduction for plotted curves, driven by the curve's physical length on the figure."""

import heapq
import math

import numpy as np


def _clipped_segment_lengths(
    px: np.ndarray, py: np.ndarray, w: float, h: float
) -> tuple[np.ndarray, np.ndarray]:
    """Liang-Barsky clip of every segment against the box [0, w] x [0, h].

    Returns (visible length of each segment in mm, boolean visibility mask).
    """
    x0, y0, x1, y1 = px[:-1], py[:-1], px[1:], py[1:]
    dx, dy = x1 - x0, y1 - y0
    t0 = np.zeros_like(dx)
    t1 = np.ones_like(dx)
    with np.errstate(divide="ignore", invalid="ignore"):
        for p, q in ((-dx, x0), (dx, w - x0), (-dy, y0), (dy, h - y0)):
            t = q / p
            parallel = p == 0
            outside_parallel = parallel & (q < 0)
            t0 = np.where(~parallel & (p < 0), np.maximum(t0, t), t0)
            t1 = np.where(~parallel & (p > 0), np.minimum(t1, t), t1)
            t1 = np.where(outside_parallel, -1.0, t1)  # mark as invisible
    finite = np.isfinite(dx) & np.isfinite(dy)
    visible = finite & (t1 >= t0)
    seg_len = np.where(visible, (t1 - t0) * np.hypot(dx, dy), 0.0)
    return np.nan_to_num(seg_len), visible


def reduce_curve(
    x: np.ndarray,
    y: np.ndarray,
    x_limits: tuple[float, float],
    y_limits: tuple[float, float],
    fig_width_mm: float,
    fig_height_mm: float,
    points_per_mm: float,
    n_min = 11
) -> tuple[np.ndarray, np.ndarray]:
    """Reduce a densely sampled curve to the number of points it actually needs on paper.

    1. The curve is mapped into figure millimetres (axes box = fig_width_mm x fig_height_mm)
       and its length *inside the axes limits* is computed (segments are clipped).
    2. N = max(n_min, ceil(points_per_mm * curve_length_mm)).
    3. Visvalingam-Whyatt simplification in mm coordinates: repeatedly remove the vertex
       whose removal changes the drawn polyline by the smallest area until N vertices are
       left. Sharp corners and high-curvature regions keep their points, straight stretches
       lose them. The result is a subset of the original samples, so every output point lies
       exactly on the original curve.

    Parts of the curve outside the limits are discarded; where the curve leaves and re-enters
    the axes, a NaN separator is inserted (matplotlib breaks the line there). NaNs in the input
    are treated as gaps in the same way. N counts real points only, not NaN separators.

    Returns (x_reduced, y_reduced) in data coordinates.
    """
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()
    if x.shape != y.shape:
        raise ValueError("x and y must have the same length")
    if x_limits is None:
        raise ValueError("x_limits must not be None")
    if y_limits is None:
        raise ValueError("y_limits must not be None")
    (xmin, xmax), (ymin, ymax) = x_limits, y_limits
    if xmax == xmin or ymax == ymin:
        raise ValueError("degenerate axis limits")

    # --- 1) map to mm and measure visible length ---------------------------------------
    px = (x - xmin) / (xmax - xmin) * fig_width_mm
    py = (y - ymin) / (ymax - ymin) * fig_height_mm
    if x.size < 2:
        return x.copy(), y.copy()
    seg_len, seg_vis = _clipped_segment_lengths(px, py, fig_width_mm, fig_height_mm)
    curve_length_mm = float(seg_len.sum())

    # --- 2) point budget ---------------------------------------------------------------
    n_target = max(n_min, math.ceil(points_per_mm * curve_length_mm))

    if n_target >= x.size:
        return x.copy(), y.copy()

    # --- split into visible runs (vertex sets touching at least one visible segment) ----
    runs: list[np.ndarray] = []
    start = None
    for i, v in enumerate(seg_vis):
        if v and start is None:
            start = i
        elif not v and start is not None:
            runs.append(np.arange(start, i + 1))
            start = None
    if start is not None:
        runs.append(np.arange(start, len(px)))
    if not runs:  # nothing visible: keep a single in-range point if there is one
        return x[:0].copy(), y[:0].copy()

    # Vectorised pre-pass for very dense input: in rounds, drop every second interior vertex
    # whose triangle area (w.r.t. its current neighbours) is negligible. Tolerance is tied to
    # the point spacing on paper, (1/points_per_mm)^2, scaled far below anything visible.
    total = sum(len(r) for r in runs)
    if total > 8 * n_target:
        tol = 1e-6 / points_per_mm**2
        new_runs = []
        for r in runs:
            for parity in range(40):
                if len(r) < 3:
                    break
                a, b, c = r[:-2], r[1:-1], r[2:]
                ar = 0.5 * np.abs(
                    (px[b] - px[a]) * (py[c] - py[a]) - (px[c] - px[a]) * (py[b] - py[a])
                )
                cand = np.zeros(len(r), dtype=bool)
                cand[1:-1] = ar < tol
                cand[(np.arange(len(r)) % 2) != (parity % 2)] = False  # non-adjacent only
                if not cand.any():
                    if parity % 2 == 1:
                        break
                    continue
                r = r[~cand]
            new_runs.append(r)
        runs = new_runs

    keep_idx = np.concatenate(runs)
    n_avail = keep_idx.size

    if n_avail <= n_target:
        # Already sparse enough. Adding vertices on straight segments would not reduce the
        # error, so pad only to honour the requested count: subdivide the longest segments.
        return _pad_runs(x, y, px, py, runs, n_target)

    # --- 3) Visvalingam-Whyatt with a global budget across all runs ----------------------
    prev_a = np.full(len(px), -1, dtype=np.int64)
    nxt_a = np.full(len(px), -1, dtype=np.int64)
    for r in runs:
        prev_a[r[1:]] = r[:-1]
        nxt_a[r[:-1]] = r[1:]
    prev, nxt = prev_a.tolist(), nxt_a.tolist()

    # Initial effective areas, vectorised; the removal loop works on plain Python floats.
    removed = [False] * len(px)
    area = [math.inf] * len(px)
    heap = []
    for r in runs:
        if len(r) < 3:
            continue
        a, b, c = r[:-2], r[1:-1], r[2:]
        ar = 0.5 * np.abs((px[b] - px[a]) * (py[c] - py[a]) - (px[c] - px[a]) * (py[b] - py[a]))
        for i, ai in zip(b.tolist(), ar.tolist()):
            area[i] = ai
            heap.append((ai, i))
    heapq.heapify(heap)

    X, Y = px.tolist(), py.tolist()
    heappop, heappush = heapq.heappop, heapq.heappush
    n_left = n_avail
    max_area = 0.0  # enforce monotone areas (standard VW tweak)
    while n_left > n_target and heap:
        a, i = heappop(heap)
        if removed[i] or area[i] != a:
            continue  # stale heap entry
        if a > max_area:
            max_area = a
        removed[i] = True
        n_left -= 1
        p, n = prev[i], nxt[i]
        nxt[p] = n
        prev[n] = p
        for j in (p, n):
            pj, nj = prev[j], nxt[j]
            if pj != -1 and nj != -1:
                aj = 0.5 * abs((X[j] - X[pj]) * (Y[nj] - Y[pj]) - (X[nj] - X[pj]) * (Y[j] - Y[pj]))
                if aj < max_area:
                    aj = max_area
                area[j] = aj
                heappush(heap, (aj, j))

    out_x, out_y = [], []
    for r in runs:
        # if out_x:
        #     out_x.append(np.nan)
        #     out_y.append(np.nan)
        sel = r[~np.asarray(removed)[r]]
        out_x.extend(x[sel])
        out_y.extend(y[sel])
    print(f'Reduced curve from {x.size} -> {len(out_x)}')
    return np.asarray(out_x), np.asarray(out_y)


def _pad_runs(x, y, px, py, runs, n_target):
    """Insert extra points on the longest (mm) segments until n_target points exist."""
    total = sum(len(r) for r in runs)
    pieces = [np.ones(len(r) - 1, dtype=int) for r in runs]
    lens = [np.hypot(np.diff(px[r]), np.diff(py[r])) for r in runs]
    heap = [(-lens[k][j], k, j) for k in range(len(runs)) for j in range(len(runs[k]) - 1)]
    heapq.heapify(heap)
    while total < n_target and heap:
        _, k, j = heapq.heappop(heap)
        pieces[k][j] += 1
        total += 1
        heapq.heappush(heap, (-lens[k][j] / pieces[k][j], k, j))
    out_x, out_y = [], []
    for k, r in enumerate(runs):
        # if out_x:
        #     out_x.append(np.nan)
        #     out_y.append(np.nan)
        for j in range(len(r) - 1):
            t = np.arange(pieces[k][j]) / pieces[k][j]
            out_x.extend(x[r[j]] + t * (x[r[j + 1]] - x[r[j]]))
            out_y.extend(y[r[j]] + t * (y[r[j + 1]] - y[r[j]]))
        out_x.append(x[r[-1]])
        out_y.append(y[r[-1]])
    return np.asarray(out_x), np.asarray(out_y)