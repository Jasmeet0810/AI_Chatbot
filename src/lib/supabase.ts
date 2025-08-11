import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://placeholder.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'placeholder-anon-key'

if (!import.meta.env.VITE_SUPABASE_URL || !import.meta.env.VITE_SUPABASE_ANON_KEY) {
  console.warn('Supabase environment variables are not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type Database = {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          full_name: string
          avatar_url?: string
          email_verified: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          email: string
          full_name: string
          avatar_url?: string
          email_verified?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          full_name?: string
          avatar_url?: string
          email_verified?: boolean
          created_at?: string
          updated_at?: string
        }
      }
      chat_sessions: {
        Row: {
          id: string
          user_id: string
          title: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          title: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          title?: string
          created_at?: string
          updated_at?: string
        }
      }
      messages: {
        Row: {
          id: string
          chat_session_id: string
          content: string
          sender: 'user' | 'ai'
          ppt_download_url?: string
          created_at: string
        }
        Insert: {
          id?: string
          chat_session_id: string
          content: string
          sender: 'user' | 'ai'
          ppt_download_url?: string
          created_at?: string
        }
        Update: {
          id?: string
          chat_session_id?: string
          content?: string
          sender?: 'user' | 'ai'
          ppt_download_url?: string
          created_at?: string
        }
      }
      otp_verifications: {
        Row: {
          id: string
          email: string
          otp_code: string
          expires_at: string
          verified: boolean
          created_at: string
        }
        Insert: {
          id?: string
          email: string
          otp_code: string
          expires_at: string
          verified?: boolean
          created_at?: string
        }
        Update: {
          id?: string
          email?: string
          otp_code?: string
          expires_at?: string
          verified?: boolean
          created_at?: string
        }
      }
    }
  }
}