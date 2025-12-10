-- =====================================================
-- Supabase User Profile Auto-Creation Trigger
-- =====================================================
-- This script automatically creates user profiles when
-- a new user signs up through Supabase Auth
-- =====================================================

-- Drop existing trigger and function if they exist
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

-- Create function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  -- Insert new user profile
  INSERT INTO public.user_profiles (
    user_id,
    email,
    name,
    preferences,
    is_admin,
    created_at
  )
  VALUES (
    NEW.id,
    NEW.email,
    -- Use name from metadata if provided, otherwise extract from email
    COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
    -- Default preferences structure
    jsonb_build_object(
      'dietary_restrictions', '[]'::jsonb,
      'health_goals', '[]'::jsonb,
      'budget_limit', 0,
      'phone_plan', null
    ),
    false, -- is_admin defaults to false
    now()
  );
  
  RETURN NEW;
END;
$$;

-- Create trigger that fires after user creation
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- =====================================================
-- Row Level Security Policies
-- =====================================================
-- Enable RLS on user_profiles table
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can insert their own profile" ON public.user_profiles;

-- Policy: Users can view their own profile
CREATE POLICY "Users can view their own profile"
ON public.user_profiles
FOR SELECT
USING (auth.uid() = user_id);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update their own profile"
ON public.user_profiles
FOR UPDATE
USING (auth.uid() = user_id);

-- Policy: Service role can do everything (for the trigger)
-- This is already implicitly allowed, but we can be explicit
CREATE POLICY "Service role can manage all profiles"
ON public.user_profiles
FOR ALL
USING (auth.jwt()->>'role' = 'service_role');

-- =====================================================
-- Grant necessary permissions
-- =====================================================
-- Grant usage on the function to authenticated users
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO authenticated;
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO service_role;
