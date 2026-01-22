import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react'

import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import Setup from './pages/Setup'
import Interview from './pages/Interview'
import Results from './pages/Results'
import ChatInterview from './pages/ChatInterview'

// Placeholder components
const NotFound = () => <div className="p-10">404 - Not Found</div>

function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <Routes>
        <Route path="/" element={<Landing />} />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <>
              <SignedIn>
                <Dashboard />
              </SignedIn>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </>
          }
        />

        <Route
          path="/setup"
          element={
            <>
              <SignedIn>
                <Setup />
              </SignedIn>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </>
          }
        />

        <Route
          path="/interview"
          element={
            <>
              <SignedIn>
                <Interview />
              </SignedIn>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </>
          }
        />

        <Route
          path="/results"
          element={
            <>
              <SignedIn>
                <Results />
              </SignedIn>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </>
          }
        />

        <Route
          path="/chat"
          element={
            <>
              <SignedIn>
                <ChatInterview />
              </SignedIn>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </>
          }
        />

        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  )
}

export default App
