
CREATE TABLE patikitap.profiles (
	id UUID NOT NULL,
	display_name VARCHAR(80) NOT NULL,
	city VARCHAR(100) NOT NULL,
	bio VARCHAR(500) NOT NULL,
	disabled BOOLEAN NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id)
)

;

alter table patikitap.books add column owner_id uuid references patikitap.profiles(id);

alter table patikitap.books add column description text not null default '';

alter table patikitap.books add column isbn varchar(13) not null default '';

alter table patikitap.books add column image_url varchar(1000) not null default '';

alter table patikitap.books add column status varchar(20) not null default 'active' check(status in ('active','reserved','completed','archived','hidden'));

alter table patikitap.books add column is_demo boolean not null default true;

alter table patikitap.books alter column is_demo set default false;

alter table patikitap.books add column created_at timestamptz not null default now();


CREATE TABLE patikitap.audit_logs (
	id SERIAL NOT NULL,
	actor_id UUID NOT NULL,
	action VARCHAR(80) NOT NULL,
	entity_type VARCHAR(40) NOT NULL,
	entity_id VARCHAR(80) NOT NULL,
	detail VARCHAR(1000) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(actor_id) REFERENCES patikitap.profiles (id)
)

;


CREATE TABLE patikitap.favorites (
	user_id UUID NOT NULL,
	book_id INTEGER NOT NULL,
	PRIMARY KEY (user_id, book_id),
	FOREIGN KEY(user_id) REFERENCES patikitap.profiles (id),
	FOREIGN KEY(book_id) REFERENCES patikitap.books (id)
)

;


CREATE TABLE patikitap.requests (
	id SERIAL NOT NULL,
	book_id INTEGER NOT NULL,
	requester_id UUID NOT NULL,
	offered_book_id INTEGER,
	message VARCHAR(1000) NOT NULL,
	status VARCHAR(20) NOT NULL,
	delivery_method VARCHAR(20) NOT NULL,
	shipping_payer VARCHAR(20) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT request_status CHECK (status in ('pending','accepted','rejected','cancelled')),
	FOREIGN KEY(book_id) REFERENCES patikitap.books (id),
	FOREIGN KEY(requester_id) REFERENCES patikitap.profiles (id),
	FOREIGN KEY(offered_book_id) REFERENCES patikitap.books (id)
)

;


CREATE TABLE patikitap.transactions (
	id SERIAL NOT NULL,
	request_id INTEGER NOT NULL,
	book_id INTEGER NOT NULL,
	offered_book_id INTEGER,
	owner_id UUID NOT NULL,
	requester_id UUID NOT NULL,
	kind VARCHAR(20) NOT NULL,
	status VARCHAR(20) NOT NULL,
	price_cents INTEGER NOT NULL,
	fee_cents INTEGER NOT NULL,
	support_cents INTEGER NOT NULL,
	support_rate_bps INTEGER NOT NULL,
	owner_confirmed BOOLEAN NOT NULL,
	requester_confirmed BOOLEAN NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	completed_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	CONSTRAINT transaction_status CHECK (status in ('accepted','in_delivery','completed','cancelled','disputed')),
	CONSTRAINT transaction_amounts CHECK (price_cents >= 0 and support_cents >= 0 and fee_cents >= 0 and support_cents + fee_cents <= price_cents),
	UNIQUE (request_id),
	FOREIGN KEY(request_id) REFERENCES patikitap.requests (id),
	FOREIGN KEY(book_id) REFERENCES patikitap.books (id),
	FOREIGN KEY(offered_book_id) REFERENCES patikitap.books (id),
	FOREIGN KEY(owner_id) REFERENCES patikitap.profiles (id),
	FOREIGN KEY(requester_id) REFERENCES patikitap.profiles (id)
)

;


CREATE TABLE patikitap.complaints (
	id SERIAL NOT NULL,
	reporter_id UUID NOT NULL,
	book_id INTEGER,
	transaction_id INTEGER,
	reason VARCHAR(1000) NOT NULL,
	status VARCHAR(20) NOT NULL,
	resolution VARCHAR(1000) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(reporter_id) REFERENCES patikitap.profiles (id),
	FOREIGN KEY(book_id) REFERENCES patikitap.books (id),
	FOREIGN KEY(transaction_id) REFERENCES patikitap.transactions (id)
)

;


CREATE TABLE patikitap.deliveries (
	id SERIAL NOT NULL,
	transaction_id INTEGER NOT NULL,
	sender_id UUID NOT NULL,
	recipient_id UUID NOT NULL,
	method VARCHAR(20) NOT NULL,
	shipping_payer VARCHAR(20) NOT NULL,
	cost_cents INTEGER NOT NULL,
	tracking_number VARCHAR(100) NOT NULL,
	carrier VARCHAR(80) NOT NULL,
	meeting_point VARCHAR(200) NOT NULL,
	status VARCHAR(20) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (transaction_id, sender_id),
	CONSTRAINT shipping_cost CHECK (cost_cents >= 0),
	FOREIGN KEY(transaction_id) REFERENCES patikitap.transactions (id),
	FOREIGN KEY(sender_id) REFERENCES patikitap.profiles (id),
	FOREIGN KEY(recipient_id) REFERENCES patikitap.profiles (id)
)

;


CREATE TABLE patikitap.notifications (
	id SERIAL NOT NULL,
	user_id UUID NOT NULL,
	message VARCHAR(500) NOT NULL,
	transaction_id INTEGER,
	read_at TIMESTAMP WITH TIME ZONE,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES patikitap.profiles (id),
	FOREIGN KEY(transaction_id) REFERENCES patikitap.transactions (id)
)

;


CREATE TABLE patikitap.support_records (
	id SERIAL NOT NULL,
	transaction_id INTEGER NOT NULL,
	amount_cents INTEGER NOT NULL,
	mode VARCHAR(20) NOT NULL,
	status VARCHAR(20) NOT NULL,
	organization VARCHAR(160) NOT NULL,
	document_url VARCHAR(1000) NOT NULL,
	note VARCHAR(1000) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT support_simulation_only CHECK (mode = 'simulation'),
	CONSTRAINT support_positive CHECK (amount_cents > 0),
	UNIQUE (transaction_id),
	FOREIGN KEY(transaction_id) REFERENCES patikitap.transactions (id)
)

;

CREATE INDEX ix_app_audit_logs_actor_id ON patikitap.audit_logs (actor_id);

CREATE INDEX ix_app_books_owner_id ON patikitap.books (owner_id);

CREATE INDEX ix_app_books_status ON patikitap.books (status);

CREATE INDEX ix_app_favorites_book_id ON patikitap.favorites (book_id);

CREATE INDEX ix_app_requests_requester_id ON patikitap.requests (requester_id);

CREATE INDEX ix_app_requests_offered_book_id ON patikitap.requests (offered_book_id);

CREATE INDEX ix_app_requests_book_id ON patikitap.requests (book_id);

CREATE UNIQUE INDEX one_pending_request ON patikitap.requests (book_id, requester_id) WHERE status='pending';

CREATE INDEX ix_app_requests_status ON patikitap.requests (status);

CREATE INDEX ix_app_transactions_status ON patikitap.transactions (status);

CREATE INDEX ix_app_transactions_book_id ON patikitap.transactions (book_id);

CREATE INDEX ix_app_transactions_requester_id ON patikitap.transactions (requester_id);

CREATE INDEX ix_app_transactions_owner_id ON patikitap.transactions (owner_id);

CREATE INDEX ix_app_complaints_reporter_id ON patikitap.complaints (reporter_id);

CREATE INDEX ix_app_complaints_status ON patikitap.complaints (status);

CREATE INDEX ix_app_deliveries_transaction_id ON patikitap.deliveries (transaction_id);

CREATE INDEX ix_app_notifications_user_id ON patikitap.notifications (user_id);

alter table patikitap.profiles enable row level security;

revoke all on table patikitap.profiles from public, anon, authenticated;

alter table patikitap.audit_logs enable row level security;

revoke all on table patikitap.audit_logs from public, anon, authenticated;

alter table patikitap.books enable row level security;

revoke all on table patikitap.books from public, anon, authenticated;

alter table patikitap.favorites enable row level security;

revoke all on table patikitap.favorites from public, anon, authenticated;

alter table patikitap.requests enable row level security;

revoke all on table patikitap.requests from public, anon, authenticated;

alter table patikitap.transactions enable row level security;

revoke all on table patikitap.transactions from public, anon, authenticated;

alter table patikitap.complaints enable row level security;

revoke all on table patikitap.complaints from public, anon, authenticated;

alter table patikitap.deliveries enable row level security;

revoke all on table patikitap.deliveries from public, anon, authenticated;

alter table patikitap.notifications enable row level security;

revoke all on table patikitap.notifications from public, anon, authenticated;

alter table patikitap.support_records enable row level security;

revoke all on table patikitap.support_records from public, anon, authenticated;

alter table patikitap.profiles add constraint profiles_auth_user_fk foreign key(id) references auth.users(id);

revoke all on all sequences in schema patikitap from public, anon, authenticated;

insert into storage.buckets (id,name,public,file_size_limit,allowed_mime_types) values ('book-media','book-media',false,5242880,array['image/jpeg']) on conflict(id) do nothing;

create policy book_media_upload on storage.objects for insert to authenticated with check (bucket_id='book-media' and (storage.foldername(name))[1]=(select auth.uid())::text);

create policy book_media_delete on storage.objects for delete to authenticated using (bucket_id='book-media' and (storage.foldername(name))[1]=(select auth.uid())::text);

create policy book_media_member_read on storage.objects for select to authenticated using (bucket_id='book-media');
-- Defense in depth: backend validation is mirrored in the database.
alter table patikitap.requests add constraint request_delivery_method check(delivery_method in ('campus','hand','cargo'));
alter table patikitap.requests add constraint request_shipping_payer check(shipping_payer in ('sender','recipient'));
alter table patikitap.requests add constraint request_distinct_books check(offered_book_id is null or offered_book_id <> book_id);
alter table patikitap.transactions add constraint transaction_participants check(owner_id <> requester_id);
alter table patikitap.transactions add constraint transaction_kind check(kind in ('Bağış','Takas','Satış'));
alter table patikitap.transactions add constraint transaction_support_rate check(support_rate_bps between 0 and 10000);
alter table patikitap.deliveries add constraint delivery_state check(status in ('pending','dispatched','delivered','cancelled'));
alter table patikitap.deliveries add constraint delivery_method check(method in ('campus','hand','cargo'));
alter table patikitap.deliveries add constraint delivery_shipping_payer check(shipping_payer in ('sender','recipient'));
alter table patikitap.deliveries add constraint delivery_participants check(sender_id <> recipient_id);
alter table patikitap.complaints add constraint complaint_target check((book_id is null) <> (transaction_id is null));
alter table patikitap.complaints add constraint complaint_state check(status in ('open','resolved','dismissed'));
alter table patikitap.support_records add constraint support_state check(status in ('recorded','documented'));
