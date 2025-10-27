import http from "k6/http";
import { check, sleep } from "k6";

const msg = "oi vc eh mto legal"

export let options = {
  vus: 1,
  duration: '10s'
};

export default function () {
  const url = "http://localhost:8000/api/enqueue";
  const payload = JSON.stringify({ msg: msg });

  const params = {
    headers: {
      "Content-Type": "application/json"
    }
  };

  const res = http.post(url, payload, params)

  check(res, {
    'is enqueued': (r) => {
      try {
        return res.status === 202;
      } catch (e) {
        return false;
      }
    }
  });

}
