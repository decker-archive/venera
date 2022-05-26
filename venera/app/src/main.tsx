import ReactDOM from 'react-dom/client'
import App from './App'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

// <Route element={<NotFound />} />
ReactDOM.createRoot(document.getElementById('zen')!).render(
  <BrowserRouter>
    <Routes>
      <Route path='/' element={<App />} />
    </Routes>
  </BrowserRouter>
)
