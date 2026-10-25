-- Favorite status and saved price tracking
-- Apply once in the Supabase SQL editor before deploying this version.
alter table patikitap.favorites
  add column saved_price integer,
  add column snapshot_title varchar(160),
  add column snapshot_author varchar(120),
  add column snapshot_kind varchar(20),
  add column snapshot_status varchar(20),
  add column saved_at timestamptz not null default now();

-- Preserve the current asking price as the baseline for existing favorites.
update patikitap.favorites f
set saved_price = b.price,
    snapshot_title = b.title,
    snapshot_author = b.author,
    snapshot_kind = b.kind,
    snapshot_status = b.status
from patikitap.books b
where b.id = f.book_id;

-- Favorite rows retain a listing snapshot after permanent book deletion.
alter table patikitap.favorites drop constraint favorites_book_id_fkey;

-- The application snapshots listing details immediately before a permanent delete.
grant update on patikitap.favorites to patikitap_runtime;
create policy runtime_update on patikitap.favorites for update to patikitap_runtime using (true) with check (true);
