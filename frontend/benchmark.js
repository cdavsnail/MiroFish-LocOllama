import { performance } from 'perf_hooks';

// Mock data setup
const numAgents = 1000;
const resultsDict = [];
for (let i = 0; i < numAgents; i++) {
  resultsDict.push({
    agent_id: i,
    response: `Response from agent ${i}`
  });
}

const interviews = [];
for (let i = 0; i < numAgents; i++) {
  interviews.push({ agent_id: i });
}

// Function with inefficiency
function originalLoop() {
  const t0 = performance.now();
  let foundCount = 0;
  for (const interview of interviews) {
    const agentIdx = interview.agent_id;
    const matchedResult = resultsDict.find(r => r.agent_id === agentIdx);
    if (matchedResult) {
      foundCount++;
    }
  }
  const t1 = performance.now();
  return t1 - t0;
}

// Function optimized
function optimizedLoop() {
  const t0 = performance.now();
  let foundCount = 0;

  // Build lookup map before loop
  const resultsMap = new Map();
  for (const r of resultsDict) {
    resultsMap.set(r.agent_id, r);
  }

  for (const interview of interviews) {
    const agentIdx = interview.agent_id;
    const matchedResult = resultsMap.get(agentIdx);
    if (matchedResult) {
      foundCount++;
    }
  }
  const t1 = performance.now();
  return t1 - t0;
}

// Warmup
for (let i=0; i<10; i++) { originalLoop(); optimizedLoop(); }

let originalTotal = 0;
let optimizedTotal = 0;
const iterations = 100;

for (let i = 0; i < iterations; i++) {
  originalTotal += originalLoop();
  optimizedTotal += optimizedLoop();
}

console.log(`Original average: ${originalTotal / iterations} ms`);
console.log(`Optimized average: ${optimizedTotal / iterations} ms`);
console.log(`Speedup: ${(originalTotal / optimizedTotal).toFixed(2)}x`);
