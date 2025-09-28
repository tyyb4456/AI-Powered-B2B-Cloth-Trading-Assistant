import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

import { RouterProvider } from 'react-router/dom'
import { createBrowserRouter } from "react-router"

import { AppProvider } from './context/AppContext'
import Layout from "./Layout"
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Suppliers from './pages/Suppliers'
import Quotes from './pages/Quotes'
import Negotiations from './pages/Negotiations'
import Contracts from './pages/Contracts'

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: "",
        element: <Dashboard />
      },
      {
        path: "chat",
        element: <Chat />
      },
      {
        path: "chat/:sessionId",
        element: <Chat />
      },
      {
        path: "suppliers",
        element: <Suppliers />
      },
      {
        path: "suppliers/:sessionId",
        element: <Suppliers />
      },
      {
        path: "quotes",
        element: <Quotes />
      },
      {
        path: "quotes/:sessionId",
        element: <Quotes />
      },
      {
        path: "negotiations",
        element: <Negotiations />
      },
      {
        path: "negotiations/:sessionId",
        element: <Negotiations />
      },
      {
        path: "contracts",
        element: <Contracts />
      },
      {
        path: "contracts/:sessionId",
        element: <Contracts />
      }
    ]
  }
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppProvider>
      <RouterProvider router={router} />
    </AppProvider>
  </StrictMode>,
)