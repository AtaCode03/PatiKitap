-- Apply once to the existing Supabase project before deploying the publisher field.
ALTER TABLE patikitap.books
    ADD COLUMN IF NOT EXISTS publisher VARCHAR(160) NOT NULL DEFAULT '';
