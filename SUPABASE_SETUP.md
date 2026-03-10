# Supabase Vector Store Setup Guide

This guide will help you set up Supabase with pgvector for persistent document storage.

## Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Fill in:
   - **Name**: `ai-chatbot-vectorstore` (or any name)
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose closest to your users
4. Click "Create new project" (takes ~2 minutes)

## Step 2: Enable pgvector Extension

1. In your Supabase project, go to **Database** → **Extensions**
2. Search for `vector`
3. Enable the **pgvector** extension

## Step 3: Create the Documents Table

1. Go to **SQL Editor** in the left sidebar
2. Click **New Query**
3. Paste this SQL and click **Run**:

```sql
-- Enable the pgvector extension
create extension if not exists vector;

-- Create the documents table for vector storage
create table documents (
  id bigserial primary key,
  content text,
  metadata jsonb,
  embedding vector(1024)  -- Cohere embed-english-light-v3.0 uses 1024 dimensions
);

-- Create an index for faster similarity search
create index on documents using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- Create a function for similarity search
create or replace function match_documents (
  query_embedding vector(1024),
  match_count int default 5,
  filter jsonb default '{}'::jsonb
) returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where metadata @> filter
  order by documents.embedding <=> query_embedding
  limit match_count;
end;
$$;
```

## Step 4: Get Your Supabase Credentials

1. Go to **Project Settings** (gear icon in sidebar)
2. Go to **API** section
3. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Service Role Key** (anon public key won't work for vector operations)

## Step 5: Get Cohere API Key (Free)

1. Go to [https://cohere.com](https://cohere.com)
2. Sign up for free account
3. Go to **Dashboard** → **API Keys**
4. Copy your **Production API Key**
5. Free tier: 100 API calls/minute (plenty for this app)

## Step 6: Add Environment Variables to Vercel

Run these commands to add the environment variables to your Vercel backend project:

```powershell
# Set Supabase URL
$headers = @{ "Authorization" = "Bearer YOUR_VERCEL_TOKEN"; "Content-Type" = "application/json" }
$body = @{ key = "SUPABASE_URL"; value = "YOUR_SUPABASE_URL"; target = @("production", "preview"); type = "plain" } | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.vercel.com/v10/projects/prj_evBcJyz6UcgDb5kUXfW6XqctExNw/env?teamId=team_haIfJx3s7VLsj1SVCzjzYqo9" -Method Post -Headers $headers -Body $body

# Set Supabase Service Key (sensitive)
$body = @{ key = "SUPABASE_SERVICE_KEY"; value = "YOUR_SUPABASE_SERVICE_KEY"; target = @("production", "preview"); type = "sensitive" } | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.vercel.com/v10/projects/prj_evBcJyz6UcgDb5kUXfW6XqctExNw/env?teamId=team_haIfJx3s7VLsj1SVCzjzYqo9" -Method Post -Headers $headers -Body $body

# Set Cohere API Key (sensitive)
$body = @{ key = "COHERE_API_KEY"; value = "YOUR_COHERE_API_KEY"; target = @("production", "preview"); type = "sensitive" } | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.vercel.com/v10/projects/prj_evBcJyz6UcgDb5kUXfW6XqctExNw/env?teamId=team_haIfJx3s7VLsj1SVCzjzYqo9" -Method Post -Headers $headers -Body $body
```

Or use the Vercel dashboard:
1. Go to your project on Vercel
2. Settings → Environment Variables
3. Add these three variables:
   - `SUPABASE_URL` (plain text)
   - `SUPABASE_SERVICE_KEY` (sensitive)
   - `COHERE_API_KEY` (sensitive)

## Step 7: Redeploy Backend

After adding environment variables, trigger a new deployment:
```bash
git add .
git commit -m "Add Supabase vector store with Cohere embeddings"
git push origin main
```

## Verification

After deployment, check the health endpoint:
```
https://ai-chatbot-backend-iota.vercel.app/api/health
```

Should return:
```json
{
  "status": "healthy",
  "vector_store_initialized": true,
  "embeddings_initialized": true,
  "supabase_connected": true
}
```

## How It Works

1. **Upload PDF**: Text is extracted, chunked, embedded with Cohere, and stored in Supabase
2. **Ask Question**: Question is embedded, vector similarity search finds relevant chunks, Groq LLM generates answer
3. **Persistent Storage**: Documents persist across serverless cold starts
4. **Semantic Search**: True vector embeddings (not just keyword matching)

## Cost

- **Supabase**: Free tier (500MB database, 2GB bandwidth/month)
- **Cohere**: Free tier (100 API calls/minute)
- **Groq**: Free tier (you already have this)

All free for development and small-scale production use!
