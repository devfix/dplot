// auto-generated using dplot (TypstGenerator - Lilaq)
#import "@preview/lilaq:0.6.0" as lq

#set page(
  width: auto,
  height: auto,
  margin: (top: 10.000mm, bottom: 10.000mm, left: 15.000mm, right: 15.000mm),
)

#block(width: 50.000mm, height: 50.000mm, [
  #place(top + left)[
    #show: lq.cond-set(lq.grid.with(kind: "x"), stroke: 1.200pt + rgb(0, 0, 0), stroke-sub: 0.400pt + rgb(211, 211, 211))
    #show: lq.cond-set(lq.grid.with(kind: "y"), stroke: none, stroke-sub: none)
    #show: lq.cond-set(lq.tick.with(kind: "x", sub: false), stroke: 1.200pt + rgb(0, 0, 0))
    #show: lq.cond-set(lq.tick.with(kind: "x", sub: true), stroke: 0.200pt + rgb(211, 211, 211))
    #show: lq.cond-set(lq.tick.with(kind: "y", sub: false), stroke: 0.400pt + rgb(0, 0, 0))
    #lq.diagram(
      bounds: "data-area",
      width: 50.000mm,
      height: 50.000mm,
      xlim: (0, 5),
      xlabel: [bottom],
      xaxis: (subticks: 4, mirror: (ticks: false)),
      ylim: (4, 6),
      ylabel: [left],
      yscale: "log",
      yaxis: (subticks: none, mirror: (ticks: false)),
      legend: none,
      lq.plot(
        (0, 1, 2, 3, 4, 5),
        (4, 5, 4, 5, 4, 5),
        stroke: (paint: rgb(255, 0, 0), thickness: 1.000pt, dash: "solid"),
        mark: none,
      ),
    )
  ]
  #place(top + left)[
    #show: lq.cond-set(lq.tick.with(kind: "y", sub: false), stroke: 0.400pt + rgb(0, 0, 0))
    #lq.diagram(
      bounds: "data-area",
      width: 50.000mm,
      height: 50.000mm,
      fill: none,
      xlim: (0, 5),
      xaxis: (ticks: none, subticks: none),
      ylim: (0, 2),
      ylabel: [right],
      yaxis: (position: right, subticks: none, mirror: (ticks: false)),
      grid: (stroke: none, stroke-sub: none),
      legend: none,
      lq.plot(
        (0, 1, 2, 3, 4, 5),
        (1, 1, 2, 1, 1, 1),
        stroke: (paint: rgb(50, 205, 50), thickness: 2.000pt, dash: "dotted"),
        mark: none,
      ),
    )
  ]
  #place(top + left)[
    #show: lq.cond-set(lq.tick.with(kind: "x", sub: false), stroke: 0.800pt + rgb(0, 0, 0))
    #show: lq.cond-set(lq.tick.with(kind: "x", sub: true), stroke: 0.400pt + rgb(128, 128, 128))
    #lq.diagram(
      bounds: "data-area",
      width: 50.000mm,
      height: 50.000mm,
      fill: none,
      xlim: (-2, 0),
      xlabel: [top],
      xaxis: (position: top, subticks: 1, mirror: (ticks: false)),
      ylim: (4, 6),
      yscale: "log",
      yaxis: (ticks: none, subticks: none),
      grid: (stroke: none, stroke-sub: none),
      legend: none,
      lq.plot(
        (-2, -1, 0),
        (4, 6, 4),
        stroke: (paint: rgb(138, 43, 226), thickness: 1.000pt, dash: "solid"),
        mark: ((mark, fill: rgb(138, 43, 226), stroke: rgb(138, 43, 226)) => (lq.marks.s)((size: mark.size, stroke: stroke, fill: none))),
        every: 2,
      ),
    )
  ]
  #place(top + left)[
    #lq.diagram(
      bounds: "data-area",
      width: 50.000mm,
      height: 50.000mm,
      fill: none,
      xlim: (-2, 0),
      xaxis: (position: top, ticks: none, subticks: none),
      ylim: (0, 2),
      yaxis: (position: right, ticks: none, subticks: none),
      grid: (stroke: none, stroke-sub: none),
      legend: none,
      lq.plot(
        (-2, -1, 0),
        (0, 1, 0),
        stroke: (paint: rgb(188, 143, 143), thickness: 0.500pt, dash: "solid"),
        mark: none,
      ),
    )
  ]
])