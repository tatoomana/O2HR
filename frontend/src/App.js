import { useEffect } from "react";
import "@/App.css";
import { Toaster } from "@/components/ui/sonner";
import Dashboard from "@/pages/Dashboard";

function App() {
  useEffect(() => {
    // Console theme is dark-first
    document.documentElement.classList.add("dark");
  }, []);

  return (
    <div className="App bg-background text-foreground">
      <Dashboard />
      <Toaster theme="dark" position="top-right" richColors closeButton />
    </div>
  );
}

export default App;
