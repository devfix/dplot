// auto-generated using dplot (TypstGenerator - Lilaq)
#import "@preview/lilaq:0.6.0" as lq

#set page(
  width: auto,
  height: auto,
  margin: (top: 3.000mm, bottom: 10.000mm, left: 12.000mm, right: 12.000mm),
)

#show: lq.cond-set(lq.tick.with(sub: false), stroke: 0.400pt + rgb(0, 0, 0))
#lq.diagram(
  bounds: "data-area",
  width: 50.000mm,
  height: 50.000mm,
  fill: rgb(240, 248, 255),
  xlim: (-2, 2),
  xlabel: [x],
  xaxis: (subticks: none, mirror: (ticks: false)),
  ylim: (0, 4),
  ylabel: [y],
  yaxis: (subticks: none, mirror: (ticks: false)),
  grid: (stroke: none, stroke-sub: none),
  legend: none,
  lq.plot(
    (-2, -1.9, -1.8, -1.7, -1.6, -1.5, -1.4, -1.3, -1.2, -1.1, -1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2),
    (4, 3.61, 3.24, 2.89, 2.56, 2.25, 1.96, 1.69, 1.44, 1.21, 1, 0.81, 0.64, 0.49, 0.36, 0.25, 0.16, 0.09, 0.04, 0.01, 0, 0.01, 0.04, 0.09, 0.16, 0.25, 0.36, 0.49, 0.64, 0.81, 1, 1.21, 1.44, 1.69, 1.96, 2.25, 2.56, 2.89, 3.24, 3.61, 4),
    stroke: (paint: rgb(0, 0, 255), thickness: 1.000pt, dash: "solid"),
    mark: none,
  ),
)