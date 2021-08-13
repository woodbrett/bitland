
create schema bitcoin;

drop table if exists bitcoin.recent_transactions;
create table bitcoin.recent_transactions(bitcoin_block_height int, address varchar, value float8, txid varchar);

drop table if exists bitcoin.relevant_contingency_transaction;
create table bitcoin.relevant_contingency_transaction (bitcoin_block_height int, address varchar, value float8, txid varchar, recorded_bitland_block_height int);

drop table if exists bitcoin.block;
create table bitcoin.block(block_height int, block_hash varchar);

alter table bitland.claim add column status varchar;
alter table bitland.claim add column claim_end_block int;
alter table bitland.claim drop column leading_claim;
alter table bitland.claim drop column invalidated_claim;



RERUN VIEWS