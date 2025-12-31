// ============================================================================
// platforms/web/pages/_app.js - Next.js App Component
// ============================================================================

import '../styles/globals.css'
import { AuthProvider } from '../lib/AuthContext'

function MyApp({ Component, pageProps }) {
  return (
    <AuthProvider>
      <Component {...pageProps} />
    </AuthProvider>
  )
}

export default MyApp
