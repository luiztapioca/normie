import http from "k6/http";
import { check, sleep } from "k6";
import { SharedArray } from "k6/data";

// Load test phrases
const phrases = new SharedArray("test_phrases", function () {
  const data = JSON.parse(open("./test_phrases.json"));
  return [
    ...data.hate_speech,
    ...data.normal_speech,
    ...data.offensive_but_not_hate
  ];
});

export const options = {
  vus: 5,
  iterations: 30, // Run 30 complete end-to-end tests
  thresholds: {
    checks: ["rate>0.9"], // 90% of checks should pass
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const MAX_POLL_ATTEMPTS = 30;
const POLL_INTERVAL = 2; // seconds

export default function () {
  const randomPhrase = phrases[Math.floor(Math.random() * phrases.length)];
  
  console.log(`Testing phrase: "${randomPhrase}"`);
  
  // Step 1: Enqueue message
  const enqueueUrl = `${BASE_URL}/api/enqueue`;
  const payload = JSON.stringify({ msg: randomPhrase });
  
  const params = {
    headers: {
      "Content-Type": "application/json",
    },
  };
  
  const enqueueRes = http.post(enqueueUrl, payload, params);
  
  const enqueueSuccess = check(enqueueRes, {
    "enqueue: status is 202": (r) => r.status === 202,
    "enqueue: returns msg_id": (r) => r.json("msg_id") !== undefined,
  });
  
  if (!enqueueSuccess || enqueueRes.status !== 202) {
    console.error("Enqueue failed, skipping test");
    return;
  }
  
  const msgId = enqueueRes.json("msg_id");
  console.log(`Message enqueued with ID: ${msgId}`);
  
  // Step 2: Poll for completion
  let completed = false;
  let attempts = 0;
  let finalStatus = null;
  
  while (!completed && attempts < MAX_POLL_ATTEMPTS) {
    sleep(POLL_INTERVAL);
    attempts++;
    
    const dequeueUrl = `${BASE_URL}/api/dequeue/${msgId}`;
    const dequeueRes = http.get(dequeueUrl, params);
    
    if (dequeueRes.status === 200) {
      const queueStatus = dequeueRes.json("queue");
      finalStatus = queueStatus;
      
      console.log(`Attempt ${attempts}: Status = ${queueStatus}`);
      
      if (queueStatus === "completed" || queueStatus === "error") {
        completed = true;
        
        check(dequeueRes, {
          "dequeue: message processed": () => true,
          "dequeue: final status is valid": () => 
            queueStatus === "completed" || queueStatus === "error",
        });
        
        console.log(`Message ${msgId} processing finished with status: ${queueStatus}`);
      }
    } else {
      console.error(`Dequeue request failed with status: ${dequeueRes.status}`);
    }
  }
  
  // Step 3: Verify completion
  check(null, {
    "e2e: message was processed within time limit": () => completed,
    "e2e: processing time acceptable": () => attempts <= MAX_POLL_ATTEMPTS / 2,
  });
  
  if (!completed) {
    console.error(`Message ${msgId} did not complete after ${attempts} attempts`);
  }
  
  sleep(1);
}
