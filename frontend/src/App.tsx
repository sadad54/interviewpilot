import { Routes, Route } from "react-router-dom";
import StartPage from "./pages/StartPage";
import InterviewPage from "./pages/InterviewPage";
import ResultsPage from "./pages/ResultsPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<StartPage />} />
      <Route path="/interview/:sessionId/:questionId" element={<InterviewPage />} />
      <Route path="/results/:responseId" element={<ResultsPage />} />
    </Routes>
  );
}

export default App;