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

// Stress test: push the system beyond normal capacity
export const options = {
  stages: [
    { duration: "2m", target: 50 },   // Ramp up to 50 users
    { duration: "3m", target: 100 },  // Spike to 100 users
    { duration: "2m", target: 150 },  // Push to 150 users
    { duration: "3m", target: 50 },   // Scale down to 50
    { duration: "2m", target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ["p(99)<2000"], // 99% of requests under 2s
    http_req_failed: ["rate<0.3"],     // Less than 30% failure rate
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export default function () {
  const randomPhrase = phrases[Math.floor(Math.random() * phrases.length)];
  
  const enqueueUrl = `${BASE_URL}/api/enqueue`;
  const payload = JSON.stringify({ msg: randomPhrase });
  
  const params = {
    headers: {
      "Content-Type": "application/json",
    },
  };
  
  const enqueueRes = http.post(enqueueUrl, payload, params);
  
  check(enqueueRes, {
    "enqueue: status is 202": (r) => r.status === 202,
  });
  
  // Only check status for some requests to reduce load
  if (enqueueRes.status === 202 && Math.random() < 0.3) {
    const msgId = enqueueRes.json("msg_id");
    sleep(0.2);
    
    const dequeueUrl = `${BASE_URL}/api/dequeue/${msgId}`;
    http.get(dequeueUrl, params);
  }
  
  sleep(0.5);
}
