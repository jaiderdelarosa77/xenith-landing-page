import { auth } from "@/auth"

export default auth((req) => {
  const isLoggedIn = !!req.auth
  const { pathname } = req.nextUrl

  // Protect dashboard routes
  if (pathname.startsWith('/dashboard') && !isLoggedIn) {
    return Response.redirect(new URL('/login', req.url))
  }

  // Redirect authenticated users away from login page
  if (pathname === '/login' && isLoggedIn) {
    return Response.redirect(new URL('/dashboard', req.url))
  }
})

export const config = {
  matcher: ['/dashboard/:path*', '/login'],
}
