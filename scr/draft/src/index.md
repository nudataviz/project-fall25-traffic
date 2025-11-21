# MVP

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
const W = 700;
const H = 220;
const topY = 60;
const botY = 160;
const midY = (topY + botY) / 2;

let SPEED_MIN = 0.3;
let SPEED_MAX = 1.5;

const container = d3.create("div");
display(container.node());

const svg = container.append("svg")
  .attr("width", W)
  .attr("height", H)
  .style("background", "#f8fafc");

svg.append("line")
  .attr("x1", 20).attr("x2", W - 20)
  .attr("y1", topY).attr("y2", topY)
  .attr("stroke", "#94a3b8").attr("stroke-width", 4);

svg.append("line")
  .attr("x1", 20).attr("x2", W - 20)
  .attr("y1", botY).attr("y2", botY)
  .attr("stroke", "#94a3b8").attr("stroke-width", 4);

svg.append("line")
  .attr("x1", 20).attr("x2", W - 20)
  .attr("y1", midY).attr("y2", midY)
  .attr("stroke", "#cbd5e1").attr("stroke-width", 2)
  .attr("stroke-dasharray", "10,10");

const mergeX = Math.floor(W * 2 / 3);
const STOP_X  = mergeX - 60;

svg.append("line")
  .attr("x1", mergeX).attr("x2", mergeX)
  .attr("y1", topY - 20).attr("y2", midY + 20)
  .attr("stroke", "#ef4444").attr("stroke-width", 3);

const carW = 50;
const carH = 35;
const carGap = 15;
const vBase = 1.1;
const vMergeY = 0.8;

const MIN_GAP = carW + carGap;
const Y_TOP = topY + 6;
const Y_BOT = midY + 6;

const MAX_TOP = 10;
const MAX_BOT = 18;

let nextId = 1;
let cars = [];
const g = svg.append("g");

const controls = container.append("div")
  .style("margin-top", "8px")
  .style("font", "12px system-ui, sans-serif");

const rowMin = controls.append("div").style("margin-bottom", "4px");
rowMin.append("span")
  .text("Min speed: ")
  .style("margin-right", "4px");

const minSlider = rowMin.append("input")
  .attr("type", "range")
  .attr("min", 0.05)
  .attr("max", 1.5)
  .attr("step", 0.05)
  .attr("value", SPEED_MIN);

const minLabel = rowMin.append("span").text(SPEED_MIN.toFixed(2));

minSlider.on("input", function() {
  const v = Number(this.value);
  SPEED_MIN = v;
  minLabel.text(v.toFixed(2));
});

const rowMax = controls.append("div");
rowMax.append("span")
  .text("Max speed: ")
  .style("margin-right", "4px");

const maxSlider = rowMax.append("input")
  .attr("type", "range")
  .attr("min", 0.3)
  .attr("max", 3.0)
  .attr("step", 0.05)
  .attr("value", SPEED_MAX);

const maxLabel = rowMax.append("span").text(SPEED_MAX.toFixed(2));

maxSlider.on("input", function() {
  const v = Number(this.value);
  SPEED_MAX = v;
  maxLabel.text(v.toFixed(2));
});

function spawn(lane, baseDelay) {
  if (baseDelay === undefined) baseDelay = 0;
  const jitter = 400 + Math.random() * 800;
  const x0 = -(carW + carGap) - Math.random() * 120;
  let y;
  if (lane === "top") {
    y = Y_TOP;
  } else {
    y = Y_BOT;
  }
  let color;
  if (lane === "top") {
    color = "#4F8EF7";
  } else {
    color = "#F4A261";
  }
  const car = {
    id: nextId,
    x: x0,
    y: y,
    delay: performance.now() + baseDelay + jitter,
    lane: lane,
    color: color,
    merging: false,
    targetY: null
  };
  nextId = nextId + 1;
  cars.push(car);
}

for (let i = 0; i < MAX_TOP; i++) {
  spawn("top", i * 400);
}
for (let i = 0; i < MAX_BOT; i++) {
  spawn("bot", i * 400 + 800);
}

function gapFreeAtMerge(bottomCars) {
  const need = MIN_GAP * 1.1;
  for (let i = 0; i < bottomCars.length; i++) {
    const b = bottomCars[i];
    if (Math.abs(b.x - mergeX) <= need) {
      return false;
    }
  }
  return true;
}

function sortByXDesc(list) {
  for (let i = 0; i < list.length; i++) {
    for (let j = i + 1; j < list.length; j++) {
      if (list[j].x > list[i].x) {
        const temp = list[i];
        list[i] = list[j];
        list[j] = temp;
      }
    }
  }
}

d3.timer(function() {
  const now = performance.now();

  const topWaiting = [];
  for (let i = 0; i < cars.length; i++) {
    const c = cars[i];
    if (c.lane === "top" && c.merging === false) topWaiting.push(c);
  }

  sortByXDesc(topWaiting);

  for (let i = 0; i < topWaiting.length; i++) {
    const c = topWaiting[i];
    if (now < c.delay) {
      continue;
    }
    let leadX;
    if (i === 0) {
      leadX = STOP_X;
    } else {
      const prev = topWaiting[i - 1];
      leadX = prev.x - MIN_GAP;
      if (leadX > STOP_X) {
        leadX = STOP_X;
      }
    }
    const distToLead = leadX - c.x;
    const distBasedSpeed = distToLead * 0.5;
    let speed = vBase;
    if (distBasedSpeed < speed) {
      speed = distBasedSpeed;
    }
    if (speed < SPEED_MIN) {
      speed = SPEED_MIN;
    }
    if (speed > SPEED_MAX) {
      speed = SPEED_MAX;
    }
    const newX = c.x + speed;
    if (newX > leadX) {
      c.x = leadX;
    } else {
      c.x = newX;
    }
    c.y = Y_TOP;
  }

  const bottomAll = [];
  for (let i = 0; i < cars.length; i++) {
    const c = cars[i];
    if (c.lane === "bot") bottomAll.push(c);
  }

  sortByXDesc(bottomAll);

  for (let i = 0; i < bottomAll.length; i++) {
    const c = bottomAll[i];
    if (now < c.delay) {
      continue;
    }
    let speed = vBase;
    if (i > 0) {
      const frontCar = bottomAll[i - 1];
      const distToFront = frontCar.x - c.x;
      const distBasedSpeed = distToFront * 0.5;
      if (distBasedSpeed < speed) {
        speed = distBasedSpeed;
      }
    }
    if (speed < SPEED_MIN) {
      speed = SPEED_MIN;
    }
    if (speed > SPEED_MAX) {
      speed = SPEED_MAX;
    }
    c.x = c.x + speed;
    if (i > 0) {
      const frontCar = bottomAll[i - 1];
      const minDist = frontCar.x - MIN_GAP;
      if (c.x > minDist) {
        c.x = minDist;
      }
    }
  }

  let head = null;
  if (topWaiting.length > 0) {
    head = topWaiting[0];
  }

  if (head !== null) {
    const atStop = Math.abs(head.x - STOP_X) < 1e-6;
    const allBottomCars = [];
    for (let i = 0; i < cars.length; i++) {
      const c = cars[i];
      if (c.lane === "bot" || c.merging === true) allBottomCars.push(c);
    }
    if (atStop && gapFreeAtMerge(allBottomCars)) {
      head.merging = true;
      head.targetY = Y_BOT;
    }
  }

  for (let i = 0; i < cars.length; i++) {
    const c = cars[i];
    if (c.merging === false) {
      continue;
    }
    if (now < c.delay) {
      continue;
    }
    c.x = c.x + vBase;
    const newY = c.y + vMergeY;
    if (newY >= c.targetY) {
      c.y = c.targetY;
      c.merging = false;
      c.lane = "bot";
    } else {
      c.y = newY;
    }
  }

  const outX = W + carW;
  const stillIn = [];
  for (let i = 0; i < cars.length; i++) {
    const c = cars[i];
    if (c.x <= outX) stillIn.push(c);
  }
  cars = stillIn;

  let topCount = 0;
  let botCount = 0;
  for (let i = 0; i < cars.length; i++) {
    const c = cars[i];
    if (c.lane === "top" && c.merging === false) {
      topCount = topCount + 1;
    }
    if (c.lane === "bot") {
      botCount = botCount + 1;
    }
  }

  while (topCount < MAX_TOP) {
    spawn("top");
    topCount = topCount + 1;
  }
  while (botCount < MAX_BOT) {
    spawn("bot", 600);
    botCount = botCount + 1;
  }

  const sel = g.selectAll("rect").data(cars, function(d){ return d.id; });

  sel.exit().remove();

  sel.enter()
    .append("rect")
    .attr("width", carW)
    .attr("height", carH)
    .attr("rx", 4)
    .attr("fill", function(d){ return d.color; })
    .attr("x", function(d){ return Math.round(d.x); })
    .attr("y", function(d){ return d.y; });

  sel
    .attr("fill", function(d){ return d.color; })
    .attr("x", function(d){ return Math.round(d.x); })
    .attr("y", function(d){ return d.y; });
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






