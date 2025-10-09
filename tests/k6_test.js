import http from "k6/http";
import { check, sleep } from "k6";

const social_texts = ["vc ta ocupado?"];

export let options = {
  vus: 10,
  duration: "30s",
};

export default function () {
  const i = __ITER % social_texts.length;
  const payload = JSON.stringify({ msg: social_texts[i] });

  const params = {
    headers: { "Content-Type": "application/json" },
  };

  const res = http.post("http://127.0.0.1:8000/api/normalise", payload, params);

  check(res, {
    "status is 200": (r) => r.status === 200,
    "result exists": (r) => JSON.parse(r.body).result !== undefined,
  });
}
