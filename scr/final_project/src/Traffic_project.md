# Lane Merging Before a Traffic Light: Late vs Early Merge

---
## Story

On many multi-lane roads, two lanes have to merge into a single lane just before a traffic light.  
Some drivers merge early, while others stay in their lane until the very last moment and cut in near the front.

This mixture of behaviors often leads to:
- sudden braking,
- hesitation and confusion,
- and long queues right before the light.

In this project, I simulate two different strategies:

- 🔴 Late Merge – drivers stay in two lanes almost to the end, then merge near the light.
- 🟢 Early Merge – drivers are “encouraged” to merge earlier, so a single lane forms before the intersection.

The main question is:

> If drivers merge earlier, do we actually see smoother traffic and less waiting?

---

## Overview

This animation focuses on simple, intuitive driving behavior rather than a full traffic engineering model.

In both scenarios:

- Cars speed up when the road ahead is clear.  
- Cars slow down when they approach another car or a red light.  
- Cars in the top lane only merge when there is a safe gap in the bottom lane.  
- Whenever a car is crawling or stopped, that time is counted as waiting time.

By comparing the two scenarios side by side, under the same traffic flow and the same traffic light,  
we can visually inspect:

- where queues form,
- how long cars tend to wait,
- and how late vs early merging changes the traffic pattern.

```js
const SPAWN_RATE = Inputs.range([0.5, 5], { 
  step: 0.1, 
  value: 1.2, 
  label: "Traffic Flow (cars/sec)" 
});

const SPEED_MIN = Inputs.range([0.1, 1.5], { 
  step: 0.05, 
  value: 0.5, 
  label: "Minimum Speed" 
});

const SPEED_MAX = Inputs.range([0.5, 3.0], { 
  step: 0.05, 
  value: 1.8, 
  label: "Maximum Speed" 
});

```

```js
const LIGHT_GREEN_TIME = 4;
const LIGHT_RED_TIME = 3;
```

## Statistics Panels

Below are two live statistics panels that summarize what is happening in each scenario:

- The red box tracks the 🔴 Late Merge case.  
- The green box tracks the 🟢 Early Merge case.

Each panel reports:

- **Passed Through** – how many cars have successfully exited the system.  
- **Avg Wait Time** – on average, how many seconds each car spent moving slowly or stopped.

These numbers give a quick sense of how much delay drivers experience under each strategy.


```js
const statsDiv = d3.create("div")
  .style("display", "flex")
  .style("gap", "20px")
  .style("margin", "20px 0")
  .style("font-family", "monospace");

const stats1 = statsDiv.append("div")
  .style("border", "2px solid #ef4444")
  .style("padding", "15px")
  .style("border-radius", "8px")
  .style("flex", "1");

stats1.append("h4")
  .style("margin", "0 0 10px 0")
  .text("📊 Late Merge Statistics");

const stats1Content = stats1.append("div");

const stats2 = statsDiv.append("div")
  .style("border", "2px solid #22c55e")
  .style("padding", "15px")
  .style("border-radius", "8px")
  .style("flex", "1");

stats2.append("h4")
  .style("margin", "0 0 10px 0")
  .text("📊 Early Merge Statistics");

const stats2Content = stats2.append("div");

display(statsDiv.node());
```

```js
const W = 700;
const H = 220;
const topY = 60;
const botY = 160;
const midY = (topY + botY) / 2;

const container = d3.create("div");
container.append("h3").text("🔴 Late Merge");
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
const STOP_X = mergeX - 60;

svg.append("line")
  .attr("x1", mergeX).attr("x2", mergeX)
  .attr("y1", topY - 20).attr("y2", midY + 20)
  .attr("stroke", "#ef4444").attr("stroke-width", 3);

const trafficLightX = W - 80;
const trafficLight = svg.append("circle")
  .attr("cx", trafficLightX)
  .attr("cy", midY)
  .attr("r", 15)
  .attr("fill", "#ef4444")
  .attr("stroke", "#333")
  .attr("stroke-width", 2);

svg.append("line")
  .attr("x1", trafficLightX)
  .attr("x2", trafficLightX)
  .attr("y1", midY - 40)
  .attr("y2", midY + 40)
  .attr("stroke", "#ef4444")
  .attr("stroke-width", 4)
  .attr("stroke-dasharray", "5,5");

svg.append("text")
  .attr("x", trafficLightX)
  .attr("y", midY + 55)
  .attr("text-anchor", "middle")
  .attr("font-size", "12px")
  .attr("fill", "#333")
  .text("Traffic Light");

const carW = 50;
const carH = 35;
const carGap = 15;
const vMergeY = 0.8;
const MIN_GAP = carW + carGap;
const Y_TOP = topY + 6;
const Y_BOT = midY + 6;

let nextId = 1;
let cars = [];
const g = svg.append("g");

let lightIsGreen = false;
let lightChangeTime = performance.now() + LIGHT_RED_TIME * 1000;

let stats = {
  totalSpawned: 0,
  totalPassed: 0,
  totalWaitTime: 0,
  carCount: 0,
  avgSpeed: 0,
  queueLength: 0
};

let lastSpawnTime = performance.now();

function spawn(lane) {
  const x0 = -(carW + carGap) - Math.random() * 30;
  const y = lane === "top" ? Y_TOP : Y_BOT;
  const color = lane === "top" ? "#4F8EF7" : "#F4A261";
  const baseSpeed = SPEED_MIN.value + Math.random() * (SPEED_MAX.value - SPEED_MIN.value);
  
  cars.push({
    id: nextId++,
    x: x0,
    y: y,
    lane: lane,
    color: color,
    merging: false,
    targetY: null,
    baseSpeed: baseSpeed,
    spawnTime: performance.now(),
    stoppedTime: 0,
    lastStoppedStart: null,
    waitingToMerge: false
  });
  
  stats.totalSpawned++;
}

function sortByXDesc(list) {
  list.sort((a, b) => b.x - a.x);
}

const timer1 = d3.timer(() => {
  const now = performance.now();

  const spawnInterval = 1000 / SPAWN_RATE.value;
  if (now - lastSpawnTime >= spawnInterval) {
    spawn(Math.random() < 0.5 ? "top" : "bot");
    lastSpawnTime = now;
  }

  if (now >= lightChangeTime) {
    lightIsGreen = !lightIsGreen;
    trafficLight.attr("fill", lightIsGreen ? "#22c55e" : "#ef4444");
    lightChangeTime = now + (lightIsGreen ? LIGHT_GREEN_TIME : LIGHT_RED_TIME) * 1000;
  }

  const topWaiting = cars.filter(c => c.lane === "top" && !c.merging);
  sortByXDesc(topWaiting);

  for (let i = 0; i < topWaiting.length; i++) {
    const c = topWaiting[i];
    
    let stopLine = STOP_X;
    if (c.waitingToMerge && i === 0) {
      stopLine = STOP_X - 8;
    }
    
    const leadX = i === 0 ? stopLine : Math.min(topWaiting[i - 1].x - MIN_GAP, stopLine);
    const dist = leadX - c.x;
    
    let speed = c.baseSpeed;
    if (dist < MIN_GAP * 2) {
      speed = Math.min(speed, Math.max(0.1, dist * 0.02));
    }
    if (dist > MIN_GAP * 3 && !c.waitingToMerge) {
      speed = SPEED_MAX.value;
    }
    
    if (speed < 0.2) {
      if (c.lastStoppedStart === null) c.lastStoppedStart = now;
    } else {
      if (c.lastStoppedStart !== null) {
        c.stoppedTime += now - c.lastStoppedStart;
        c.lastStoppedStart = null;
      }
    }
    
    speed = Math.max(SPEED_MIN.value, Math.min(SPEED_MAX.value, speed));
    c.x = Math.min(c.x + speed, leadX);
  }

const bottomAll = cars.filter(c => c.lane === "bot" || c.merging);
sortByXDesc(bottomAll);
const stopLine = trafficLightX - carW;

for (let i = 0; i < bottomAll.length; i++) {
  const c = bottomAll[i];
  let speed = c.baseSpeed;
  let targetX = W + carW * 2;

  let distFront = Infinity;
  if (i > 0) {
    const front = bottomAll[i - 1];
    distFront = front.x - c.x;
    targetX = Math.min(targetX, front.x - MIN_GAP);

    if (distFront < MIN_GAP * 2) {
      speed = Math.min(speed, Math.max(0.1, distFront * 0.02));
    }
  }

  const mergingAhead = cars.filter(c2 => 
    c2.merging && c2.x > c.x && c2.x < c.x + MIN_GAP * 3
  );
  if (mergingAhead.length > 0) {
    speed = Math.min(speed, 0.2);
    targetX = Math.min(targetX, mergingAhead[0].x - MIN_GAP);
  }

  if (!lightIsGreen && c.x < stopLine) {
    const distLight = stopLine - c.x;
    targetX = Math.min(targetX, stopLine);

    if (distLight < 2) {
      speed = 0;
    } else if (distLight < 30) {
      speed = Math.min(speed, distLight * 0.15);
    } else {
      speed = Math.min(speed, distLight * 0.25);
    }
  }

  const inMergeToLight = c.x >= mergeX && c.x < stopLine - 10;
  if (inMergeToLight && distFront > MIN_GAP * 1.5) {
    const targetSpeed = Math.max(c.baseSpeed, SPEED_MAX.value * 0.9);
    speed = Math.min(SPEED_MAX.value, Math.max(speed, targetSpeed));
  }

  if (speed < 0.2) {
    if (c.lastStoppedStart === null) {
      c.lastStoppedStart = now;
    }
  } else {
    if (c.lastStoppedStart !== null) {
      c.stoppedTime += now - c.lastStoppedStart;
      c.lastStoppedStart = null;
    }
  }

  if (lightIsGreen || c.x >= stopLine) {
    if (speed > 0) {
      speed = Math.max(SPEED_MIN.value, Math.min(SPEED_MAX.value, speed));
    }
  } else {
    if (speed > 0) {
      speed = Math.min(SPEED_MAX.value, speed);
    }
  }

  c.x = Math.min(c.x + speed, targetX);
}

  const head = topWaiting[0];
  if (head && head.x >= STOP_X - 10 && !head.merging) {
    const allBottomAsc = cars
      .filter(c => c.lane === "bot" || c.merging)
      .slice()
      .sort((a, b) => a.x - b.x);

    const ahead = allBottomAsc.find(b => b.x > head.x);
    const behind = [...allBottomAsc].reverse().find(b => b.x < head.x);

    const safeAhead = !ahead || (ahead.x - head.x > MIN_GAP);
    const safeBehind = !behind || (head.x - behind.x > MIN_GAP);

    if (safeAhead && safeBehind) {
      head.merging = true;
      head.targetY = Y_BOT;
      head.waitingToMerge = false;
    } else {
      head.waitingToMerge = true;
    }
  }

  cars.forEach(c => {
    if (!c.merging) return;
    c.x += c.baseSpeed;
    c.y += vMergeY;
    if (c.y >= c.targetY) {
      c.y = c.targetY;
      c.merging = false;
      c.lane = "bot";
      c.waitingToMerge = false;
    }
  });

  const leaving = cars.filter(c => c.x > W + carW);
  leaving.forEach(c => {
    stats.totalWaitTime += c.stoppedTime / 1000;
    stats.totalPassed++;
  });
  cars = cars.filter(c => c.x <= W + carW);

  stats.carCount = cars.length;
  stats.queueLength = topWaiting.filter(c => c.x < STOP_X - 10).length;
  const avgWait = stats.totalPassed > 0 ? (stats.totalWaitTime / stats.totalPassed).toFixed(1) : 0;

  stats1Content.html(`
    Passed Through: ${stats.totalPassed} cars<br>
    Avg Wait Time: ${avgWait} sec
  `);


  const sel = g.selectAll("rect").data(cars, d => d.id);
  sel.exit().remove();
  sel.enter()
    .append("rect")
    .attr("width", carW)
    .attr("height", carH)
    .attr("rx", 4)
    .merge(sel)
    .attr("fill", d => d.color)
    .attr("x", d => Math.round(d.x))
    .attr("y", d => d.y);
});

invalidation.then(() => timer1.stop());
```

```js
const W2 = 700;
const H2 = 220;
const topY2 = 60;
const botY2 = 160;
const midY2 = (topY2 + botY2) / 2;

const container2 = d3.create("div");
container2.append("h3").text("🟢 Early Merge");
display(container2.node());

const svg2 = container2.append("svg")
  .attr("width", W2)
  .attr("height", H2)
  .style("background", "#f8fafc");

svg2.append("line")
  .attr("x1", 20).attr("x2", W2 - 20)
  .attr("y1", topY2).attr("y2", topY2)
  .attr("stroke", "#94a3b8").attr("stroke-width", 4);

svg2.append("line")
  .attr("x1", 20).attr("x2", W2 - 20)
  .attr("y1", botY2).attr("y2", botY2)
  .attr("stroke", "#94a3b8").attr("stroke-width", 4);

svg2.append("line")
  .attr("x1", 20).attr("x2", W2 - 20)
  .attr("y1", midY2).attr("y2", midY2)
  .attr("stroke", "#cbd5e1").attr("stroke-width", 2)
  .attr("stroke-dasharray", "10,10");

const mergeX2 = Math.floor(W2 / 3);
const STOP_X2 = mergeX2 - 60;

svg2.append("line")
  .attr("x1", mergeX2).attr("x2", mergeX2)
  .attr("y1", topY2 - 20).attr("y2", midY2 + 20)
  .attr("stroke", "#22c55e").attr("stroke-width", 3);

const trafficLightX2 = W2 - 80;
const trafficLight2 = svg2.append("circle")
  .attr("cx", trafficLightX2)
  .attr("cy", midY2)
  .attr("r", 15)
  .attr("fill", "#ef4444")
  .attr("stroke", "#333")
  .attr("stroke-width", 2);

svg2.append("line")
  .attr("x1", trafficLightX2)
  .attr("x2", trafficLightX2)
  .attr("y1", midY2 - 40)
  .attr("y2", midY2 + 40)
  .attr("stroke", "#ef4444")
  .attr("stroke-width", 4)
  .attr("stroke-dasharray", "5,5");

svg2.append("text")
  .attr("x", trafficLightX2)
  .attr("y", midY2 + 55)
  .attr("text-anchor", "middle")
  .attr("font-size", "12px")
  .attr("fill", "#333")
  .text("Traffic Light");

const carW2 = 50;
const carH2 = 35;
const MIN_GAP2 = carW2 + 15;
const Y_TOP2 = topY2 + 6;
const Y_BOT2 = midY2 + 6;

let nextId2 = 1;
let cars2 = [];
const g2 = svg2.append("g");

let lightIsGreen2 = false;
let lightChangeTime2 = performance.now() + LIGHT_RED_TIME * 1000;

let stats2 = {
  totalSpawned: 0,
  totalPassed: 0,
  totalWaitTime: 0,
  carCount: 0,
  avgSpeed: 0,
  queueLength: 0
};

let lastSpawnTime2 = performance.now();

function spawn2(lane) {
  const x0 = -(carW2 + 15) - Math.random() * 30;
  const y = lane === "top" ? Y_TOP2 : Y_BOT2;
  const color = lane === "top" ? "#4F8EF7" : "#F4A261";
  const baseSpeed = SPEED_MIN.value + Math.random() * (SPEED_MAX.value - SPEED_MIN.value);
  
  cars2.push({
    id: nextId2++,
    x: x0,
    y: y,
    lane: lane,
    color: color,
    merging: false,
    targetY: null,
    baseSpeed: baseSpeed,
    spawnTime: performance.now(),
    stoppedTime: 0,
    lastStoppedStart: null,
    waitingToMerge: false
  });
  
  stats2.totalSpawned++;
}

const timer2 = d3.timer(() => {
  const now = performance.now();

  const spawnInterval = 1000 / SPAWN_RATE.value;
  if (now - lastSpawnTime2 >= spawnInterval) {
    spawn2(Math.random() < 0.5 ? "top" : "bot");
    lastSpawnTime2 = now;
  }

  if (now >= lightChangeTime2) {
    lightIsGreen2 = !lightIsGreen2;
    trafficLight2.attr("fill", lightIsGreen2 ? "#22c55e" : "#ef4444");
    lightChangeTime2 = now + (lightIsGreen2 ? LIGHT_GREEN_TIME : LIGHT_RED_TIME) * 1000;
  }

  const topWaiting = cars2.filter(c => c.lane === "top" && !c.merging);
  topWaiting.sort((a, b) => b.x - a.x);

  for (let i = 0; i < topWaiting.length; i++) {
    const c = topWaiting[i];
    
    let stopLine = STOP_X2;
    if (c.waitingToMerge && i === 0) {
      stopLine = STOP_X2 - 5;
    }
    
    const leadX = i === 0 ? stopLine : Math.min(topWaiting[i - 1].x - MIN_GAP2, stopLine);
    const dist = leadX - c.x;
    
    let speed = c.baseSpeed;
    if (dist < MIN_GAP2 * 2) {
      speed = Math.min(speed, Math.max(0.1, dist * 0.02));
    }
    
    if (speed < 0.2) {
      if (c.lastStoppedStart === null) c.lastStoppedStart = now;
    } else {
      if (c.lastStoppedStart !== null) {
        c.stoppedTime += now - c.lastStoppedStart;
        c.lastStoppedStart = null;
      }
    }
    
    speed = Math.max(SPEED_MIN.value, Math.min(SPEED_MAX.value, speed));
    c.x = Math.min(c.x + speed, leadX);
  }

const bottomAll = cars2.filter(c => c.lane === "bot" || c.merging);
bottomAll.sort((a, b) => b.x - a.x);
const stopLine2 = trafficLightX2 - carW2;

for (let i = 0; i < bottomAll.length; i++) {
  const c = bottomAll[i];
  let speed = c.baseSpeed;
  let targetX = W2 + carW2 * 2;

  let distFront = Infinity;
  if (i > 0) {
    const front = bottomAll[i - 1];
    distFront = front.x - c.x;
    targetX = Math.min(targetX, front.x - MIN_GAP2);

    if (distFront < MIN_GAP2 * 2) {
      speed = Math.min(speed, Math.max(0.1, distFront * 0.02));
    }
  }

  const mergingAhead = cars2.filter(c2 => 
    c2.merging && c2.x > c.x && c2.x < c.x + MIN_GAP2 * 3
  );
  if (mergingAhead.length > 0) {
    speed = Math.min(speed, 0.8);
  }

  if (!lightIsGreen2 && c.x < stopLine2) {
    const distLight = stopLine2 - c.x;
    targetX = Math.min(targetX, stopLine2);

    if (distLight < 2) {
      speed = 0;
    } else if (distLight < 30) {
      speed = Math.min(speed, distLight * 0.15);
    } else {
      speed = Math.min(speed, distLight * 0.25);
    }
  }

  const inMergeToLight2 = c.x >= mergeX2 && c.x < stopLine2 - 10;
  if (inMergeToLight2 && distFront > MIN_GAP2 * 1.5) {
    const targetSpeed = Math.max(c.baseSpeed, SPEED_MAX.value * 0.9);
    speed = Math.min(SPEED_MAX.value, Math.max(speed, targetSpeed));
  }

  if (speed < 0.2) {
    if (c.lastStoppedStart === null) c.lastStoppedStart = now;
  } else {
    if (c.lastStoppedStart !== null) {
      c.stoppedTime += now - c.lastStoppedStart;
      c.lastStoppedStart = null;
    }
  }

  if (lightIsGreen2 || c.x >= stopLine2) {
    if (speed > 0) {
      speed = Math.max(SPEED_MIN.value, Math.min(SPEED_MAX.value, speed));
    }
  } else {
    if (speed > 0) {
      speed = Math.min(SPEED_MAX.value, speed);
    }
  }

  c.x = Math.min(c.x + speed, targetX);
}


  const head = topWaiting[0];
  if (head && head.x >= STOP_X2 - 10) {
    if (!head.merging && !head.waitingToMerge) {
      const allBottom = cars2.filter(c => c.lane === "bot" || c.merging);
      
      const mergeZoneClear = !allBottom.some(b => 
        Math.abs(b.x - mergeX2) < MIN_GAP2 * 1.2
      );
      
      if (mergeZoneClear) {
        head.merging = true;
        head.targetY = Y_BOT2;
        head.waitingToMerge = false;
      } else {
        head.waitingToMerge = true;
      }
    } else if (head.waitingToMerge && !head.merging) {
      const allBottom = cars2.filter(c => c.lane === "bot" || c.merging);
      const mergeZoneClear = !allBottom.some(b => 
        Math.abs(b.x - mergeX2) < MIN_GAP2 * 1.2
      );
      
      if (mergeZoneClear) {
        head.merging = true;
        head.targetY = Y_BOT2;
        head.waitingToMerge = false;
      }
    }
  }

  cars2.forEach(c => {
    if (!c.merging) return;
    c.x += c.baseSpeed;
    c.y += 0.8;
    if (c.y >= c.targetY) {
      c.y = c.targetY;
      c.merging = false;
      c.lane = "bot";
      c.waitingToMerge = false;
    }
  });

  const leaving = cars2.filter(c => c.x > W2 + carW2);
  leaving.forEach(c => {
    const totalTime = (now - c.spawnTime) / 1000;
    stats2.totalWaitTime += c.stoppedTime / 1000;
    stats2.totalPassed++;
  });
  
  cars2 = cars2.filter(c => c.x <= W2 + carW2);

  stats2.carCount = cars2.length;
  stats2.queueLength = topWaiting.filter(c => c.x < STOP_X2 - 10).length;
  
  const avgWait = stats2.totalPassed > 0 ? (stats2.totalWaitTime / stats2.totalPassed).toFixed(1) : 0;
  const throughput = stats2.totalPassed;
  
  stats2Content.html(`
    Passed Through: ${stats2.totalPassed} cars<br>
    Avg Wait Time: ${avgWait} sec
  `);


  const sel = g2.selectAll("rect").data(cars2, d => d.id);
  sel.exit().remove();
  sel.enter()
    .append("rect")
    .attr("width", carW2)
    .attr("height", carH2)
    .attr("rx", 4)
    .merge(sel)
    .attr("fill", d => d.color)
    .attr("x", d => Math.round(d.x))
    .attr("y", d => d.y);
});

invalidation.then(() => timer2.stop());
```
```js
display(SPAWN_RATE);
display(SPEED_MIN);
display(SPEED_MAX);
```

## Controls

At the bottom of the page, you can adjust the inputs that feed both scenarios:

- **Traffic Flow (cars/sec)** – how many cars enter per second.  
- **Minimum Speed / Maximum Speed** – the range of comfortable driving speeds.

Both the 🔴 Late Merge and 🟢 Early Merge animations respond to the **same** slider values,  
so changing these controls lets you see how each strategy behaves under identical conditions.
