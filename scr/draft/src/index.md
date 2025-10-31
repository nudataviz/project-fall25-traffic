# EDA

**Name:** LaneMerge Simulation  

**Story:**  
On many multi-lane roads, traffic often merges into a single lane at intersections. Some drivers merge early, while others cut in at the last moment, causing congestion and long waiting times. We propose simulating a rule change where drivers must merge 100 meters before the traffic light (with a $200 fine for violations) to test whether orderly merging improves traffic flow and reduces waiting time.  

## Overview

This exploratory data analysis (EDA) focuses on visualizing and understanding basic **traffic lane dynamics** before modeling the full *LaneMerge Simulation* proposed in the project.  
The goal is to build an initial animation that helps visualize car movement, spacing, and timing — serving as a foundation for later modeling of merging behavior and traffic regulation.

---

## Figure

The current figure (implemented in **D3** within Observable Framework) presents a **two-lane road animation**:

- Two solid lines and one dashed center line represent a simplified road.  
- Each blue rectangle represents a car moving in one direction.  
- Cars travel at the same speed but start at different times to simulate staggered traffic flow.  

This visualization demonstrates smooth, continuous vehicle motion and provides an initial baseline for simulating merging events.

```js
import * as d3 from "d3";

const W = 700, H = 220, topY = 60, botY = 160, midY = (topY + botY)/2;
const svg = d3.create("svg").attr("width", W).attr("height", H).style("background", "lightgrey");
display(svg.node());

svg.append("line").attr("x1",20).attr("x2",W-20).attr("y1",topY).attr("y2",topY).attr("stroke","gray").attr("stroke-width",4);
svg.append("line").attr("x1",20).attr("x2",W-20).attr("y1",botY).attr("y2",botY).attr("stroke","gray").attr("stroke-width",4);
svg.append("line").attr("x1",20).attr("x2",W-20).attr("y1",midY).attr("y2",midY).attr("stroke","gray").attr("stroke-width",2).attr("stroke-dasharray","10,10");

const carW = 60, carGap = 15, v = 1.2;
const carH = (midY - topY) - 10;

function makeLane(yTop, laneDelay=0){
  const y = yTop + 6;
  const n = 5;
  const cars = d3.range(n).map(i => ({
    x: -(i+1)*(carW+carGap),
    delay: laneDelay + i*800 + Math.random()*800
}));
  const rects = svg.selectAll(null)
    .data(cars)
    .enter()
    .append("rect")
    .attr("x", d => d.x)
    .attr("y", y)
    .attr("width", carW)
    .attr("height", carH)
    .attr("fill", "yellow")
    .attr("rx", 3);
  return {cars, rects};
}

const topLane = makeLane(topY, 0);
const botLane = makeLane(midY, 1200);


d3.timer((elapsed) => {
  for (const lane of [topLane, botLane]) {
    lane.cars.forEach(d => {
      if (elapsed < d.delay) return;
      d.x += v;
      if (d.x > W) d.x = -carW - carGap;
    });
    lane.rects.attr("x", d => d.x);
  }
});

```

---

## Description of Results

From the basic simulation:

- When car start times are staggered and spacing is consistent, the flow remains smooth and congestion-free.  
- When start times overlap or spacing shortens, vehicles cluster visually — an early sign of potential bottlenecks.  
- This confirms that **timing and distance between vehicles** are key to maintaining stable traffic flow even before merging occurs.  

These insights motivated the modeling design to include adjustable parameters controlling speed limits, safe distance, and merge timing.

---

## Next Steps: Modeling & Interaction

The next phase will expand from simple motion to **merge behavior simulation**, focusing on how lane regulation affects congestion.

---

### Planned Adjustable Parameters

1. **Minimum safe distance between cars** — determines when vehicles can safely merge.  
2. **Safe braking space** — ensures vehicles maintain enough distance to stop if the car in front slows down.  
3. **Speed limit** — affects flow rate and merging efficiency.

---

### Scenarios to Compare

- **Early merging:** vehicles begin merging approximately *100 meters before* the merge point.  
- **Late merging:** vehicles merge only near the end, simulating *“last-minute cutting in.”*

The final model will allow interactive adjustment of these parameters, letting users explore how earlier merging leads to smoother traffic flow and fewer jams.

---

## Challenges and Risks

- Modeling realistic merge logic without cars overlapping.  
- Synchronizing multiple animations while maintaining smooth rendering.  
- Designing intuitive user controls for parameter adjustment.  
- Simulated results may not perfectly reflect real driver behavior.






