import { Route, Routes } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import UploadPage from "./pages/UploadPage";
import AnalysisPage from "./pages/AnalysisPage";
import ResultsPage from "./pages/ResultsPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/upload" element={<UploadPage />} />
      <Route path="/analysis/:jobId" element={<AnalysisPage />} />
      <Route path="/results/:jobId" element={<ResultsPage />} />
    </Routes>
  );
}

export default App;

