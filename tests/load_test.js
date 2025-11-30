import http from "k6/http";
import { check, sleep } from "k6";
import { SharedArray } from "k6/data";

// Load test phrases from JSON file
const phrases = new SharedArray("test_phrases", function () {
  const data = JSON.parse(open("./test_phrases.json"));
  
  // Combine all phrase types into a single array
  const allPhrases = [
    ...data.hate_speech,
    ...data.normal_speech,
    ...data.offensive_but_not_hate
  ];
  
  return allPhrases;
});

export const options = {
  stages: [
    { duration: "30s", target: 10 },  // Ramp up to 10 users
    { duration: "1m", target: 20 },   // Stay at 20 users
    { duration: "30s", target: 0 },   // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"], // 95% of requests should be below 500ms
    http_req_failed: ["rate<0.1"],    // Less than 10% of requests should fail
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export default function () {
  // Select a random phrase
  const randomPhrase = phrases[Math.floor(Math.random() * phrases.length)];
  
  // Enqueue the message
  const enqueueUrl = `${BASE_URL}/api/enqueue`;
  const payload = JSON.stringify({ msg: randomPhrase });
  
  const params = {
    headers: {
      "Content-Type": "application/json",
    },
  };
  
  const enqueueRes = http.post(enqueueUrl, payload, params);
  
  const enqueueCheck = check(enqueueRes, {
    "enqueue: status is 202": (r) => r.status === 202,
    "enqueue: has msg_id": (r) => r.json("msg_id") !== undefined,
  });
  
  if (enqueueCheck && enqueueRes.status === 202) {
    const msgId = enqueueRes.json("msg_id");
    
    // Wait a bit before checking status
    sleep(0.5);
    
    // Dequeue/check status
    const dequeueUrl = `${BASE_URL}/api/dequeue/${msgId}`;
    const dequeueRes = http.get(dequeueUrl, params);
    
    check(dequeueRes, {
      "dequeue: status is 200": (r) => r.status === 200,
      "dequeue: has queue status": (r) => r.json("queue") !== undefined,
      "dequeue: msg_id matches": (r) => r.json("msg_id") === msgId,
    });
  }
  
  sleep(1);
}
