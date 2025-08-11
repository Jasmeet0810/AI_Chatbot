// import { useState, useEffect, createContext, useContext } from 'react'
// import { supabase } from '../lib/supabase'
// import type { User } from '@supabase/supabase-js'

// interface AuthContextType {
//   user: User | null
//   loading: boolean
//   signUp: (email: string, password: string, fullName: string) => Promise<{ success: boolean; message: string; needsVerification?: boolean }>
//   signIn: (email: string, password: string) => Promise<{ success: boolean; message: string }>
//   signOut: () => Promise<void>
//   verifyOTP: (email: string, otp: string) => Promise<{ success: boolean; message: string }>
//   resendOTP: (email: string) => Promise<{ success: boolean; message: string }>
// }

// const AuthContext = createContext<AuthContextType | undefined>(undefined)

// export const useAuth = () => {
//   const context = useContext(AuthContext)
//   if (context === undefined) {
//     throw new Error('useAuth must be used within an AuthProvider')
//   }
//   return context
// }

// export const useAuthProvider = () => {
//   const [user, setUser] = useState<User | null>(null)
//   const [loading, setLoading] = useState(true)

//   useEffect(() => {
//     // Get initial session
//     supabase.auth.getSession().then(({ data: { session } }) => {
//       setUser(session?.user ?? null)
//       setLoading(false)
//     })

//     // Listen for auth changes
//     const { data: { subscription } } = supabase.auth.onAuthStateChange(
//       async (event, session) => {
//         setUser(session?.user ?? null)
//         setLoading(false)
//       }
//     )

//     return () => subscription.unsubscribe()
//   }, [])

//   const validateEmail = (email: string): boolean => {
//     const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
//     return emailRegex.test(email)
//   }

//   const validatePassword = (password: string): { valid: boolean; message: string } => {
//     if (password.length < 12) {
//       return { valid: false, message: 'Password must be at least 12 characters long' }
//     }
//     if (!/[A-Z]/.test(password)) {
//       return { valid: false, message: 'Password must contain at least 1 uppercase letter' }
//     }
//     if (!/[0-9]/.test(password)) {
//       return { valid: false, message: 'Password must contain at least 1 number' }
//     }
//     if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
//       return { valid: false, message: 'Password must contain at least 1 special character' }
//     }
//     return { valid: true, message: '' }
//   }

//   const generateOTP = (): string => {
//     return Math.floor(100000 + Math.random() * 900000).toString()
//   }

//   const signUp = async (email: string, password: string, fullName: string) => {
//     try {
//       // Validate email
//       if (!validateEmail(email)) {
//         return { success: false, message: 'Please enter a valid email address' }
//       }

//       // Validate password
//       const passwordValidation = validatePassword(password)
//       if (!passwordValidation.valid) {
//         return { success: false, message: passwordValidation.message }
//       }

//       // Check if user already exists
//       const { data: existingUser } = await supabase
//         .from('users')
//         .select('email, email_verified')
//         .eq('email', email)
//         .single()

//       if (existingUser) {
//         if (existingUser.email_verified) {
//           return { success: false, message: 'Account already exists. Please sign in.' }
//         } else {
//           // User exists but not verified, resend OTP
//           const otp = generateOTP()
//           const expiresAt = new Date(Date.now() + 10 * 60 * 1000).toISOString() // 10 minutes

//           await supabase
//             .from('otp_verifications')
//             .upsert({
//               email,
//               otp_code: otp,
//               expires_at: expiresAt,
//               verified: false
//             })

//           // In a real app, send email here
//           console.log(`OTP for ${email}: ${otp}`)
          
//           return { 
//             success: true, 
//             message: 'Verification code sent to your email. Please check your inbox.',
//             needsVerification: true 
//           }
//         }
//       }

//       // Create new user account with Supabase Auth
//       const { data: authData, error: authError } = await supabase.auth.signUp({
//         email,
//         password,
//         options: {
//           data: {
//             full_name: fullName
//           }
//         }
//       })

//       if (authError) {
//         return { success: false, message: authError.message }
//       }

//       // Generate and store OTP
//       const otp = generateOTP()
//       const expiresAt = new Date(Date.now() + 10 * 60 * 1000).toISOString()

//       await supabase
//         .from('otp_verifications')
//         .insert({
//           email,
//           otp_code: otp,
//           expires_at: expiresAt,
//           verified: false
//         })

//       // In a real app, send email here
//       console.log(`OTP for ${email}: ${otp}`)

//       return { 
//         success: true, 
//         message: 'Account created! Verification code sent to your email.',
//         needsVerification: true 
//       }

//     } catch (error) {
//       console.error('Sign up error:', error)
//       return { success: false, message: 'An error occurred during sign up' }
//     }
//   }

//   const signIn = async (email: string, password: string) => {
//     try {
//       if (!validateEmail(email)) {
//         return { success: false, message: 'Please enter a valid email address' }
//       }

//       const { data, error } = await supabase.auth.signInWithPassword({
//         email,
//         password
//       })

//       if (error) {
//         if (error.message.includes('Invalid login credentials')) {
//           // Check if user exists but is not verified
//           const { data: userData } = await supabase
//             .from('users')
//             .select('email_verified')
//             .eq('email', email)
//             .single()

//           if (userData && !userData.email_verified) {
//             return { success: false, message: 'Please verify your email first. Check your inbox for the verification code.' }
//           }
          
//           return { success: false, message: 'Invalid email or password' }
//         }
//         return { success: false, message: error.message }
//       }

//       return { success: true, message: 'Successfully signed in!' }

//     } catch (error) {
//       console.error('Sign in error:', error)
//       return { success: false, message: 'An error occurred during sign in' }
//     }
//   }

//   const verifyOTP = async (email: string, otp: string) => {
//     try {
//       // Get OTP record
//       const { data: otpData, error: otpError } = await supabase
//         .from('otp_verifications')
//         .select('*')
//         .eq('email', email)
//         .eq('otp_code', otp)
//         .eq('verified', false)
//         .single()

//       if (otpError || !otpData) {
//         return { success: false, message: 'Invalid or expired verification code' }
//       }

//       // Check if OTP is expired
//       if (new Date() > new Date(otpData.expires_at)) {
//         return { success: false, message: 'Verification code has expired. Please request a new one.' }
//       }

//       // Mark OTP as verified
//       await supabase
//         .from('otp_verifications')
//         .update({ verified: true })
//         .eq('id', otpData.id)

//       // Update user as verified
//       const { error: updateError } = await supabase
//         .from('users')
//         .update({ email_verified: true })
//         .eq('email', email)

//       if (updateError) {
//         console.error('Error updating user verification:', updateError)
//       }

//       return { success: true, message: 'Email verified successfully! You can now sign in.' }

//     } catch (error) {
//       console.error('OTP verification error:', error)
//       return { success: false, message: 'An error occurred during verification' }
//     }
//   }

//   const resendOTP = async (email: string) => {
//     try {
//       const otp = generateOTP()
//       const expiresAt = new Date(Date.now() + 10 * 60 * 1000).toISOString()

//       await supabase
//         .from('otp_verifications')
//         .upsert({
//           email,
//           otp_code: otp,
//           expires_at: expiresAt,
//           verified: false
//         })

//       // In a real app, send email here
//       console.log(`New OTP for ${email}: ${otp}`)

//       return { success: true, message: 'New verification code sent to your email' }

//     } catch (error) {
//       console.error('Resend OTP error:', error)
//       return { success: false, message: 'Failed to resend verification code' }
//     }
//   }

//   const signOut = async () => {
//     await supabase.auth.signOut()
//   }

//   return {
//     user,
//     loading,
//     signUp,
//     signIn,
//     signOut,
//     verifyOTP,
//     resendOTP
//   }
// }

// export { AuthContext }

import { useState, useEffect, createContext, useContext } from 'react'
import { supabase } from '../lib/supabase'
import type { User } from '@supabase/supabase-js'

interface AuthContextType {
  user: User | null
  loading: boolean
  signUp: (email: string, password: string, fullName: string) => Promise<{ success: boolean; message: string; needsVerification?: boolean }>
  signIn: (email: string, password: string) => Promise<{ success: boolean; message: string }>
  signOut: () => Promise<void>
  verifyOTP: (email: string, otp: string) => Promise<{ success: boolean; message: string }>
  resendOTP: (email: string) => Promise<{ success: boolean; message: string }>
}

// ✅ Dev mode setup
const devMode = process.env.NODE_ENV === 'development'

const defaultDevUser: User = {
  id: 'dev-user-id',
  email: 'dev@example.com',
  role: 'authenticated',
  app_metadata: { provider: 'email' },
  user_metadata: { full_name: 'Dev User' },
  created_at: new Date().toISOString(),
  aud: 'authenticated',
  confirmed_at: new Date().toISOString(),
  email_confirmed_at: new Date().toISOString(),
  phone: '',
  phone_confirmed_at: null,
  last_sign_in_at: new Date().toISOString(),
  identities: [],
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const useAuthProvider = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (devMode) {
      setUser(defaultDevUser)
      setLoading(false)
      return
    }

    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (_event, session) => {
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const validatePassword = (password: string): { valid: boolean; message: string } => {
    if (password.length < 12) {
      return { valid: false, message: 'Password must be at least 12 characters long' }
    }
    if (!/[A-Z]/.test(password)) {
      return { valid: false, message: 'Password must contain at least 1 uppercase letter' }
    }
    if (!/[0-9]/.test(password)) {
      return { valid: false, message: 'Password must contain at least 1 number' }
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      return { valid: false, message: 'Password must contain at least 1 special character' }
    }
    return { valid: true, message: '' }
  }

  const generateOTP = (): string => {
    return Math.floor(100000 + Math.random() * 900000).toString()
  }

  const signUp = async (email: string, password: string, fullName: string) => {
    if (devMode) {
      return {
        success: true,
        message: 'Signed up (dev mode)',
        needsVerification: false
      }
    }

    try {
      if (!validateEmail(email)) {
        return { success: false, message: 'Please enter a valid email address' }
      }

      const passwordValidation = validatePassword(password)
      if (!passwordValidation.valid) {
        return { success: false, message: passwordValidation.message }
      }

      const { data: existingUser } = await supabase
        .from('users')
        .select('email, email_verified')
        .eq('email', email)
        .single()

      if (existingUser) {
        if (existingUser.email_verified) {
          return { success: false, message: 'Account already exists. Please sign in.' }
        } else {
          const otp = generateOTP()
          const expiresAt = new Date(Date.now() + 10 * 60 * 1000).toISOString()

          await supabase
            .from('otp_verifications')
            .upsert({
              email,
              otp_code: otp,
              expires_at: expiresAt,
              verified: false
            })

          console.log(`OTP for ${email}: ${otp}`)

          return {
            success: true,
            message: 'Verification code sent to your email. Please check your inbox.',
            needsVerification: true
          }
        }
      }

      const { error: authError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName
          }
        }
      })

      if (authError) {
        return { success: false, message: authError.message }
      }

      const otp = generateOTP()
      const expiresAt = new Date(Date.now() + 10 * 60 * 1000).toISOString()

      await supabase
        .from('otp_verifications')
        .insert({
          email,
          otp_code: otp,
          expires_at: expiresAt,
          verified: false
        })

      console.log(`OTP for ${email}: ${otp}`)

      return {
        success: true,
        message: 'Account created! Verification code sent to your email.',
        needsVerification: true
      }

    } catch (error) {
      console.error('Sign up error:', error)
      return { success: false, message: 'An error occurred during sign up' }
    }
  }

  const signIn = async (email: string, password: string) => {
    if (devMode) {
      setUser(defaultDevUser)
      return { success: true, message: 'Signed in (dev mode)' }
    }

    try {
      if (!validateEmail(email)) {
        return { success: false, message: 'Please enter a valid email address' }
      }

      const { error } = await supabase.auth.signInWithPassword({ email, password })

      if (error) {
        const { data: userData } = await supabase
          .from('users')
          .select('email_verified')
          .eq('email', email)
          .single()

        if (userData && !userData.email_verified) {
          return { success: false, message: 'Please verify your email first. Check your inbox for the verification code.' }
        }

        return { success: false, message: 'Invalid email or password' }
      }

      return { success: true, message: 'Successfully signed in!' }

    } catch (error) {
      console.error('Sign in error:', error)
      return { success: false, message: 'An error occurred during sign in' }
    }
  }

  const signOut = async () => {
    if (devMode) {
      setUser(null)
      return
    }

    await supabase.auth.signOut()
  }

  const verifyOTP = async (email: string, otp: string) => {
    if (devMode) {
      return { success: true, message: 'Verified (dev mode)' }
    }

    try {
      const { data: otpData, error: otpError } = await supabase
        .from('otp_verifications')
        .select('*')
        .eq('email', email)
        .eq('otp_code', otp)
        .eq('verified', false)
        .single()

      if (otpError || !otpData) {
        return { success: false, message: 'Invalid or expired verification code' }
      }

      if (new Date() > new Date(otpData.expires_at)) {
        return { success: false, message: 'Verification code has expired. Please request a new one.' }
      }

      await supabase
        .from('otp_verifications')
        .update({ verified: true })
        .eq('id', otpData.id)

      const { error: updateError } = await supabase
        .from('users')
        .update({ email_verified: true })
        .eq('email', email)

      if (updateError) {
        console.error('Error updating user verification:', updateError)
      }

      return { success: true, message: 'Email verified successfully! You can now sign in.' }

    } catch (error) {
      console.error('OTP verification error:', error)
      return { success: false, message: 'An error occurred during verification' }
    }
  }

  const resendOTP = async (email: string) => {
    if (devMode) {
      return { success: true, message: 'OTP resent (dev mode)' }
    }

    try {
      const otp = generateOTP()
      const expiresAt = new Date(Date.now() + 10 * 60 * 1000).toISOString()

      await supabase
        .from('otp_verifications')
        .upsert({
          email,
          otp_code: otp,
          expires_at: expiresAt,
          verified: false
        })

      console.log(`New OTP for ${email}: ${otp}`)

      return { success: true, message: 'New verification code sent to your email' }

    } catch (error) {
      console.error('Resend OTP error:', error)
      return { success: false, message: 'Failed to resend verification code' }
    }
  }

  return {
    user,
    loading,
    signUp,
    signIn,
    signOut,
    verifyOTP,
    resendOTP
  }
}

export { AuthContext }
