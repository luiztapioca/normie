import http from "k6/http";
import { check, sleep } from "k6";

const id = "22c4a005-e410-4e89-95b6-73f3b40d3797"

// export let options = {
//   vus: 1,
//   duration: '1s'
// };

export default function () {
  const url = `http://localhost:8000/api/dequeue/${id}`;

  const params = {
    headers: {
      "Content-Type": "application/json"
    }
  };

  const res = http.get(url, params)

//   console.log(res.json().msg_id)

//   check(res, {
//     'is enqueued': (r) => {
//       try {
//         return res.status === 202;
//       } catch (e) {
//         return false;
//       }
//     }
//   });
}
