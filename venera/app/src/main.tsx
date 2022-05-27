import ReactDOM from 'react-dom/client'
import Index from './index'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

// <Route element={<NotFound />} />
ReactDOM.createRoot(document.getElementById('app-mount')!).render(
  <BrowserRouter>
    <Routes>
      <Route path='/' element={<Index />} />
    </Routes>
  </BrowserRouter>
)
