import { useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const helloWorldApi = async () => {
    try {
      const response = await axios.get(`${API}/`);
      console.log(response.data.message);
    } catch (e) {
      console.error(e, `errored out requesting / api`);
    }
  };

  useEffect(() => {
    helloWorldApi();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>OpenHands + Headroom Docker Stack</h1>
        <p className="mt-2">
          This project is Infrastructure as Code. The deliverables live in the
          <code> /app/deliverables </code> directory:
        </p>
        <ul className="mt-2" style={{ textAlign: "left", lineHeight: 1.9 }}>
          <li><code>docker-compose.yml</code></li>
          <li><code>.env.example</code></li>
          <li><code>init.sh</code></li>
          <li><code>.gitignore</code></li>
          <li><code>README.md</code></li>
          <li><code>push_to_github.sh</code></li>
        </ul>
        <p className="mt-4" style={{ fontSize: "1rem", opacity: 0.8 }}>
          Run <code>./init.sh &amp;&amp; docker compose up -d</code>, or publish with
          <code> ./push_to_github.sh &lt;repo-url&gt;</code>.
        </p>
      </header>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}>
            <Route index element={<Home />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
