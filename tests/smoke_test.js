import http from "k6/http";
import { check, sleep } from "k6";

// Smoke test: minimal load to verify basic functionality
export const options = {
  vus: 1,
  duration: "1m",
  thresholds: {
    http_req_failed: ["rate<0.01"], // Less than 1% of requests should fail
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

const testPhrases = [
  "Olá, como você está?",
  "Esse discurso é inaceitável e ofensivo",
  "A diversidade nos torna mais fortes",
];

export default function () {
  const phrase = testPhrases[__ITER % testPhrases.length];
  
  // Test enqueue endpoint
  const enqueueUrl = `${BASE_URL}/api/enqueue`;
  const payload = JSON.stringify({ msg: phrase });
  
  const params = {
    headers: {
      "Content-Type": "application/json",
    },
  };
  
  const enqueueRes = http.post(enqueueUrl, payload, params);
  
  check(enqueueRes, {
    "enqueue: status is 202": (r) => r.status === 202,
    "enqueue: response time < 200ms": (r) => r.timings.duration < 200,
    "enqueue: returns msg_id": (r) => r.json("msg_id") !== undefined,
  });
  
  if (enqueueRes.status === 202) {
    const msgId = enqueueRes.json("msg_id");
    
    // Test dequeue endpoint
    const dequeueUrl = `${BASE_URL}/api/dequeue/${msgId}`;
    const dequeueRes = http.get(dequeueUrl, params);
    
    check(dequeueRes, {
      "dequeue: status is 200": (r) => r.status === 200,
      "dequeue: response time < 100ms": (r) => r.timings.duration < 100,
      "dequeue: has valid queue status": (r) => {
        const queue = r.json("queue");
        return ["pending", "completed", "error"].includes(queue);
      },
    });
  }
  
  sleep(1);
}
