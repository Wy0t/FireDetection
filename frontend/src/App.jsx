import {BrowserRouter, Routes, Route, Navigate} from "react-router-dom"
import Home from "./pages/Home"
import Test from "./pages/Test"

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="" element={<Home />} />
          <Route path="Test" element={<Test />} />
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
