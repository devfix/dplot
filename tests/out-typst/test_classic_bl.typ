// auto-generated using dplot (TypstGenerator - Lilaq)
#import "@preview/lilaq:0.6.0" as lq

#set page(
  width: auto,
  height: auto,
  margin: (top: 0mm, bottom: 0mm, left: 0mm, right: 0mm),
)

#lq.diagram(
  width: 50.000mm,
  height: 50.000mm,
  fill: rgb(217, 217, 217),
  xlim: (-2, 2),
  xlabel: [x],
  ylim: (0, 5),
  ylabel: [y],
  grid: none,
  legend: none,
  lq.plot(
    (-2, -1, 0, 1, 2),,
    (5, 1, 0, 1, 5),,
    stroke: (paint: rgb(0, 0, 0), thickness: 1pt, dash: "solid"),
  ),
)