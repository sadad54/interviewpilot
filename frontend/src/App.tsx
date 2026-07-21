import { Routes, Route } from "react-router-dom";
import StartPage from "./pages/StartPage";
import InterviewPage from "./pages/InterviewPage";
import ResultsPage from "./pages/ResultsPage";
import MockInterviewPage from "./pages/MockInterviewPage";
import InterviewReportPage from "./pages/InterviewReportPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<StartPage />} />
      <Route path="/mock-interview/:publicId" element={<MockInterviewPage />} />
      <Route path="/report/:publicId" element={<InterviewReportPage />} />
      <Route path="/shared-report/:shareToken" element={<InterviewReportPage shared />} />
      <Route path="/interview/:sessionId/:questionId" element={<InterviewPage />} />
      <Route path="/results/:responseId" element={<ResultsPage />} />
    </Routes>
  );
}

export default App;
