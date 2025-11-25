import http from "k6/http";
import { check, sleep } from "k6";

const id = "384dfd77-0cdc-44ee-96c8-dc5d310568f7"

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
